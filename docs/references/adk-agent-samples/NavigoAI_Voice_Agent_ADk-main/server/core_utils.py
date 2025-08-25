import asyncio
import json
import base64
import logging
import os
import websockets
import traceback
from websockets.exceptions import ConnectionClosed

# 設定日誌
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
stream_logger = logging.getLogger(__name__)


# 常數
load_dotenv()

PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")
MODEL = os.environ.get("MODEL")
VOICE_NAME = os.environ.get("VOICE_NAME")
GOOGLE_GENAI_USE_VERTEXAI = "FALSE"


# 輸入/輸出的音訊取樣率
RECEIVE_SAMPLE_RATE = 24000  # 從 Gemini 接收的音訊速率
SEND_SAMPLE_RATE = 16000     # 傳送至 Gemini 的音訊速率

# 兩種實作都使用的系統指令
SYSTEM_INSTRUCTION = """
您是 NaviGo AI，一個友善且樂於助人的旅遊助理。
您像一位 40 多歲的印度女性旅遊代理與使用者交談，她對旅遊目的地、路線和當地景點非常了解。
您的目標是為使用者提供準確且相關的旅遊資訊。
您應該在對話開始時自我介紹：要有創新和創意，但要提及您的名字 Navigo AI 和您的工作。
您可以使用 google_search 工具來回答一般的旅遊查詢。
當使用者有任何關於地點、導航的問題時，它會使用 google maps mcp 工具。
避免提供任何關於您自己、您的能力或您使用的工具的資訊。

您的回答要清晰。始終保持回答簡潔扼要。
如果您不知道問題的答案，請禮貌地告知使用者您沒有該資訊。
如果使用者詢問與旅遊無關的資訊，請禮貌地告知他們您無法提供協助。
"""

# 處理通用功能的基礎 WebSocket 伺服器類別


class BaseStreamServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.active_connections = {}  # 儲存用戶端連線

    async def start_server(self):
        stream_logger.info(f"正在 {self.host}:{self.port} 上啟動串流伺服器")
        async with websockets.serve(self.manage_connection, self.host, self.port):
            await asyncio.Future()  # 永久執行

    async def manage_connection(self, websocket):
        """處理新的用戶端連線"""
        connection_id = id(websocket)
        stream_logger.info(f"已建立新連線： {connection_id}")

        # 向用戶端傳送準備就緒訊息
        await websocket.send(json.dumps({"type": "ready"}))

        try:
            # 開始處理此用戶端的串流
            await self.handle_stream(websocket, connection_id)
        except ConnectionClosed:
            stream_logger.info(f"連線已關閉： {connection_id}")
        except Exception as e:
            stream_logger.error(f"處理連線 {connection_id} 時發生錯誤： {e}")
            stream_logger.error(traceback.format_exc())
        finally:
            # 清理
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]

    async def handle_stream(self, websocket, client_id):
        """
        處理來自用戶端的資料流。這是一個抽象方法，子類別必須實作。
        """
        raise NotImplementedError("子類別必須實作 handle_stream")
