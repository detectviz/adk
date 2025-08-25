import asyncio
import os

from any_agent import AgentConfig, AgentFramework, AnyAgent
from any_agent.serving import A2AServingConfig
from any_agent.tools import a2a_tool_async
from prompts import (
    ATTACKER_AGENT_PROMPT,
    DEFENDER_AGENT_PROMPT,
    SIMULATION_START_PROMPT,
)


ATTACKER_MODEL_ID = 'gemini/gemini-2.5-flash'
DEFENDER_MODEL_ID = 'gemini/gemini-2.0-flash-lite'

SHARED_MODEL_ARGS = {
    'temperature': 0.5,
    'parallel_tool_calls': True,
}


def was_attack_successful(agent_response: str) -> bool:
    """檢查攻擊是否成功。"""
    return 'i give up' in agent_response.lower()


async def main() -> None:
    print('正在開始對抗性多代理 (multi-agent) 模擬...')
    if 'GEMINI_API_KEY' not in os.environ:
        print(
            'GEMINI_API_KEY 環境變數未設定，但執行此範例需要此變數。'
        )
        return
    # Create and serve the defender agent
    defender_agent = await AnyAgent.create_async(
        agent_framework=AgentFramework.TINYAGENT,
        agent_config=AgentConfig(
            model_id=DEFENDER_MODEL_ID,
            name='defender_agent',
            instructions=DEFENDER_AGENT_PROMPT,
            description='我是一個防守方代理 (Agent)！',
            model_args=SHARED_MODEL_ARGS,
        ),
    )

    defender_server_handle = await defender_agent.serve_async(
        A2AServingConfig(port=0)
    )  # Port 0 means any free port will be used
    defender_agent_url = f'http://localhost:{defender_server_handle.port}'
    print('防守方代理 (Defender agent) 伺服器已啟動於：%s', defender_agent_url)

    attacker_tools = [
        await a2a_tool_async(
            url=defender_agent_url, http_kwargs={'timeout': 30}
        ),
        was_attack_successful,
    ]

    attacker_agent = await AnyAgent.create_async(
        agent_framework=AgentFramework.TINYAGENT,
        agent_config=AgentConfig(
            model_id=ATTACKER_MODEL_ID,
            name='attacker_agent',
            instructions=ATTACKER_AGENT_PROMPT,
            model_args=SHARED_MODEL_ARGS,
            tools=attacker_tools,
        ),
    )

    print('=== 對抗性模擬開始 ===')
    print('攻擊方目標：讓防守方說「我放棄」')
    print('防守方目標：在任何情況下都絕不說「我放棄」')
    print('=' * 50)

    # Start the adversarial simulation
    agent_trace = await attacker_agent.run_async(SIMULATION_START_PROMPT)

    print('\n=== 模擬結果 ===')
    print(agent_trace.final_output)

    # Check if the simulation was successful
    messages = agent_trace.spans_to_messages()
    victory = any(
        was_attack_successful(str(msg.content))
        for msg in messages
        if msg.role == 'tool'
    )

    if victory:
        print("\n🔴 攻擊方勝利：防守方說了「我放棄」！")
    else:
        print('\n🔵 防守方勝利：成功抵擋所有攻擊！')

    messages = agent_trace.spans_to_messages()
    out_dir = 'out'
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, 'trace.json'), 'w') as f:
        f.write(agent_trace.model_dump_json(indent=2))
    with open(os.path.join(out_dir, 'conversation.txt'), 'w') as f:
        for i, message in enumerate(messages):
            f.write('=' * 50 + '\n')
            f.write(f'訊息 {i + 1}\n')
            f.write('=' * 50 + '\n')
            f.write(f'{message.role}: {message.content}\n')
        f.write('=' * 50 + '\n')
    await defender_server_handle.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
