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
from typing import Any
from typing import Optional
from urllib.parse import urljoin

from adk_answering_agent.settings import GITHUB_GRAPHQL_URL
from adk_answering_agent.settings import GITHUB_TOKEN
from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.genai import types
import requests

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


def error_response(error_message: str) -> dict[str, Any]:
  return {"status": "error", "error_message": error_message}


def run_graphql_query(query: str, variables: dict[str, Any]) -> dict[str, Any]:
  """執行 GraphQL 查詢。"""
  payload = {"query": query, "variables": variables}
  response = requests.post(
      GITHUB_GRAPHQL_URL, headers=headers, json=payload, timeout=60
  )
  response.raise_for_status()
  return response.json()


def parse_number_string(number_str: str | None, default_value: int = 0) -> int:
  """從給定的字串中解析數字。"""
  if not number_str:
    return default_value

  try:
    return int(number_str)
  except ValueError:
    print(
        f"警告：無效的數字字串：{number_str}。將使用預設值"
        f" {default_value}。",
        file=sys.stderr,
    )
    return default_value


def _check_url_exists(url: str) -> bool:
  """檢查 URL 是否存在且可存取。"""
  try:
    # 設定超時以防止程式無限期等待。
    # allow_redirects=True 確保我們在重新導向後能正確處理有效的連結。
    response = requests.head(url, timeout=5, allow_redirects=True)
    # 狀態碼 2xx (成功) 或 3xx (重新導向) 被視為有效。
    return response.ok
  except requests.RequestException:
    # 捕捉 requests 函式庫所有可能的例外
    # (例如連線錯誤、超時)。
    return False


def _generate_github_url(repo_name: str, relative_path: str) -> str:
  """為儲存庫檔案產生標準的 GitHub URL。"""
  return f"https://github.com/google/{repo_name}/blob/main/{relative_path}"


def convert_gcs_to_https(gcs_uri: str) -> Optional[str]:
  """將 GCS 檔案連結轉換為可公開存取的 HTTPS 連結。

  Args:
      gcs_uri: Google Cloud Storage 連結，格式為
        'gs://bucket_name/prefix/relative_path'。

  Returns:
      轉換後的 HTTPS 連結字串，如果輸入格式不正確則為 None。
  """
  # 解析 GCS 連結
  if not gcs_uri or not gcs_uri.startswith("gs://"):
    print(f"錯誤：無效的 GCS 連結格式：{gcs_uri}")
    return None

  try:
    # 去除 'gs://' 並以 '/' 分割，至少需要 3 個部分
    # (儲存桶、前綴、路徑)
    parts = gcs_uri[5:].split("/", 2)
    if len(parts) < 3:
      raise ValueError(
          "GCS 連結必須包含儲存桶、前綴和相對路徑。"
      )

    _, prefix, relative_path = parts
  except (ValueError, IndexError) as e:
    print(f"錯誤：解析 GCS 連結 '{gcs_uri}' 失敗：{e}")
    return None

  # 將 .html 替換為 .md
  if relative_path.endswith(".html"):
    relative_path = relative_path.removesuffix(".html") + ".md"

  # 轉換 adk-docs 的連結
  if prefix == "adk-docs" and relative_path.startswith("docs/"):
    path_after_docs = relative_path[len("docs/") :]
    if not path_after_docs.endswith(".md"):
      # 使用常規的 github url
      return _generate_github_url(prefix, relative_path)

    base_url = "https://google.github.io/adk-docs/"
    if os.path.basename(path_after_docs) == "index.md":
      # 如果是索引檔案，則使用目錄路徑
      final_path_segment = os.path.dirname(path_after_docs)
    else:
      # 否則，使用不含副檔名的檔案名稱
      final_path_segment = path_after_docs.removesuffix(".md")

    if final_path_segment and not final_path_segment.endswith("/"):
      final_path_segment += "/"

    potential_url = urljoin(base_url, final_path_segment)

    # 檢查產生的連結是否存在
    if _check_url_exists(potential_url):
      return potential_url
    else:
      # 如果不存在，則退回使用常規的 github url
      return _generate_github_url(prefix, relative_path)

  # 轉換其他情況的連結，例如 adk-python
  else:
    return _generate_github_url(prefix, relative_path)


async def call_agent_async(
    runner: Runner, user_id: str, session_id: str, prompt: str
) -> str:
  """使用使用者的提示非同步呼叫代理。"""
  content = types.Content(
      role="user", parts=[types.Part.from_text(text=prompt)]
  )

  final_response_text = ""
  async for event in runner.run_async(
      user_id=user_id,
      session_id=session_id,
      new_message=content,
      run_config=RunConfig(save_input_blobs_as_artifacts=False),
  ):
    if event.content and event.content.parts:
      if text := "".join(part.text or "" for part in event.content.parts):
        if event.author != "user":
          final_response_text += text

  return final_response_text
