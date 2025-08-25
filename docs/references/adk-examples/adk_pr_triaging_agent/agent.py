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

from pathlib import Path
from typing import Any

from adk_pr_triaging_agent.settings import BOT_LABEL
from adk_pr_triaging_agent.settings import GITHUB_BASE_URL
from adk_pr_triaging_agent.settings import IS_INTERACTIVE
from adk_pr_triaging_agent.settings import OWNER
from adk_pr_triaging_agent.settings import REPO
from adk_pr_triaging_agent.utils import error_response
from adk_pr_triaging_agent.utils import get_diff
from adk_pr_triaging_agent.utils import post_request
from adk_pr_triaging_agent.utils import read_file
from adk_pr_triaging_agent.utils import run_graphql_query
from google.adk import Agent
import requests

LABEL_TO_OWNER = {
    "documentation": "polong-lin",
    "services": "DeanChensj",
    "tools": "seanzhou1023",
    "mcp": "seanzhou1023",
    "eval": "ankursharmas",
    "live": "hangfei",
    "models": "genquan9",
    "tracing": "Jacksunwei",
    "core": "Jacksunwei",
    "web": "wyf7107",
}

CONTRIBUTING_MD = read_file(
    Path(__file__).resolve().parents[3] / "CONTRIBUTING.md"
)

APPROVAL_INSTRUCTION = (
    "不要要求使用者批准標記或評論！如果您找不到"
    "適合 PR 的標籤，請不要標記它。"
)
if IS_INTERACTIVE:
  APPROVAL_INSTRUCTION = (
      "只有在使用者批准標記或評論時才進行標記或評論！"
  )


def get_pull_request_details(pr_number: int) -> str:
  """取得指定拉取請求的詳細資訊。

  Args:
    pr_number: Github 拉取請求的編號。

  Returns:
    此請求的狀態，成功時附帶詳細資訊。
  """
  print(f"正在從 {OWNER}/{REPO} 取得 PR #{pr_number} 的詳細資訊")
  query = """
    query($owner: String!, $repo: String!, $prNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $prNumber) {
          id
          title
          body
          author {
            login
          }
          labels(last: 10) {
            nodes {
              name
            }
          }
          files(last: 50) {
            nodes {
              path
            }
          }
          comments(last: 50) {
            nodes {
              id
              body
              createdAt
              author {
                login
              }
            }
          }
          commits(last: 50) {
            nodes {
              commit {
                url
                message
              }
            }
          }
          statusCheckRollup {
            state
            contexts(last: 20) {
              nodes {
                ... on StatusContext {
                  context
                  state
                  targetUrl
                }
                ... on CheckRun {
                  name
                  status
                  conclusion
                  detailsUrl
                }
              }
            }
          }
        }
      }
    }
  """
  variables = {"owner": OWNER, "repo": REPO, "prNumber": pr_number}
  url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/pulls/{pr_number}"

  try:
    response = run_graphql_query(query, variables)
    if "errors" in response:
      return error_response(str(response["errors"]))

    pr = response.get("data", {}).get("repository", {}).get("pullRequest")
    if not pr:
      return error_response(f"找不到拉取請求 #{pr_number}。")

    # 過濾掉主要的合併提交。
    original_commits = pr.get("commits", {}).get("nodes", {})
    if original_commits:
      filtered_commits = [
          commit_node
          for commit_node in original_commits
          if not commit_node["commit"]["message"].startswith(
              "Merge branch 'main' into"
          )
      ]
      pr["commits"]["nodes"] = filtered_commits

    # 取得 PR 的差異並截斷它以避免超過最大權杖數。
    pr["diff"] = get_diff(url)[:10000]

    return {"status": "success", "pull_request": pr}
  except requests.exceptions.RequestException as e:
    return error_response(str(e))


def add_label_and_reviewer_to_pr(pr_number: int, label: str) -> dict[str, Any]:
  """在 PR 上新增指定的標籤並向對應的審核者請求審核。

  Args:
      pr_number: Github 拉取請求的編號
      label: 要新增的標籤

  Returns:
      此請求的狀態，成功時附帶已套用的標籤和指派的
      審核者。
  """
  print(f"正在嘗試將標籤 '{label}' 和審核者新增至 PR #{pr_number}")
  if label not in LABEL_TO_OWNER:
    return error_response(
        f"錯誤：標籤 '{label}' 不是允許的標籤。將不予套用。"
    )

  # 拉取請求在 Github 中是一個特殊的問題，所以我們可以使用問題的 url 來處理 PR。
  label_url = (
      f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/issues/{pr_number}/labels"
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
  reviewer_url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/pulls/{pr_number}/requested_reviewers"
  reviewer_payload = {"reviewers": [owner]}
  try:
    post_request(reviewer_url, reviewer_payload)
  except requests.exceptions.RequestException as e:
    return {
        "status": "warning",
        "message": f"未指派審核者：{e}",
        "applied_label": label,
    }

  return {
      "status": "success",
      "applied_label": label,
      "assigned_reviewer": owner,
  }


def add_comment_to_pr(pr_number: int, comment: str) -> dict[str, Any]:
  """將指定的留言新增至給定的 PR 編號。

  Args:
    pr_number: Github 拉取請求的編號
    comment: 要新增的留言

  Returns:
    此請求的狀態，成功時附帶已套用的留言。
  """
  print(f"正在嘗試將留言 '{comment}' 新增至問題 #{pr_number}")

  # 拉取請求在 Github 中是一個特殊的問題，所以我們可以使用問題的 url 來處理 PR。
  url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/issues/{pr_number}/comments"
  payload = {"body": comment}

  try:
    post_request(url, payload)
  except requests.exceptions.RequestException as e:
    return error_response(f"錯誤：{e}")
  return {
      "status": "success",
      "added_comment": comment,
  }


root_agent = Agent(
    model="gemini-2.5-pro",
    name="adk_pr_triaging_assistant",
    description="對 ADK 拉取請求進行分類。",
    instruction=f"""
      # 1. 身分
      您是 Github {REPO} 儲存庫（擁有者為 {OWNER}）的拉取請求 (PR) 分類機器人。

      # 2. 職責
      您的核心職責包括：
      - 取得拉取請求的詳細資訊。
      - 為拉取請求新增標籤。
      - 為拉取請求指派審核者。
      - 檢查拉取請求是否遵循貢獻指南。
      - 如果拉取請求未遵循指南，則新增留言。

      **重要事項：{APPROVAL_INSTRUCTION}**

      # 3. 指南與規則
      以下是標記規則：
      - 如果 PR 與文件有關，請標記為 "documentation"。
      - 如果與 session、memory、artifacts 服務有關，請標記為 "services"
      - 如果與 UI/web 有關，請標記為 "web"
      - 如果與工具有關，請標記為 "tools"
      - 如果與代理評估有關，則標記為 "eval"。
      - 如果與串流/即時有關，請標記為 "live"。
      - 如果與模型支援（非 Gemini，如 Litellm、Ollama、OpenAI 模型）有關，請標記為 "models"。
      - 如果與追蹤有關，請標記為 "tracing"。
      - 如果是代理協調、代理定義，請標記為 "core"。
      - 如果與模型內容協定（例如 MCP 工具、MCP 工具集、MCP 會話管理等）有關，請標記為 "mcp"。
      - 如果您找不到適合 PR 的標籤，請遵循以「重要事項：」開頭的先前指示。

      以下是貢獻指南：
      `{CONTRIBUTING_MD}`

      以下是檢查 PR 是否遵循指南的準則：
      - 拉取請求詳細資訊中的 "statusCheckRollup" 可協助您判斷 PR 是否遵循某些指南（例如 CLA 合規性）。

      以下是留言的指南：
      - **保持禮貌和樂於助人：** 以友善的語氣開始。
      - **具體說明：** 清楚地只列出貢獻指南中仍然缺少的章節。
      - **稱呼作者：** 使用 PR 作者的使用者名稱提及他們（例如 `@username`）。
      - **提供情境：** 解釋*為什麼*需要這些資訊或操作。
      - **不要重複：** 如果您已經在 PR 上留言要求提供資訊，除非新增了新資訊但仍不完整，否則不要再次留言。
      - **表明身分：** 在您的留言中包含一個粗體註記（例如「來自 ADK 分類代理的回應」），以表明此留言是由 ADK 問答代理新增的。

      **PR 的留言範例：**
      > **來自 ADK 分類代理的回應**
      >
      > 您好 @[pr-author-username]，感謝您建立此 PR！
      >
      > 此 PR 是一個錯誤修復，您能否將 github 問題與此 PR 關聯？如果沒有現有問題，您能否建立一個？
      >
      > 此外，您能否在套用修復後提供日誌或螢幕截圖？
      >
      > 這些資訊將有助於審核者更有效地審核您的 PR。謝謝！

      # 4. 步驟
      當您收到一個 PR 時，應採取以下步驟：
      - 呼叫 `get_pull_request_details` 工具以取得 PR 的詳細資訊。
      - 如果 PR 已關閉或標有「{BOT_LABEL}」或「google-contributior」，請略過該 PR（即不標記或評論）。
      - 檢查 PR 是否遵循貢獻指南。
        - 如果未遵循指南，請建議或在 PR 中新增一則留言，指向貢獻指南 (https://github.com/google/adk-python/blob/main/CONTRIBUTING.md)。
        - 如果遵循指南，請建議或為 PR 新增標籤。

      # 5. 輸出
      以易於閱讀的格式呈現以下內容，並突顯 PR 編號和您的標籤。
      - 幾句話的 PR 摘要
      - 您建議或新增的標籤及其理由
      - 如果您為 PR 指派了審核者，則為標籤的擁有者
      - 您建議或新增至 PR 的留言及其理由
    """,
    tools=[
        get_pull_request_details,
        add_label_and_reviewer_to_pr,
        add_comment_to_pr,
    ],
)
