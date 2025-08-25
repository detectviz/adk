# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import AsyncGenerator
from typing_extensions import override

from google.adk.agents import LlmAgent, BaseAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from pydantic import BaseModel, Field

# --- 常數 (Constants) ---
APP_NAME = "story_app"
USER_ID = "12345"
SESSION_ID = "123344"
GEMINI_2_FLASH = "gemini-2.0-flash"

# --- 設定日誌 (Configure Logging) ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- 自訂協調器代理 (Custom Orchestrator Agent) ---
# --8<-- [start:init]
class StoryFlowAgent(BaseAgent):
    """
    用於故事生成和優化工作流程的自訂代理。

    此代理協調一系列大型語言模型（LLM）代理，以生成故事、評論、
    修訂、檢查文法和語氣，並在語氣為負面時可能重新生成故事。
    """

    # --- Pydantic 的欄位宣告 (Field Declarations for Pydantic) ---
    # 將初始化期間傳入的代理宣告為帶有類型提示的類別屬性
    story_generator: LlmAgent
    critic: LlmAgent
    reviser: LlmAgent
    grammar_check: LlmAgent
    tone_check: LlmAgent

    loop_agent: LoopAgent
    sequential_agent: SequentialAgent

    # model_config 允許在需要時設定 Pydantic 組態，例如 arbitrary_types_allowed
    model_config = {"arbitrary_types_allowed": True}

    def __init__(
        self,
        name: str,
        story_generator: LlmAgent,
        critic: LlmAgent,
        reviser: LlmAgent,
        grammar_check: LlmAgent,
        tone_check: LlmAgent,
    ):
        """
        初始化 StoryFlowAgent。

        Args:
            name: 代理的名稱。
            story_generator: 用於生成初始故事的 LlmAgent。
            critic: 用於評論故事的 LlmAgent。
            reviser: 用於根據評論修訂故事的 LlmAgent。
            grammar_check: 用於檢查文法的 LlmAgent。
            tone_check: 用於分析語氣的 LlmAgent。
        """
        # 在呼叫 super().__init__ 之前建立內部代理
        loop_agent = LoopAgent(
            name="CriticReviserLoop", sub_agents=[critic, reviser], max_iterations=2
        )
        sequential_agent = SequentialAgent(
            name="PostProcessing", sub_agents=[grammar_check, tone_check]
        )

        # 為框架定義 sub_agents 列表
        sub_agents_list = [
            story_generator,
            loop_agent,
            sequential_agent,
        ]

        # Pydantic 將根據類別註釋進行驗證和指派。
        super().__init__(
            name=name,
            story_generator=story_generator,
            critic=critic,
            reviser=reviser,
            grammar_check=grammar_check,
            tone_check=tone_check,
            loop_agent=loop_agent,
            sequential_agent=sequential_agent,
            sub_agents=sub_agents_list, # 直接傳遞 sub_agents 列表
        )
# --8<-- [end:init]

    # --8<-- [start:executionlogic]
    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        實作故事工作流程的自訂協調邏輯。
        使用 Pydantic 指派的實例屬性（例如 self.story_generator）。
        """
        logger.info(f"[{self.name}] 開始故事生成工作流程。")

        # 1. 初始故事生成
        logger.info(f"[{self.name}] 執行 StoryGenerator...")
        async for event in self.story_generator.run_async(ctx):
            logger.info(f"[{self.name}] 來自 StoryGenerator 的事件：{event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        # 在繼續之前檢查故事是否已生成
        if "current_story" not in ctx.session.state or not ctx.session.state["current_story"]:
             logger.error(f"[{self.name}] 未能生成初始故事。中止工作流程。")
             return # 如果初始故事生成失敗，則停止處理

        logger.info(f"[{self.name}] 生成器之後的故事狀態：{ctx.session.state.get('current_story')}")


        # 2. 評論者-修訂者迴圈
        logger.info(f"[{self.name}] 執行 CriticReviserLoop...")
        # 使用初始化期間指派的 loop_agent 實例屬性
        async for event in self.loop_agent.run_async(ctx):
            logger.info(f"[{self.name}] 來自 CriticReviserLoop 的事件：{event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        logger.info(f"[{self.name}] 迴圈之後的故事狀態：{ctx.session.state.get('current_story')}")

        # 3. 循序後處理（文法和語氣檢查）
        logger.info(f"[{self.name}] 執行 PostProcessing...")
        # 使用初始化期間指派的 sequential_agent 實例屬性
        async for event in self.sequential_agent.run_async(ctx):
            logger.info(f"[{self.name}] 來自 PostProcessing 的事件：{event.model_dump_json(indent=2, exclude_none=True)}")
            yield event

        # 4. 基於語氣的條件邏輯
        tone_check_result = ctx.session.state.get("tone_check_result")
        logger.info(f"[{self.name}] 語氣檢查結果：{tone_check_result}")

        if tone_check_result == "negative":
            logger.info(f"[{self.name}] 語氣為負面。重新生成故事...")
            async for event in self.story_generator.run_async(ctx):
                logger.info(f"[{self.name}] 來自 StoryGenerator (重新生成) 的事件：{event.model_dump_json(indent=2, exclude_none=True)}")
                yield event
        else:
            logger.info(f"[{self.name}] 語氣不是負面。保留目前的故事。")
            pass

        logger.info(f"[{self.name}] 工作流程完成。")
    # --8<-- [end:executionlogic]

# --8<-- [start:llmagents]
# --- 定義各個 LLM 代理 ---
story_generator = LlmAgent(
    name="StoryGenerator",
    model=GEMINI_2_FLASH,
    instruction="""您是一位故事作家。請就以下主題寫一個短篇故事（約 100 字）：{topic}""",
    input_schema=None,
    output_key="current_story",  # 用於在會話狀態中儲存輸出的鍵
)

critic = LlmAgent(
    name="Critic",
    model=GEMINI_2_FLASH,
    instruction="""您是一位故事評論家。請評論所提供的故事：{{current_story}}。提供 1-2 句關於如何改進的建設性批評。專注於情節或角色。""",
    input_schema=None,
    output_key="criticism",  # 用於在會話狀態中儲存批評的鍵
)

reviser = LlmAgent(
    name="Reviser",
    model=GEMINI_2_FLASH,
    instruction="""您是一位故事修訂者。請根據 {{criticism}} 中的批評修訂所提供的故事：{{current_story}}。僅輸出修訂後的故事。""",
    input_schema=None,
    output_key="current_story",  # 覆蓋原始故事
)

grammar_check = LlmAgent(
    name="GrammarCheck",
    model=GEMINI_2_FLASH,
    instruction="""您是一位文法檢查員。請檢查所提供故事的文法：{current_story}。僅以列表形式輸出建議的修正，如果沒有錯誤，則輸出「文法正確！」。""",
    input_schema=None,
    output_key="grammar_suggestions",
)

tone_check = LlmAgent(
    name="ToneCheck",
    model=GEMINI_2_FLASH,
    instruction="""您是一位語氣分析師。請分析所提供故事的語氣：{current_story}。如果語氣普遍為正面，僅輸出「positive」；如果語氣普遍為負面，則輸出「negative」；否則輸出「neutral」。""",
    input_schema=None,
    output_key="tone_check_result", # 此代理的輸出決定了條件流程
)
# --8<-- [end:llmagents]

# --8<-- [start:story_flow_agent]
# --- 建立自訂代理實例 ---
story_flow_agent = StoryFlowAgent(
    name="StoryFlowAgent",
    story_generator=story_generator,
    critic=critic,
    reviser=reviser,
    grammar_check=grammar_check,
    tone_check=tone_check,
)

INITIAL_STATE = {"topic": "一隻勇敢的小貓探索鬼屋"}

# --- 設定執行器和會話 ---
async def setup_session_and_runner():
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state=INITIAL_STATE)
    logger.info(f"初始會話狀態：{session.state}")
    runner = Runner(
        agent=story_flow_agent, # 傳遞自訂協調器代理
        app_name=APP_NAME,
        session_service=session_service
    )
    return session_service, runner

# --- 與代理互動的函式 ---
async def call_agent_async(user_input_topic: str):
    """
    將新主題傳送給代理（如果需要，會覆蓋初始主題）並執行工作流程。
    """

    session_service, runner = await setup_session_and_runner()

    current_session = await session_service.get_session(app_name=APP_NAME, 
                                                  user_id=USER_ID, 
                                                  session_id=SESSION_ID)
    if not current_session:
        logger.error("找不到會話！")
        return

    current_session.state["topic"] = user_input_topic
    logger.info(f"已將會話狀態主題更新為：{user_input_topic}")

    content = types.Content(role='user', parts=[types.Part(text=f"生成一個關於以下主題的故事：{user_input_topic}")])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = "未擷取到最終回應。"
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"來自 [{event.author}] 的潛在最終回應：{event.content.parts[0].text}")
            final_response = event.content.parts[0].text

    print("\n--- 代理互動結果 ---")
    print("代理最終回應：", final_response)

    final_session = await session_service.get_session(app_name=APP_NAME, 
                                                user_id=USER_ID, 
                                                session_id=SESSION_ID)
    print("最終會話狀態：")
    import json
    print(json.dumps(final_session.state, indent=2))
    print("-------------------------------\n")

# --- 執行代理 ---
# 注意：在 Colab 中，您可以直接在頂層使用 'await'。
# 如果將此程式碼作為獨立的 Python 腳本執行，您需要使用 asyncio.run() 或管理事件迴圈。
# await call_agent_async("一個孤獨的機器人在垃圾場找到朋友")
# --8<-- [end:story_flow_agent]
