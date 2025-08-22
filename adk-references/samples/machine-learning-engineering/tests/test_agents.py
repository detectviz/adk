"""機器學習工程代理及其子代理的測試案例。"""


import dotenv
import os
import sys
import pytest
import textwrap
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.runners import InMemoryRunner
from google.adk.sessions import InMemorySessionService

from machine_learning_engineering.agent import root_agent

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_happy_path():
    """在簡單輸入上執行代理並期望正常回應。"""
    user_input = textwrap.dedent(
        """
        問題：你是誰
        答案：你好！我是一個機器學習工程代理。
    """
    ).strip()

    app_name = "machine-learning-engineering"

    runner = InMemoryRunner(agent=root_agent, app_name=app_name)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )
    content = types.Content(parts=[types.Part(text=user_input)], role="user")
    response = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        print(event)
        if event.content.parts and event.content.parts[0].text:
            response = event.content.parts[0].text

    # 正確的答案應提及「機器學習」。
    assert "machine learning" in response.lower()

if __name__ == "__main__":
    unittest.main()
