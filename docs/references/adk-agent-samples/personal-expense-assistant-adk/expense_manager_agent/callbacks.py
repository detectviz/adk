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

import hashlib
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest


def modify_image_data_in_history(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> None:
    # 下列程式碼將修改傳送至大型語言模型 (LLM) 的請求
    # 我們將使用反向和計數器的方法，僅保留最近 3 則使用者訊息中的圖片資料

    # 計算我們已處理的使用者訊息數量
    user_message_count = 0

    # 處理反向列表
    for content in reversed(llm_request.contents):
        # 僅計算使用者手動查詢，而非函式呼叫
        if (content.role == "user") and (content.parts[0].function_response is None):
            user_message_count += 1
            modified_content_parts = []

            # 檢查任何圖片資料是否缺少圖片 ID 佔位符
            # 然後，如果超過 3 則使用者訊息，則從對話記錄中移除圖片資料
            for idx, part in enumerate(content.parts):
                if part.inline_data is None:
                    modified_content_parts.append(part)
                    continue

                if (
                    (idx + 1 >= len(content.parts))
                    or (content.parts[idx + 1].text is None)
                    or (not content.parts[idx + 1].text.startswith("[IMAGE-ID "))
                ):
                    # 為圖片產生雜湊 ID 並新增佔位符
                    image_data = part.inline_data.data
                    hasher = hashlib.sha256(image_data)
                    image_hash_id = hasher.hexdigest()[:12]
                    placeholder = f"[IMAGE-ID {image_hash_id}]"

                    # 僅在最近 3 則使用者訊息中保留圖片資料
                    if user_message_count <= 3:
                        modified_content_parts.append(part)

                    modified_content_parts.append(types.Part(text=placeholder))

                else:
                    # 僅在最近 3 則使用者訊息中保留圖片資料
                    if user_message_count <= 3:
                        modified_content_parts.append(part)

            # 這將修改 llm_request 內的內容
            content.parts = modified_content_parts
