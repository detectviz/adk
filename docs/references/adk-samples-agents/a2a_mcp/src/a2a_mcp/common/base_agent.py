# type: ignore
from abc import ABC

from pydantic import BaseModel, Field


class BaseAgent(BaseModel, ABC):
    """代理的基礎類別。"""

    model_config = {
        'arbitrary_types_allowed': True,
        'extra': 'allow',
    }

    agent_name: str = Field(
        description='代理的名稱。',
    )

    description: str = Field(
        description="代理用途的簡要說明。",
    )

    content_types: list[str] = Field(description='支援的內容類型。')
