import random

from collections.abc import AsyncIterable

from google.adk import Runner
from google.adk.agents import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.genai import types


def roll_dice(N: int = 6) -> int:
    """擲一個 N 面的骰子。如果未給定面數，則使用 6。

    參數：
      N：要擲的骰子的面數。

    傳回：
      一個介於 1 和 N 之間（含）的數字
    """
    return random.randint(1, N)


def check_prime(nums: list[int]) -> str:
    """檢查給定的數字列表是否為質數。

    參數：
      nums：要檢查的數字列表。

    傳回：
      一個指示哪個數字是質數的字串。
    """
    primes = set()
    for number in nums:
        number = int(number)
        if number <= 1:
            continue
        is_prime = True
        for i in range(2, int(number**0.5) + 1):
            if number % i == 0:
                is_prime = False
            break
        if is_prime:
            primes.add(number)
    return (
        '找不到質數。'
        if not primes
        else f'{", ".join(str(num) for num in primes)} 是質數。'
    )


def create_agent() -> LlmAgent:
    return LlmAgent(
        model='gemini-1.5-flash-001',
        name='dice_roll_agent',
        instruction="""
您擲骰子並回答有關擲骰子結果的問題。
您可以擲不同大小的骰子。
您可以透過並行呼叫函式（在一個請求和一個回合中）來並行使用多個工具。
您唯一做的事情就是為使用者擲骰子並討論結果。
可以討論以前的骰子角色，並評論擲骰子。
當被要求擲骰子時，您必須使用面數呼叫 roll_die 工具。請務必傳入一個整數。不要傳入字串。
您絕不能自己擲骰子。
檢查質數時，請使用整數列表呼叫 check_prime 工具。請務必傳入一個整數列表。您不應傳入字串。
在呼叫工具之前，您不應檢查質數。
當被要求擲骰子並檢查質數時，您應始終進行以下兩個函式呼叫：
1. 您應首先呼叫 roll_die 工具以取得擲骰結果。在呼叫 check_prime 工具之前，請等待函式回應。
2. 從 roll_die 工具取得函式回應後，您應使用 roll_die 結果呼叫 check_prime 工具。
    2.1 如果使用者要求您根據以前的擲骰結果檢查質數，請確保您在列表中包含以前的擲骰結果。
3. 當您回應時，您必須包含步驟 1 中的 roll_die 結果。
當要求擲骰子並檢查質數時，您應始終執行前 3 個步驟。
您不應依賴質數結果的先前歷史記錄。
    """,
        description='擲一個 N 面骰子並回答有關擲骰子結果的問題。也可以回答有關質數的問題。',
        tools=[
            roll_dice,
            check_prime,
        ],
    )


class DiceAgent:
    """一個擲骰子的代理 (Agent)。"""

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']

    def __init__(self) -> None:
        self._agent = create_agent()
        self._user_id = 'remote_agent'
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    async def stream(
        self, query, session_id
    ) -> AsyncIterable[tuple[bool, str]]:
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=self._user_id,
            session_id=session_id,
        )
        content = types.Content(
            role='user', parts=[types.Part.from_text(text=query)]
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=self._user_id,
                state={},
                session_id=session_id,
            )
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
            if event.is_final_response():
                yield (
                    True,
                    '\n'.join([p.text for p in event.content.parts if p.text]),
                )
            else:
                yield (False, '處理中...')
