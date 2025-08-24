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

from google.cloud import storage
from settings import get_settings
import base64
import re
from schema import ChatRequest, ImageData
from google.genai import types
import hashlib
import json
from google.adk.artifacts import GcsArtifactService
import logger


SETTINGS = get_settings()

GCS_BUCKET_CLIENT = storage.Client(project=SETTINGS.GCLOUD_PROJECT_ID).get_bucket(
    SETTINGS.STORAGE_BUCKET_NAME
)


def store_uploaded_image_as_artifact(
    artifact_service: GcsArtifactService,
    app_name: str,
    user_id: str,
    session_id: str,
    image_data: ImageData,
) -> tuple[str, bytes]:
    """
    將上傳的圖片儲存為 Google Cloud Storage 中的成品。

    參數：
        artifact_service：用於儲存成品的成品服務
        app_name：應用程式的名稱
        user_id：使用者的 ID
        session_id：會話的 ID
        image_data：要儲存的圖片資料

    傳回：
        tuple[str, bytes]：一個包含圖片雜湊 ID 和圖片位元組的元組
    """

    # 解碼 base64 圖片資料並用其產生雜湊 id
    image_byte = base64.b64decode(image_data.serialized_image)
    hasher = hashlib.sha256(image_byte)
    image_hash_id = hasher.hexdigest()[:12]

    artifact_versions = artifact_service.list_versions(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=image_hash_id,
    )
    if artifact_versions:
        logger.info(f"圖片 {image_hash_id} 已存在於 GCS，略過上傳")

        return image_hash_id, image_byte

    artifact_service.save_artifact(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        filename=image_hash_id,
        artifact=types.Part(
            inline_data=types.Blob(mime_type=image_data.mime_type, data=image_byte)
        ),
    )

    return image_hash_id, image_byte


def download_image_from_gcs(
    artifact_service: GcsArtifactService,
    app_name: str,
    user_id: str,
    session_id: str,
    image_hash: str,
) -> tuple[str, str] | None:
    """
    從 Google Cloud Storage 下載圖片成品並
    以 base64 編碼字串及其 MIME 類型傳回。
    使用本機快取以避免重複下載。

    參數：
        artifact_service：用於下載成品的成品服務
        app_name：應用程式的名稱
        user_id：使用者的 ID
        session_id：會話的 ID
        image_hash：要下載的圖片的雜湊識別碼

    傳回：
        tuple[str, str] | None：一個包含 (base64_encoded_data, mime_type) 的元組，如果下載失敗則為 None
    """
    try:
        artifact = artifact_service.load_artifact(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            filename=image_hash,
        )
        if not artifact:
            logger.info(f"圖片 {image_hash} 不存在於 GCS 成品服務中")
            return None

        # 取得 blob 和 mime 類型
        image_data = artifact.inline_data.data
        mime_type = artifact.inline_data.mime_type

        logger.info(f"已下載類型為 {mime_type} 的圖片 {image_hash}")

        return base64.b64encode(image_data).decode("utf-8"), mime_type
    except Exception as e:
        logger.error(f"從 GCS 下載圖片時發生錯誤：{e}")
        return None


def format_user_request_to_adk_content_and_store_artifacts(
    request: ChatRequest, app_name: str, artifact_service: GcsArtifactService
) -> types.Content:
    """將使用者請求格式化為 ADK 內容格式。

    參數：
        request：包含文字和可選檔案的聊天請求物件
        app_name：應用程式的名稱
        artifact_service：用於儲存成品的成品服務

    傳回：
        types.Content：ADK 的格式化內容
    """
    # 建立一個清單來存放各個部分
    parts = []

    # 如果存在，則處理圖片檔案
    for data in request.files:
        # 處理圖片並新增字串佔位符

        image_hash_id, image_byte = store_uploaded_image_as_artifact(
            artifact_service=artifact_service,
            app_name=app_name,
            user_id=request.user_id,
            session_id=request.session_id,
            image_data=data,
        )

        # 新增內嵌資料部分
        parts.append(
            types.Part(
                inline_data=types.Blob(mime_type=data.mime_type, data=image_byte)
            )
        )

        # 新增圖片佔位符識別碼
        placeholder = f"[IMAGE-ID {image_hash_id}]"
        parts.append(types.Part(text=placeholder))

    # 處理使用者未指定文字輸入的情況
    if not request.text:
        request.text = " "

    parts.append(types.Part(text=request.text))

    # 建立並傳回內容物件
    return types.Content(role="user", parts=parts)


def sanitize_image_id(image_id: str) -> str:
    """透過移除任何前置/後置空格來清理圖片 ID。"""
    if image_id.startswith("[IMAGE-"):
        image_id = image_id.split("ID ")[1].split("]")[0]

    return image_id.strip()


def extract_attachment_ids_and_sanitize_response(
    response_text: str,
) -> tuple[str, list[str]]:
    """從 FINAL RESPONSE 區段的 JSON 程式碼區塊中擷取圖片雜湊 ID。

    參數：
        response_text：來自 LLM 的 markdown 格式的回應文字。

    傳回：
        tuple[str, list[str]]：一個包含已清理的回應文字和圖片雜湊 ID 清單的元組。
    """
    # JSON 程式碼區塊模式，尋找 ```json { ... } ```
    json_block_pattern = r"```json\s*({[^`]*?})\s*```"
    json_match = re.search(json_block_pattern, response_text, re.DOTALL)

    all_attachments_hash_ids = []
    sanitized_text = response_text

    if json_match:
        json_str = json_match.group(1).strip()
        try:
            # 嘗試剖析 JSON
            json_data = json.loads(json_str)

            # 如果附件 ID 以預期格式存在，則擷取它們
            if isinstance(json_data, dict) and "attachments" in json_data:
                attachments = json_data["attachments"]
                if isinstance(attachments, list):
                    # 從每個附件字串中擷取圖片 ID
                    for attachment_id in attachments:
                        all_attachments_hash_ids.append(
                            sanitize_image_id(attachment_id)
                        )

            # 從回應中移除 JSON 區塊
            sanitized_text = response_text.replace(json_match.group(0), "")
        except json.JSONDecodeError:
            # 如果 JSON 剖析失敗，請嘗試使用 regex 直接擷取圖片 ID
            id_pattern = r"\[IMAGE-ID\s+([^\]]+)\]"
            hash_id_matches = re.findall(id_pattern, json_str)
            all_attachments_hash_ids = [
                sanitize_image_id(match.strip())
                for match in hash_id_matches
                if match.strip()
            ]

            # 從回應中移除 JSON 區塊
            sanitized_text = response_text.replace(json_match.group(0), "")

    # 清理已清理的文字
    sanitized_text = sanitized_text.strip()

    return sanitized_text, all_attachments_hash_ids


def extract_thinking_process(response_text: str) -> tuple[str, str]:
    """從回應文字中擷取思維過程並清理回應。

    預期的回應應如下所示

    # THINKING PROCESS
    <thinking process>

    # FINAL RESPONSE
    <final response>

    參數：
        response_text：來自 LLM 的 markdown 格式的回應文字。

    傳回：
        tuple[str, str]：一個包含已清理的回應文字和擷取的思維過程的元組。
    """
    # 比對直到 FINAL RESPONSE 標題或結尾
    thinking_pattern = r"#\s*THINKING PROCESS[\s\S]*?(?=#\s*FINAL RESPONSE|\Z)"
    thinking_match = re.search(thinking_pattern, response_text, re.MULTILINE)

    thinking_process = ""

    if thinking_match:
        # 擷取不含標題的內容
        thinking_content = thinking_match.group(0)
        # 移除標題並僅取得內容
        thinking_process = re.sub(
            r"^#\s*THINKING PROCESS\s*", "", thinking_content, flags=re.MULTILINE
        ).strip()

        # 從回應中移除 THINKING PROCESS 區段
        sanitized_text = response_text.replace(thinking_content, "")
    else:
        sanitized_text = response_text

    # 如果存在，則僅擷取 FINAL RESPONSE 區段作為已清理的文字
    final_response_pattern = r"#\s*FINAL RESPONSE[\s\S]*?(?=#\s*ATTACHMENTS|\Z)"  # 比對直到 ATTACHMENTS 標題或結尾
    final_response_match = re.search(
        final_response_pattern, sanitized_text, re.MULTILINE
    )

    if final_response_match:
        # 擷取不含標題的內容
        final_response_content = final_response_match.group(0)
        # 移除標題並僅取得內容
        sanitized_text = re.sub(
            r"^#\s*FINAL RESPONSE\s*", "", final_response_content, flags=re.MULTILINE
        ).strip()

    return sanitized_text, thinking_process
