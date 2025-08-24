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

import mimetypes
import gradio as gr
import requests
import base64
from typing import List, Dict, Any
from settings import get_settings
from PIL import Image
import io
from schema import ImageData, ChatRequest, ChatResponse


SETTINGS = get_settings()


def encode_image_to_base64_and_get_mime_type(image_path: str) -> ImageData:
    """將檔案編碼為 base64 字串並取得 MIME 類型。

    讀取圖片檔案並傳回 base64 編碼的圖片資料及其 MIME 類型。

    參數：
        image_path：要編碼的圖片檔案路徑。

    傳回：
        ImageData 物件，包含 base64 編碼的圖片資料及其 MIME 類型。
    """
    # 讀取圖片檔案
    with open(image_path, "rb") as file:
        image_content = file.read()

    # 取得 mime 類型
    mime_type = mimetypes.guess_type(image_path)[0]

    # Base64 編碼圖片
    base64_data = base64.b64encode(image_content).decode("utf-8")

    # 以 ImageData 物件傳回
    return ImageData(serialized_image=base64_data, mime_type=mime_type)


def decode_base64_to_image(base64_data: str) -> Image.Image:
    """將 base64 字串解碼為 PIL 圖片。

    將 base64 編碼的圖片字串轉換回可顯示或進一步處理的 PIL 圖片物件。

    參數：
        base64_data：圖片的 Base64 編碼字串。

    傳回：
        解碼後圖片的 PIL 圖片物件。
    """
    # 解碼 base64 字串並轉換為 PIL 圖片
    image_data = base64.b64decode(base64_data)
    image_buffer = io.BytesIO(image_data)
    image = Image.open(image_buffer)

    return image


def get_response_from_llm_backend(
    message: Dict[str, Any],
    history: List[Dict[str, Any]],
) -> List[str | gr.Image]:
    """將訊息和歷史記錄傳送到後端並取得回應。

    參數：
        message：包含目前訊息的字典，其中包含「text」和可選的「files」鍵。
        history：對話中先前訊息字典的清單。

    傳回：
        包含文字回應和來自後端服務的任何圖片附件的清單。
    """
    # 擷取檔案並轉換為 base64
    image_data = []
    if uploaded_files := message.get("files", []):
        for file_path in uploaded_files:
            image_data.append(encode_image_to_base64_and_get_mime_type(file_path))

    # 準備請求負載
    payload = ChatRequest(
        text=message["text"],
        files=image_data,
        session_id="default_session",
        user_id="default_user",
    )

    # 將請求傳送到後端
    try:
        response = requests.post(SETTINGS.BACKEND_URL, json=payload.model_dump())
        response.raise_for_status()  # 對於 HTTP 錯誤引發例外狀況

        result = ChatResponse(**response.json())
        if result.error:
            return [f"錯誤：{result.error}"]

        chat_responses = []

        if result.thinking_process:
            chat_responses.append(
                gr.ChatMessage(
                    role="assistant",
                    content=result.thinking_process,
                    metadata={"title": "🧠 思維過程"},
                )
            )

        chat_responses.append(gr.ChatMessage(role="assistant", content=result.response))

        if result.attachments:
            for attachment in result.attachments:
                image_data = attachment.serialized_image
                chat_responses.append(gr.Image(decode_base64_to_image(image_data)))

        return chat_responses
    except requests.exceptions.RequestException as e:
        return [f"連線至後端服務時發生錯誤：{str(e)}"]


if __name__ == "__main__":
    demo = gr.ChatInterface(
        get_response_from_llm_backend,
        title="個人開銷助理",
        description="此助理可協助您儲存收據資料、尋找收據，以及追蹤您在特定期間內的開銷。",
        type="messages",
        multimodal=True,
        textbox=gr.MultimodalTextbox(file_count="multiple", file_types=["image"]),
    )

    demo.launch(
        server_name="0.0.0.0",
        server_port=8080,
    )
