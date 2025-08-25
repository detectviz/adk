import logging
import os
import threading
from collections.abc import AsyncIterable
from typing import Annotated, Any, ClassVar

from a2a.types import TextPart
from pydantic import BaseModel, Field

import marvin

logger = logging.getLogger(__name__)


ClarifyingQuestion = Annotated[
    str, Field(description="一個要問使用者的澄清問題")
]


def _to_text_part(text: str) -> TextPart:
    return TextPart(text=text)


class ExtractionOutcome[T](BaseModel):
    """表示嘗試提取聯絡資訊的結果。"""

    extracted_data: T
    summary: str = Field(
        description="提取資訊的摘要。",
    )


class ExtractorAgent[T]:
    """使用 Marvin 框架的聯絡資訊提取代理。"""

    SUPPORTED_CONTENT_TYPES: ClassVar[list[str]] = [
        "text",
        "text/plain",
        "application/json",
    ]

    def __init__(self, instructions: str, result_type: type[T]):
        self.instructions = instructions
        self.result_type = result_type

    async def invoke(self, query: str, sessionId: str) -> dict[str, Any]:
        """使用 marvin 處理使用者查詢

        參數：
            query：使用者的輸入文字。
            sessionId：會話識別碼

        傳回：
            一個描述結果和必要後續步驟的字典。
        """
        try:
            logger.debug(
                f"[會話: {sessionId}] PID: {os.getpid()} | PyThread: {threading.get_ident()} | 正在使用/建立 MarvinThread ID: {sessionId}"
            )

            result = await marvin.run_async(
                query,
                context={
                    "your personality": self.instructions,
                    "reminder": "使用您的記憶來幫助填寫表單",
                },
                thread=marvin.Thread(id=sessionId),
                result_type=ExtractionOutcome[self.result_type] | ClarifyingQuestion,
            )

            if isinstance(result, ExtractionOutcome):
                return {
                    "is_task_complete": True,
                    "require_user_input": False,
                    "text_parts": [_to_text_part(result.summary)],
                    "data": result.extracted_data.model_dump(),
                }
            else:
                assert isinstance(result, str)
                return {
                    "is_task_complete": False,
                    "require_user_input": True,
                    "text_parts": [_to_text_part(result)],
                    "data": None,
                }

        except Exception as e:
            logger.exception(f"在為會話 {sessionId} 呼叫代理期間發生錯誤")
            return {
                "is_task_complete": False,
                "require_user_input": True,
                "text_parts": [
                    _to_text_part(
                        f"抱歉，處理您的請求時發生錯誤：{str(e)}"
                    )
                ],
                "data": None,
            }

    async def stream(self, query: str, sessionId: str) -> AsyncIterable[dict[str, Any]]:
        """串流使用者查詢的回應。

        參數：
            query：使用者的輸入文字。
            sessionId：會話識別碼。

        傳回：
            一個回應字典的非同步可疊代物件。
        """
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "正在分析您的文字以尋找聯絡資訊...",
        }

        yield await self.invoke(query, sessionId)
