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

import os
import json
import asyncio
import base64
import warnings

from pathlib import Path
from dotenv import load_dotenv

from google.genai.types import (
    Part,
    Content,
    Blob,
)

from google.adk.runners import InMemoryRunner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from google_search_agent.agent import root_agent

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

#
# ADK 串流
#

# 載入 Gemini API 金鑰
load_dotenv()

APP_NAME = "ADK 串流範例"


async def start_agent_session(user_id, is_audio=False):
    """啟動一個代理會話"""

    # 建立一個 Runner
    runner = InMemoryRunner(
        app_name=APP_NAME,
        agent=root_agent,
    )

    # 建立一個會話
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,  # 請替換為實際的使用者 ID
    )

    # 設定回應的模態
    modality = "AUDIO" if is_audio else "TEXT"
    run_config = RunConfig(response_modalities=[modality])

    # 為此會話建立一個 LiveRequestQueue
    live_request_queue = LiveRequestQueue()

    # 啟動代理會話
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )
    return live_events, live_request_queue


async def agent_to_client_messaging(websocket, live_events):
    """代理到客戶端的通訊"""
    async for event in live_events:

        # 如果回合完成或被中斷，則發送它
        if event.turn_complete or event.interrupted:
            message = {
                "turn_complete": event.turn_complete,
                "interrupted": event.interrupted,
            }
            await websocket.send_text(json.dumps(message))
            print(f"[代理到客戶端]: {message}")
            continue

        # 讀取 Content 及其第一個 Part
        part: Part = (
            event.content and event.content.parts and event.content.parts[0]
        )
        if not part:
            continue

        # 如果是音訊，則發送 Base64 編碼的音訊資料
        is_audio = part.inline_data and part.inline_data.mime_type.startswith("audio/pcm")
        if is_audio:
            audio_data = part.inline_data and part.inline_data.data
            if audio_data:
                message = {
                    "mime_type": "audio/pcm",
                    "data": base64.b64encode(audio_data).decode("ascii")
                }
                await websocket.send_text(json.dumps(message))
                print(f"[代理到客戶端]: audio/pcm: {len(audio_data)} 位元組。")
                continue

        # 如果是文字且為部分文字，則發送它
        if part.text and event.partial:
            message = {
                "mime_type": "text/plain",
                "data": part.text
            }
            await websocket.send_text(json.dumps(message))
            print(f"[代理到客戶端]: text/plain: {message}")


async def client_to_agent_messaging(websocket, live_request_queue):
    """客戶端到代理的通訊"""
    while True:
        # 解碼 JSON 訊息
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]

        # 將訊息傳送給代理
        if mime_type == "text/plain":
            # 傳送文字訊息
            content = Content(role="user", parts=[Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            print(f"[客戶端到代理]: {data}")
        elif mime_type == "audio/pcm":
            # 傳送音訊資料
            decoded_data = base64.b64decode(data)
            live_request_queue.send_realtime(Blob(data=decoded_data, mime_type=mime_type))
        else:
            raise ValueError(f"不支援的 Mime 類型：{mime_type}")


#
# FastAPI 網頁應用程式
#

app = FastAPI()

STATIC_DIR = Path("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """提供 index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, is_audio: str):
    """客戶端 websocket 端點"""

    # 等待客戶端連線
    await websocket.accept()
    print(f"客戶端 #{user_id} 已連線，音訊模式：{is_audio}")

    # 啟動代理會話
    user_id_str = str(user_id)
    live_events, live_request_queue = await start_agent_session(user_id_str, is_audio == "true")

    # 啟動任務
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue)
    )

    # 等待直到 websocket 中斷連線或發生錯誤
    tasks = [agent_to_client_task, client_to_agent_task]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # 關閉 LiveRequestQueue
    live_request_queue.close()

    # 中斷連線
    print(f"客戶端 #{user_id} 已中斷連線")
