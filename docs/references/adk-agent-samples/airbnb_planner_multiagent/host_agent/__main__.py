import asyncio
import traceback  # Import the traceback module

from collections.abc import AsyncIterator
from pprint import pformat

import gradio as gr

from google.adk.events import Event
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from routing_agent import (
    root_agent as routing_agent,
)


APP_NAME = 'routing_app'
USER_ID = 'default_user'
SESSION_ID = 'default_session'

SESSION_SERVICE = InMemorySessionService()
ROUTING_AGENT_RUNNER = Runner(
    agent=routing_agent,
    app_name=APP_NAME,
    session_service=SESSION_SERVICE,
)


async def get_response_from_agent(
    message: str,
    history: list[gr.ChatMessage],
) -> AsyncIterator[gr.ChatMessage]:
    """從主機代理 (host agent) 取得回應。"""
    try:
        event_iterator: AsyncIterator[Event] = ROUTING_AGENT_RUNNER.run_async(
            user_id=USER_ID,
            session_id=SESSION_ID,
            new_message=types.Content(
                role='user', parts=[types.Part(text=message)]
            ),
        )

        async for event in event_iterator:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        formatted_call = f'```python\n{pformat(part.function_call.model_dump(exclude_none=True), indent=2, width=80)}\n```'
                        yield gr.ChatMessage(
                            role='assistant',
                            content=f'🛠️ **工具呼叫：{part.function_call.name}**\n{formatted_call}',
                        )
                    elif part.function_response:
                        response_content = part.function_response.response
                        if (
                            isinstance(response_content, dict)
                            and 'response' in response_content
                        ):
                            formatted_response_data = response_content[
                                'response'
                            ]
                        else:
                            formatted_response_data = response_content
                        formatted_response = f'```json\n{pformat(formatted_response_data, indent=2, width=80)}\n```'
                        yield gr.ChatMessage(
                            role='assistant',
                            content=f'⚡ **來自 {part.function_response.name} 的工具回應**\n{formatted_response}',
                        )
            if event.is_final_response():
                final_response_text = ''
                if event.content and event.content.parts:
                    final_response_text = ''.join(
                        [p.text for p in event.content.parts if p.text]
                    )
                elif event.actions and event.actions.escalate:
                    final_response_text = f'代理 (Agent) 已上報：{event.error_message or "無特定訊息。"}'
                if final_response_text:
                    yield gr.ChatMessage(
                        role='assistant', content=final_response_text
                    )
                break
    except Exception as e:
        print(f'get_response_from_agent 中發生錯誤 (類型：{type(e)})：{e}')
        traceback.print_exc()  # 這將會印出完整的追蹤記錄
        yield gr.ChatMessage(
            role='assistant',
            content='處理您的請求時發生錯誤。請查看伺服器日誌以了解詳細資訊。',
        )


async def main():
    """主要 gradio 應用程式。"""
    print('正在建立 ADK 工作階段...')
    await SESSION_SERVICE.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print('ADK 工作階段已成功建立。')

    with gr.Blocks(
        theme=gr.themes.Ocean(), title='帶有標誌的 A2A 主機代理 (Host Agent)'
    ) as demo:
        gr.Image(
            'https://a2a-protocol.org/latest/assets/a2a-logo-black.svg',
            width=100,
            height=100,
            scale=0,
            show_label=False,
            show_download_button=False,
            container=False,
            show_fullscreen_button=False,
        )
        gr.ChatInterface(
            get_response_from_agent,
            title='A2A 主機代理 (Host Agent)',
            description='此助理可以協助您查詢天氣和尋找 airbnb 住宿',
        )

    print('正在啟動 Gradio 介面...')
    demo.queue().launch(
        server_name='0.0.0.0',
        server_port=8083,
    )
    print('Gradio 應用程式已關閉。')


if __name__ == '__main__':
    asyncio.run(main())
