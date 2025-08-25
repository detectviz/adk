
"""圖像評分的基本評估。"""

import pathlib
import dotenv
import pytest
from google.adk.evaluation import AgentEvaluator

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest.mark.asyncio
async def test_all():
    """測試代理在一些範例上的基本能力。"""
    await AgentEvaluator.evaluate(
        "image_scoring",
        str(pathlib.Path(__file__).parent / "data"),
        num_runs=2,
    )
