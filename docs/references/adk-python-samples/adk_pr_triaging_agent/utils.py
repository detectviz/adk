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

import sys
from typing import Any

from adk_pr_triaging_agent.settings import GITHUB_GRAPHQL_URL
from adk_pr_triaging_agent.settings import GITHUB_TOKEN
from google.adk.agents.run_config import RunConfig
from google.adk.runners import Runner
from google.genai import types
import requests

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

diff_headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3.diff",
}


def run_graphql_query(query: str, variables: dict[str, Any]) -> dict[str, Any]:
  """執行 GraphQL 查詢。"""
  payload = {"query": query, "variables": variables}
  response = requests.post(
      GITHUB_GRAPHQL_URL, headers=headers, json=payload, timeout=60
  )
  response.raise_for_status()
  return response.json()


def get_request(url: str, params: dict[str, Any] | None = None) -> Any:
  """執行 GET 請求。"""
  if params is None:
    params = {}
  response = requests.get(url, headers=headers, params=params, timeout=60)
  response.raise_for_status()
  return response.json()


def get_diff(url: str) -> str:
  """執行 GET 請求以取得差異。"""
  response = requests.get(url, headers=diff_headers)
  response.raise_for_status()
  return response.text


def post_request(url: str, payload: Any) -> dict[str, Any]:
  """執行 POST 請求。"""
  response = requests.post(url, headers=headers, json=payload, timeout=60)
  response.raise_for_status()
  return response.json()


def error_response(error_message: str) -> dict[str, Any]:
  """傳回錯誤回應。"""
  return {"status": "error", "error_message": error_message}


def read_file(file_path: str) -> str:
  """讀取給定檔案的內容。"""
  try:
    with open(file_path, "r") as f:
      return f.read()
  except FileNotFoundError:
    print(f"錯誤：找不到檔案：{file_path}。")
    return ""


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
