"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from expense_manager_agent.agent import root_agent as expense_manager_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from fastapi import FastAPI, Body, Depends
from typing import AsyncIterator
from types import SimpleNamespace
import uvicorn
from contextlib import asynccontextmanager
import asyncio
from utils import (
    extract_attachment_ids_and_sanitize_response,
    download_image_from_gcs,
    extract_thinking_process,
    format_user_request_to_adk_content_and_store_artifacts,
)
from schema import ImageData, ChatRequest, ChatResponse
import logger
from google.adk.artifacts import GcsArtifactService
from settings import get_settings

SETTINGS = get_settings()
APP_NAME = "expense_manager_app"


# 應用程式狀態，用於存放服務內容
class AppContexts(SimpleNamespace):
    """一個可透過屬性存取來存放應用程式內容的類別"""

    session_service: InMemorySessionService = None
    artifact_service: GcsArtifactService = None
    expense_manager_agent_runner: Runner = None


# 初始化應用程式狀態
app_contexts = AppContexts()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 在應用程式啟動期間初始化服務內容
    app_contexts.session_service = InMemorySessionService()
    app_contexts.artifact_service = GcsArtifactService(
        bucket_name=SETTINGS.STORAGE_BUCKET_NAME
    )
    app_contexts.expense_manager_agent_runner = Runner(
        agent=expense_manager_agent,  # 我們要執行的代理 (agent)
        app_name=APP_NAME,  # 將執行與我們的應用程式關聯
        session_service=app_contexts.session_service,  # 使用我們的會話管理員 (session manager)
        artifact_service=app_contexts.artifact_service,  # 使用我們的成品管理員 (artifact manager)
    )

    logger.info("應用程式已成功啟動")
    yield
    logger.info("應用程式正在關閉")
    # 如有必要，在應用程式關閉期間執行清理


# 取得應用程式狀態作為相依項的輔助函式
async def get_app_contexts() -> AppContexts:
    return app_contexts


# 建立 FastAPI 應用程式
app = FastAPI(title="個人開銷助理 API", lifespan=lifespan)


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest = Body(...),
    app_context: AppContexts = Depends(get_app_contexts),
) -> ChatResponse:
    """處理聊天請求並從代理取得回應"""

    # 以 ADK 格式準備使用者訊息並儲存圖片成品
    content = await asyncio.to_thread(
        format_user_request_to_adk_content_and_store_artifacts,
        request=request,
        app_name=APP_NAME,
        artifact_service=app_context.artifact_service,
    )

    final_response_text = "代理未產生最終回應。"  # 預設值

    # 使用請求中的會話 ID，如果未提供則使用預設值
    session_id = request.session_id
    user_id = request.user_id

    # 如果會話不存在，則建立會話
    if not app_context.session_service.get_session(
        app_name=APP_NAME, user_id=user_id, session_id=session_id
    ):
        app_context.session_service.create_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

    try:
        # 使用代理處理訊息
        # 類型註解：runner.run_async 回傳一個 AsyncIterator[Event]
        events_iterator: AsyncIterator[Event] = (
            app_context.expense_manager_agent_runner.run_async(
                user_id=user_id, session_id=session_id, new_message=content
            )
        )
        async for event in events_iterator:  # event 的類型為 Event
            # 關鍵概念：is_final_response() 標示該輪的結束訊息
            if event.is_final_response():
                if event.content and event.content.parts:
                    # 從第一個部分擷取文字
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    # 處理潛在的錯誤/升級
                    final_response_text = f"代理已升級：{event.error_message or '無特定訊息。'}"
                break  # 找到最終回應後停止處理事件

        logger.info(
            "從代理收到最終回應", raw_final_response=final_response_text
        )

        # 擷取並處理回應中的任何附件和思維過程
        base64_attachments = []
        sanitized_text, attachment_ids = extract_attachment_ids_and_sanitize_response(
            final_response_text
        )
        sanitized_text, thinking_process = extract_thinking_process(sanitized_text)

        # 從 GCS 下載圖片並將雜湊 ID 取代為 base64 資料
        for image_hash_id in attachment_ids:
            # 下載圖片資料並取得 MIME 類型
            result = await asyncio.to_thread(
                download_image_from_gcs,
                artifact_service=app_context.artifact_service,
                image_hash=image_hash_id,
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )
            if result:
                base64_data, mime_type = result
                base64_attachments.append(
                    ImageData(serialized_image=base64_data, mime_type=mime_type)
                )

        logger.info(
            "已處理附有附件的回應",
            sanitized_response=sanitized_text,
            thinking_process=thinking_process,
            attachment_ids=attachment_ids,
        )

        return ChatResponse(
            response=sanitized_text,
            thinking_process=thinking_process,
            attachments=base64_attachments,
        )

    except Exception as e:
        logger.error("處理聊天請求時發生錯誤", error_message=str(e))
        return ChatResponse(
            response="", error=f"產生回應時發生錯誤：{str(e)}"
        )


# 僅在直接執行此檔案時才執行伺服器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
