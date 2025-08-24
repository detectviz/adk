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

from typing import Any

from adk_triaging_agent.settings import BOT_LABEL
from adk_triaging_agent.settings import GITHUB_BASE_URL
from adk_triaging_agent.settings import IS_INTERACTIVE
from adk_triaging_agent.settings import OWNER
from adk_triaging_agent.settings import REPO
from adk_triaging_agent.utils import error_response
from adk_triaging_agent.utils import get_request
from adk_triaging_agent.utils import patch_request
from adk_triaging_agent.utils import post_request
from google.adk.agents.llm_agent import Agent
import requests

LABEL_TO_OWNER = {
    "agent engine": "yeesian",
    "documentation": "polong-lin",
    "services": "DeanChensj",
    "question": "",
    "mcp": "seanzhou1023",
    "tools": "seanzhou1023",
    "eval": "ankursharmas",
    "live": "hangfei",
    "models": "genquan9",
    "tracing": "Jacksunwei",
    "core": "Jacksunwei",
    "web": "wyf7107",
}

APPROVAL_INSTRUCTION = (
    "不要要求使用者批准標記！如果您找不到適合問題的"
    "標籤，請不要標記它。"
)
if IS_INTERACTIVE:
  APPROVAL_INSTRUCTION = "只有在使用者批准標記時才標記它們！"


def list_unlabeled_issues(issue_count: int) -> dict[str, Any]:
  """列出儲存庫中最近的 `issue_count` 個未標記問題。

  Args:
    issue_count: 要傳回的問題數量

  Returns:
    此請求的狀態，成功時附帶問題列表。
  """
  url = f"{GITHUB_BASE_URL}/search/issues"
  query = f"repo:{OWNER}/{REPO} is:open is:issue no:label"
  params = {
      "q": query,
      "sort": "created",
      "order": "desc",
      "per_page": issue_count,
      "page": 1,
  }

  try:
    response = get_request(url, params)
  except requests.exceptions.RequestException as e:
    return error_response(f"錯誤：{e}")
  issues = response.get("items", None)

  unlabeled_issues = []
  for issue in issues:
    if not issue.get("labels", None):
      unlabeled_issues.append(issue)
  return {"status": "success", "issues": unlabeled_issues}


def add_label_and_owner_to_issue(
    issue_number: int, label: str
) -> dict[str, Any]:
  """將指定的標籤和擁有者新增至給定的問題編號。

  Args:
    issue_number: Github 問題的問題編號。
    label: 要指派的標籤

  Returns:
    此請求的狀態，成功時附帶已套用的標籤和指派的擁有者。
  """
  print(f"正在嘗試將標籤 '{label}' 新增至問題 #{issue_number}")
  if label not in LABEL_TO_OWNER:
    return error_response(
        f"錯誤：標籤 '{label}' 不是允許的標籤。將不予套用。"
    )

  label_url = (
      f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/issues/{issue_number}/labels"
  )
  label_payload = [label, BOT_LABEL]

  try:
    response = post_request(label_url, label_payload)
  except requests.exceptions.RequestException as e:
    return error_response(f"錯誤：{e}")

  owner = LABEL_TO_OWNER.get(label, None)
  if not owner:
    return {
        "status": "warning",
        "message": (
            f"{response}\n\n標籤 '{label}' 沒有擁有者。將不"
            "指派。"
        ),
        "applied_label": label,
    }

  assignee_url = (
      f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/issues/{issue_number}/assignees"
  )
  assignee_payload = {"assignees": [owner]}

  try:
    response = post_request(assignee_url, assignee_payload)
  except requests.exceptions.RequestException as e:
    return error_response(f"錯誤：{e}")

  return {
      "status": "success",
      "message": response,
      "applied_label": label,
      "assigned_owner": owner,
  }


def change_issue_type(issue_number: int, issue_type: str) -> dict[str, Any]:
  """變更給定問題編號的問題類型。

  Args:
    issue_number: Github 問題的問題編號，字串格式。
    issue_type: 要指派的問題類型

  Returns:
    此請求的狀態，成功時附帶已套用的問題類型。
  """
  print(
      f"正在嘗試將問題類型 '{issue_type}' 變更為問題 #{issue_number}"
  )
  url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/issues/{issue_number}"
  payload = {"type": issue_type}

  try:
    response = patch_request(url, payload)
  except requests.exceptions.RequestException as e:
    return error_response(f"錯誤：{e}")

  return {"status": "success", "message": response, "issue_type": issue_type}


root_agent = Agent(
    model="gemini-2.5-pro",
    name="adk_triaging_assistant",
    description="對 ADK 問題進行分類。",
    instruction=f"""
      您是 Github {REPO} 儲存庫（擁有者為 {OWNER}）的分類機器人。您將協助取得問題並建議標籤。
      重要事項：{APPROVAL_INSTRUCTION}

      以下是標記規則：
      - 如果使用者詢問與文件相關的問題，請標記為 "documentation"。
      - 如果與 session、memory 服務有關，請標記為 "services"
      - 如果與 UI/web 有關，請標記為 "web"
      - 如果使用者提出問題，請標記為 "question"
      - 如果與工具有關，請標記為 "tools"
      - 如果與代理評估有關，則標記為 "eval"。
      - 如果與串流/即時有關，請標記為 "live"。
      - 如果與模型支援（非 Gemini，如 Litellm、Ollama、OpenAI 模型）有關，請標記為 "models"。
      - 如果與追蹤有關，請標記為 "tracing"。
      - 如果是代理協調、代理定義，請標記為 "core"。
      - 如果與代理引擎有關，請標記為 "agent engine"。
      - 如果與模型內容協定（例如 MCP 工具、MCP 工具集、MCP 會話管理等）有關，請標記為 "mcp"。
      - 如果您找不到適合問題的標籤，請遵循以「重要事項：」開頭的先前指示。

      呼叫 `add_label_and_owner_to_issue` 工具為問題加上標籤，這也會將問題指派給標籤的擁有者。

      為問題加上標籤後，呼叫 `change_issue_type` 工具以變更問題類型：
      - 如果問題是錯誤報告，請將問題類型變更為「錯誤」。
      - 如果問題是功能請求，請將問題類型變更為「功能」。
      - 否則，**請勿變更問題類型**。

      以易於閱讀的格式呈現以下內容，並突顯問題編號和您的標籤。
      - 幾句話的問題摘要
      - 您的標籤建議和理由
      - 如果您將問題指派給擁有者，則為標籤的擁有者
    """,
    tools=[
        list_unlabeled_issues,
        add_label_and_owner_to_issue,
        change_issue_type,
    ],
)
