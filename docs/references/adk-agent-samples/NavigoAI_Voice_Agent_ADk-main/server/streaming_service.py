from core_utils import (
    BaseStreamServer,
    stream_logger,
    MODEL,
    VOICE_NAME,
    SEND_SAMPLE_RATE,
    SYSTEM_INSTRUCTION
)
import asyncio
import json
import base64
import logging
import os
import traceback

# Import Google ADK components
from google.adk.agents import Agent, LiveRequestQueue
from google.adk.runners import Runner
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
from google.adk.tools import google_search
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

load_dotenv()

# Import common components

# 用於訂單狀態的函式工具


class StreamingService(BaseStreamServer):
    """用於音訊和視訊資料的即時串流服務。"""

    def __init__(self, host="0.0.0.0", port=8080):
        super().__init__(host, port)

        # 從環境變數中檢索 API 金鑰或直接插入。
        google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

        if not google_maps_api_key:
            # 用於測試的後備或直接指派 - 不建議在生產環境中使用
            # 如果不使用環境變數，請替換
            google_maps_api_key = "YOUR_GOOGLE_MAPS_API_KEY_HERE"
            if google_maps_api_key == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
                print(
                    "警告：GOOGLE_MAPS_API_KEY 未設定。請將其設定為環境變數或在腳本中設定。")

        # 初始化 ADK 元件
        self.agent = Agent(
            name="voice_assistant_agent",
            model=MODEL,
            instruction=SYSTEM_INSTRUCTION,
            tools=[
                google_search,
                MCPToolset(
                    connection_params=StdioServerParameters(
                        command='npx',
                        args=[
                            "-y",
                            "@modelcontextprotocol/server-google-maps",
                        ],
                        env={
                            "GOOGLE_MAPS_API_KEY": google_maps_api_key
                        }
                    ),
                )
            ],
        )

        # 建立會話服務
        self.session_service = InMemorySessionService()

    async def handle_stream(self, websocket, client_id):
        """處理來自用戶端的即時資料流。"""
        # 儲存用戶端參考
        self.active_connections[client_id] = websocket

        # 為用戶端建立新會話
        user_id = f"user_{client_id}"
        session_id = f"session_{client_id}"
        await self.session_service.create_session(
            app_name="streaming_assistant",
            user_id=user_id,
            session_id=session_id,
        )

        # 建立執行器
        runner = Runner(
            app_name="streaming_assistant",
            agent=self.agent,
            session_service=self.session_service,
        )

        # 建立即時請求佇列
        live_request_queue = LiveRequestQueue()

        # 建立包含音訊設定的執行組態
        run_config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=VOICE_NAME
                    )
                )
            ),
            response_modalities=["AUDIO"],
            output_audio_transcription=types.AudioTranscriptionConfig(),
            input_audio_transcription=types.AudioTranscriptionConfig(),
        )

        # 用於來自用戶端的音訊和視訊資料的佇列
        audio_queue = asyncio.Queue()
        video_queue = asyncio.Queue()

        async with asyncio.TaskGroup() as tg:
            # 處理傳入 WebSocket 訊息的任務
            async def receive_client_messages():
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get("type") == "audio":
                            audio_bytes = base64.b64decode(
                                data.get("data", ""))
                            await audio_queue.put(audio_bytes)
                        elif data.get("type") == "video":
                            video_bytes = base64.b64decode(
                                data.get("data", ""))
                            video_mode = data.get("mode", "webcam")
                            await video_queue.put({"data": video_bytes, "mode": video_mode})
                        elif data.get("type") == "end":
                            stream_logger.info(
                                "用戶端已完成此回合的資料傳輸。")
                        elif data.get("type") == "text":
                            stream_logger.info(
                                f"收到來自用戶端的文字： {data.get('data')}")
                    except json.JSONDecodeError:
                        stream_logger.error(
                            "無法解碼傳入的 JSON 訊息。")
                    except Exception as e:
                        stream_logger.error(
                            f"處理用戶端訊息時發生例外狀況： {e}")

            async def send_audio_to_service():
                while True:
                    data = await audio_queue.get()
                    live_request_queue.send_realtime(
                        types.Blob(
                            data=data, mime_type=f"audio/pcm;rate={SEND_SAMPLE_RATE}")
                    )
                    audio_queue.task_done()

            async def send_video_to_service():
                while True:
                    video_data = await video_queue.get()
                    video_bytes = video_data.get("data")
                    video_mode = video_data.get("mode", "webcam")
                    stream_logger.info(
                        f"正在從來源傳輸視訊幀： {video_mode}")
                    live_request_queue.send_realtime(
                        types.Blob(data=video_bytes, mime_type="image/jpeg")
                    )
                    video_queue.task_done()

            async def receive_service_responses():
                # 在回合完成事件之間追蹤使用者和模型的輸出
                input_texts = []
                output_texts = []
                current_session_id = None

                # 用於追蹤目前回合中是否發生中斷的旗標
                interrupted = False

                # 處理來自代理的回應
                async for event in runner.run_live(
                    user_id=user_id,
                    session_id=session_id,
                    live_request_queue=live_request_queue,
                    run_config=run_config,
                ):
                    # 使用字串比對檢查回合完成或中斷
                    # 在有適當的 API 之前，這是一種後備方法
                    event_str = str(event)

                    # 如果有會話恢復更新，則儲存會話 ID
                    if hasattr(event, 'session_resumption_update') and event.session_resumption_update:
                        update = event.session_resumption_update
                        if update.resumable and update.new_handle:
                            current_session_id = update.new_handle
                            stream_logger.info(
                                f"已使用控制代碼建立新會話： {current_session_id}")
                            # 將會話 ID 傳送至用戶端
                            session_id_msg = json.dumps({
                                "type": "session_id",
                                "data": current_session_id
                            })
                            await websocket.send(session_id_msg)

                    # 處理內容
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            # 處理音訊內容
                            if hasattr(part, "inline_data") and part.inline_data:
                                b64_audio = base64.b64encode(
                                    part.inline_data.data).decode("utf-8")
                                await websocket.send(json.dumps({"type": "audio", "data": b64_audio}))

                            # 處理文字內容
                            if hasattr(part, "text") and part.text:
                                # 根據內容角色檢查這是使用者文字還是模型文字
                                if hasattr(event.content, "role") and event.content.role == "user":
                                    # 使用者文字應傳送至用戶端
                                    if "partial=True" in event_str:
                                        await websocket.send(json.dumps({"type": "user_transcript", "data": part.text}))
                                    input_texts.append(part.text)
                                else:
                                    # 從日誌中，我們可以看到重複的文字問題發生是因為
                                    # 我們收到了帶有 "partial=True" 的串流區塊，後面跟著一個包含完整文字的最終合併
                                    # 回應，其中 "partial=None"

                                    # 在事件字串中檢查部分旗標
                                    # 僅處理帶有 "partial=True" 的訊息
                                    if "partial=True" in event_str:
                                        await websocket.send(json.dumps({"type": "text", "data": part.text}))
                                        output_texts.append(part.text)
                                    # 跳過帶有 "partial=None" 的訊息以避免重複

                    # 檢查中斷
                    if event.interrupted and not interrupted:
                        stream_logger.warning(
                            "使用者已中斷串流。")
                        await websocket.send(json.dumps({
                            "type": "interrupted",
                            "data": "回應被使用者輸入中斷"
                        }))
                        interrupted = True

                    # 檢查回合完成
                    if event.turn_complete:
                        # 僅在沒有中斷的情況下傳送 turn_complete
                        if not interrupted:
                            stream_logger.info(
                                "模型已完成其回合。")
                            await websocket.send(json.dumps({
                                "type": "turn_complete",
                                "session_id": current_session_id
                            }))

                        # 記錄收集的轉錄以進行偵錯
                        if input_texts:
                            # 取得唯一的文字以防止重複
                            unique_texts = list(dict.fromkeys(input_texts))
                            stream_logger.info(
                                f"轉錄的使用者語音： {' '.join(unique_texts)}")

                        if output_texts:
                            # 取得唯一的文字以防止重複
                            unique_texts = list(dict.fromkeys(output_texts))
                            stream_logger.info(
                                f"產生的模型回應： {' '.join(unique_texts)}")

                        # 為下一回合重設
                        input_texts = []
                        output_texts = []
                        interrupted = False

            # 啟動所有任務
            tg.create_task(receive_client_messages(),
                           name="ClientMessageReceiver")
            tg.create_task(send_audio_to_service(), name="AudioSender")
            tg.create_task(send_video_to_service(), name="VideoSender")
            tg.create_task(receive_service_responses(),
                           name="ServiceResponseReceiver")


async def main():
    """啟動伺服器的主函式"""
    server = StreamingService()
    await server.start_server()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        stream_logger.info("伺服器正在關閉。")
    except Exception as e:
        stream_logger.critical(f"發生致命的未處理例外狀況： {e}")
        import traceback
        traceback.print_exc()
