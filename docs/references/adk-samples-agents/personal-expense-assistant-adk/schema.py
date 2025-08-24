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

from pydantic import BaseModel
from typing import List, Optional


class ImageData(BaseModel):
    """具有雜湊識別碼的圖片資料模型。

    屬性：
        serialized_image：圖片內容的 Base64 編碼字串（可選）。
        mime_type：圖片的 MIME 類型。
    """

    serialized_image: str
    mime_type: str


class ChatRequest(BaseModel):
    """聊天請求的模型。

    屬性：
        text：訊息的文字內容。
        files：圖片資料物件清單。
        session_id：對話的會話識別碼。
        user_id：對話的使用者識別碼。
    """

    text: str
    files: List[ImageData] = []
    session_id: str = "default_session"
    user_id: str = "default_user"


class ChatResponse(BaseModel):
    """聊天回應的模型。

    屬性：
        response：模型的回應文字。
        thinking_process：模型的可選思維過程。
        attachments：要向使用者顯示的圖片資料清單。
        error：如果發生錯誤，則為可選的錯誤訊息。
    """

    response: str
    thinking_process: str = ""
    attachments: List[ImageData] = []
    error: Optional[str] = None
