import datetime, uuid
from zoneinfo import ZoneInfo
from .sub_agents.prompt import image_generation_prompt_agent 
from .sub_agents.image import image_generation_agent 
from .sub_agents.scoring import scoring_images_prompt 
from .checker_agent import checker_agent_instance
from google.adk.agents import SequentialAgent, LoopAgent
from google.adk.agents.callback_context import CallbackContext


def set_session(callback_context: CallbackContext):
    """
    在回呼上下文 (callback context) 的狀態中設定一個唯一的 ID 和時間戳。
    此函式在 main_loop_agent 執行之前被呼叫。
    """

    callback_context.state["unique_id"] = str(uuid.uuid4())
    callback_context.state["timestamp"] = datetime.datetime.now(
        ZoneInfo("UTC")
    ).isoformat()


# 此代理負責根據輸入文字生成與評分圖像。
# 它使用一個循序的過程來：
# 1. 從輸入文字建立一個圖像生成提示
# 2. 使用該提示生成圖像
# 3. 對生成的圖像進行評分
# 此過程將持續進行，直到：
# - 圖像分數達到品質門檻
# - 達到最大迭代次數

image_generation_scoring_agent = SequentialAgent(
    name="image_generation_scoring_agent",

    description=(
        """
        分析輸入文字並建立圖像生成提示，使用 imagen3 生成相關圖像並對圖像進行評分。"
        1. 呼叫 image_generation_prompt_agent 代理以生成用於生成圖像的提示
        2. 呼叫 image_generation_agent 代理以生成圖像
        3. 呼叫 scoring_images_prompt 代理以對圖像進行評分
            """
    ),
    sub_agents=[image_generation_prompt_agent, image_generation_agent, scoring_images_prompt],
)


# --- 5. 定義循環代理 (Loop Agent) ---
# 循環代理 (LoopAgent) 將按照列出的順序重複執行其子代理。
# 它將持續循環，直到其中一個子代理（特別是 checker_agent 的工具）
# 設定 tool_context.actions.escalate = True。
image_scoring = LoopAgent(
    name="image_scoring",
    description="重複執行一個循序的過程並檢查終止條件。",
    sub_agents=[
        image_generation_scoring_agent,  # 首先，執行您的循序過程 [1]
        checker_agent_instance,  # 其次，檢查條件並可能停止循環 [1]
    ],
    before_agent_callback=set_session,
)
root_agent = image_scoring
