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
import sys

from adk_answering_agent.settings import ADK_DOCS_ROOT_PATH
from adk_answering_agent.settings import ADK_PYTHON_ROOT_PATH
from adk_answering_agent.settings import GCS_BUCKET_NAME
from adk_answering_agent.settings import GOOGLE_CLOUD_PROJECT
from adk_answering_agent.settings import VERTEXAI_DATASTORE_ID
from google.api_core.exceptions import GoogleAPICallError
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.cloud import storage
import markdown

GCS_PREFIX_TO_ROOT_PATH = {
    "adk-docs": ADK_DOCS_ROOT_PATH,
    "adk-python": ADK_PYTHON_ROOT_PATH,
}


def cleanup_gcs_prefix(project_id: str, bucket_name: str, prefix: str) -> bool:
  """刪除儲存桶中具有給定前綴的所有物件。"""
  print(f"開始清理 GCS：gs://{bucket_name}/{prefix}...")
  try:
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))

    if not blobs:
      print("GCS 目標位置已為空，無需清理。")
      return True

    bucket.delete_blobs(blobs)
    print(f"成功刪除 {len(blobs)} 個物件。")
    return True
  except GoogleAPICallError as e:
    print(f"[錯誤] 清理 GCS 失敗：{e}", file=sys.stderr)
    return False


def upload_directory_to_gcs(
    source_directory: str, project_id: str, bucket_name: str, prefix: str
) -> bool:
  """將整個目錄上傳到 GCS。"""
  print(
      f"開始將目錄 {source_directory} 上傳到 GCS："
      f" gs://{bucket_name}/{prefix}..."
  )

  if not os.path.isdir(source_directory):
    print(f"[錯誤] {source_directory} 不是目錄或不存在。")
    return False

  storage_client = storage.Client(project=project_id)
  bucket = storage_client.bucket(bucket_name)
  file_count = 0
  for root, dirs, files in os.walk(source_directory):
    # 就地修改 'dirs' 列表，以防止 os.walk 進入
    # 隱藏目錄。
    dirs[:] = [d for d in dirs if not d.startswith(".")]

    # 僅保留 .md 和 .py 檔案。
    files = [f for f in files if f.endswith(".md") or f.endswith(".py")]

    for filename in files:
      local_path = os.path.join(root, filename)

      relative_path = os.path.relpath(local_path, source_directory)
      gcs_path = os.path.join(prefix, relative_path)

      try:
        content_type = None
        if filename.lower().endswith(".md"):
          # Vertex AI Search 無法識別 text/markdown，
          # 將其轉換為 html 並改用 text/html
          content_type = "text/html"
          with open(local_path, "r", encoding="utf-8") as f:
            md_content = f.read()
          html_content = markdown.markdown(
              md_content, output_format="html5", encoding="utf-8"
          )
          if not html_content:
            print("  - 已略過空檔案：" + local_path)
            continue
          gcs_path = gcs_path.removesuffix(".md") + ".html"
          bucket.blob(gcs_path).upload_from_string(
              html_content, content_type=content_type
          )
        else:  # Python 檔案
          bucket.blob(gcs_path).upload_from_filename(
              local_path, content_type=content_type
          )
        type_msg = (
            f"(類型 {content_type})" if content_type else "(類型自動偵測)"
        )
        print(
            f"  - 已上傳 {type_msg}：{local_path} ->"
            f" gs://{bucket_name}/{gcs_path}"
        )
        file_count += 1
      except GoogleAPICallError as e:
        print(
            f"[錯誤] 上傳檔案 {local_path} 時發生錯誤：{e}", file=sys.stderr
        )
        return False

  print(f"成功將 {file_count} 個檔案上傳到 GCS。")
  return True


def import_from_gcs_to_vertex_ai(
    full_datastore_id: str,
    gcs_bucket: str,
) -> bool:
  """從 GCS 資料夾觸發大量匯入工作至 Vertex AI Search。"""
  print(f"正在從 gs://{gcs_bucket}/** 觸發完整同步匯入...")

  try:
    client = discoveryengine.DocumentServiceClient()
    gcs_uri = f"gs://{gcs_bucket}/**"
    request = discoveryengine.ImportDocumentsRequest(
        # parent 的格式為
        # "projects/{project_number}/locations/{location}/collections/{collection}/dataStores/{datastore_id}/branches/default_branch"
        parent=full_datastore_id + "/branches/default_branch",
        # 指定 GCS 來源並對非結構化資料使用 "content"。
        gcs_source=discoveryengine.GcsSource(
            input_uris=[gcs_uri], data_schema="content"
        ),
        reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.FULL,
    )
    operation = client.import_documents(request=request)
    print(
        "已成功啟動完整同步匯入操作。"
        f"操作名稱：{operation.operation.name}"
    )
    return True

  except GoogleAPICallError as e:
    print(f"[錯誤] 觸發匯入時發生錯誤：{e}", file=sys.stderr)
    return False


def main():
  # 檢查必要的環境變數。
  if not GOOGLE_CLOUD_PROJECT:
    print(
        "[錯誤] 未設定 GOOGLE_CLOUD_PROJECT 環境變數。正在結束...",
        file=sys.stderr,
    )
    return 1
  if not GCS_BUCKET_NAME:
    print(
        "[錯誤] 未設定 GCS_BUCKET_NAME 環境變數。正在結束...",
        file=sys.stderr,
    )
    return 1
  if not VERTEXAI_DATASTORE_ID:
    print(
        "[錯誤] 未設定 VERTEXAI_DATASTORE_ID 環境變數。"
        " 正在結束...",
        file=sys.stderr,
    )
    return 1
  if not ADK_DOCS_ROOT_PATH:
    print(
        "[錯誤] 未設定 ADK_DOCS_ROOT_PATH 環境變數。正在結束...",
        file=sys.stderr,
    )
    return 1
  if not ADK_PYTHON_ROOT_PATH:
    print(
        "[錯誤] 未設定 ADK_PYTHON_ROOT_PATH 環境變數。正在結束...",
        file=sys.stderr,
    )
    return 1

  for gcs_prefix in GCS_PREFIX_TO_ROOT_PATH:
    # 1. 清理 GSC 以便重新開始。
    if not cleanup_gcs_prefix(
        GOOGLE_CLOUD_PROJECT, GCS_BUCKET_NAME, gcs_prefix
    ):
      print("[錯誤] 清理 GCS 失敗。正在結束...", file=sys.stderr)
      return 1

    # 2. 將文件上傳到 GCS。
    if not upload_directory_to_gcs(
        GCS_PREFIX_TO_ROOT_PATH[gcs_prefix],
        GOOGLE_CLOUD_PROJECT,
        GCS_BUCKET_NAME,
        gcs_prefix,
    ):
      print("[錯誤] 將文件上傳到 GCS 失敗。正在結束...", file=sys.stderr)
      return 1

  # 3. 將文件從 GCS 匯入到 Vertex AI Search。
  if not import_from_gcs_to_vertex_ai(VERTEXAI_DATASTORE_ID, GCS_BUCKET_NAME):
    print(
        "[錯誤] 從 GCS 將文件匯入到 Vertex AI Search 失敗。"
        " 正在結束...",
        file=sys.stderr,
    )
    return 1

  print("--- 同步工作已成功啟動 ---")
  return 0


if __name__ == "__main__":
  sys.exit(main())
