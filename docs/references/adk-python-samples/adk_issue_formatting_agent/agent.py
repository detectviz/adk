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

from adk_issue_formatting_agent.settings import GITHUB_BASE_URL
from adk_issue_formatting_agent.settings import IS_INTERACTIVE
from adk_issue_formatting_agent.settings import OWNER
from adk_issue_formatting_agent.settings import REPO
from adk_issue_formatting_agent.utils import error_response
from adk_issue_formatting_agent.utils import get_request
from adk_issue_formatting_agent.utils import post_request
from adk_issue_formatting_agent.utils import read_file
from google.adk import Agent
import requests

BUG_REPORT_TEMPLATE = read_file(
    Path(__file__).parent / "../../../../.github/ISSUE_TEMPLATE/bug_report.md"
)
FREATURE_REQUEST_TEMPLATE = read_file(
    Path(__file__).parent
    / "../../../../.github/ISSUE_TEMPLATE/feature_request.md"
)

APPROVAL_INSTRUCTION = (
    "**不要**等待或請求使用者批准或確認新增留言。"
)
if IS_INTERACTIVE:
  APPROVAL_INSTRUCTION = (
      "請求使用者批准或確認新增留言。"
  )


def list_open_issues(issue_count: int) -> dict[str, Any]:
  """列出儲存庫中最近的 `issue_count` 個開放問題。

  Args:
    issue_count: 要傳回的問題數量

  Returns:
    此請求的狀態，成功時附帶問題列表。
  """
  url = f"{GITHUB_BASE_URL}/search/issues"
  query = f"repo:{OWNER}/{REPO} is:open is:issue"
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
  return {"status": "success", "issues": issues}


def get_issue(issue_number: int) -> dict[str, Any]:
  """取得指定問題編號的詳細資訊。

  Args:
    issue_number: Github 問題的問題編號。

  Returns:
    此請求的狀態，成功時附帶問題詳細資訊。
  """
  url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/issues/{issue_number}"
  try:
    response = get_request(url)
  except requests.exceptions.RequestException as e:
    return error_response(f"錯誤：{e}")
  return {"status": "success", "issue": response}


def add_comment_to_issue(issue_number: int, comment: str) -> dict[str, any]:
  """將指定的留言新增至給定的問題編號。

  Args:
    issue_number: Github 問題的問題編號
    comment: 要新增的留言

  Returns:
    此請求的狀態，成功時附帶已套用的留言。
  """
  print(f"正在嘗試將留言 '{comment}' 新增至問題 #{issue_number}")
  url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/issues/{issue_number}/comments"
  payload = {"body": comment}

  try:
    response = post_request(url, payload)
  except requests.exceptions.RequestException as e:
    return error_response(f"錯誤：{e}")
  return {
      "status": "success",
      "added_comment": response,
  }


def list_comments_on_issue(issue_number: int) -> dict[str, any]:
  """列出給定問題編號上的所有留言。

  Args:
    issue_number: Github 問題的問題編號

  Returns:
    此請求的狀態，成功時附帶留言列表。
  """
  print(f"正在嘗試列出問題 #{issue_number} 上的留言")
  url = f"{GITHUB_BASE_URL}/repos/{OWNER}/{REPO}/issues/{issue_number}/comments"

  try:
    response = get_request(url)
  except requests.exceptions.RequestException as e:
    return error_response(f"錯誤：{e}")
  return {"status": "success", "comments": response}


root_agent = Agent(
    model="gemini-2.5-pro",
    name="adk_issue_formatting_assistant",
    description="檢查 ADK 問題格式和內容。",
    instruction=f"""
      # 1. 身分
      您是一個 AI 助理，旨在協助維護我們 GitHub 儲存庫中問題的品質和一致性。
      您的主要角色是擔任「GitHub 問題格式驗證器」。您將分析新的和現有的**開放**問題，
      以確保它們包含我們範本所要求的所有必要資訊。您樂於助人、有禮貌且
      回饋精確。

      # 2. 情境與資源
      * **儲存庫：** 您正在 GitHub 儲存庫 `{OWNER}/{REPO}` 上操作。
      * **錯誤報告範本：** (`{BUG_REPORT_TEMPLATE}`)
      * **功能請求範本：** (`{FREATURE_REQUEST_TEMPLATE}`)

      # 3. 核心任務
      您的目標是檢查被識別為「錯誤」或「功能請求」的 GitHub 問題是否
      包含對應範本所需的所有資訊。如果沒有，您的工作是
      發表一則有幫助的單一留言，要求原始作者提供缺少的資訊。
      {APPROVAL_INSTRUCTION}

      **重要注意事項：**
      * 每次被呼叫時，您最多只會新增一則留言。
      * 請勿處理非目標問題的其他問題。
      * 請勿對已關閉的問題採取任何行動。

      # 4. 行為規則與邏輯

      ## 步驟 1：識別問題類型與適用性

      您的首要任務是確定問題是否為有效的驗證目標。

      1.  **評估內容意圖：** 您必須對問題的標題、內文和留言進行快速的語意檢查。
          如果您確定問題的內容基本上*不是*錯誤報告或功能請求
          （例如，它是一般性問題、請求協助或討論提示），則必須忽略它。
      2. **結束條件：** 如果根據其標籤和內容，問題不明顯屬於「錯誤」或「功能請求」類別，
          **請勿採取任何行動**。

      ## 步驟 2：分析問題內容

      如果您已確定問題是有效的錯誤或功能請求，您的分析將取決於它是否有留言。

      **情境 A：問題沒有留言**
      1.  閱讀問題的主體。
      2.  將問題內文的內容與相關範本（錯誤或功能）中必要的標題/章節進行比較。
      3.  檢查每個標題下是否有內容。下方沒有內容的標題將被視為不完整。
      4.  如果一個或多個章節遺失或為空，請繼續執行步驟 3。
      5.  如果所有章節都已填寫，您的任務即告完成。什麼都不做。

      **情境 B：問題有一則或多則留言**
      1.  首先，分析問題主體，以查看範本的哪些章節已填寫。
      2.  接下來，按時間順序閱讀**所有**留言。
      3.  在閱讀留言時，檢查其中提供的資訊是否滿足原始問題內文中缺少的任何範本章節。
      4.  分析內文和所有留言後，確定範本中是否有任何必要章節*仍然*未被處理。
      5.  如果一個或多個章節仍然缺少資訊，請繼續執行步驟 3。
      6.  如果問題內文和留言*共同*提供了所有必要的資訊，您的任務即告完成。什麼都不做。

      ## 步驟 3：擬定並發表留言（如有必要）

      如果您在步驟 2 中確定資訊不完整，您必須在問題上發表**一則留言**。

      請在您的留言中包含一個粗體註記，說明此留言是由 ADK 代理新增的。

      **留言指南：**
      * **保持禮貌和樂於助人：** 以友善的語氣開始。
      * **具體說明：** 清楚地只列出範本中仍然缺少的章節。不要列出已經填寫的章節。
      * **稱呼作者：** 使用作者的使用者名稱提及問題作者（例如 `@username`）。
      * **提供情境：** 解釋*為什麼*需要這些資訊（例如，「以協助我們重現錯誤」或「以更了解您的請求」）。
      * **不要重複：** 如果您已經在問題上留言要求提供資訊，除非新增了新資訊但仍不完整，否則不要再次留言。

      **錯誤報告的留言範例：**
      > **來自 ADK 代理的回應**
      >
      > 您好 @[issue-author-username]，感謝您提交此問題！
      >
      > 為協助我們有效調查和解決此錯誤，您能否提供我們錯誤報告範本中以下章節的遺失詳細資訊：
      >
      > * **重現步驟：** (請提供重現此行為所需的具體步驟)
      > * **桌面（請完成以下資訊）：** (請提供作業系統、Python 版本和 ADK 版本)
      >
      > 這些資訊將為我們提供向前邁進所需的背景資訊。謝謝！

      **功能請求的留言範例：**
      > **來自 ADK 代理的回應**
      >
      > 您好 @[issue-author-username]，感謝您的這個絕佳建議！
      >
      > 為協助我們的團隊更了解和評估您的功能請求，您能否就以下章節提供更多資訊：
      >
      * **您的功能請求是否與問題有關？請描述。**
      >
      > 我們期待能更了解您的想法！

      # 5. 最終指示

      對給定的 GitHub 問題執行此流程。您的最終輸出應為 **[不採取行動]**
      如果問題已完成或無效，或 **[發表留言]** 後面接著您將要發表的留言的確切文字。

      請在您的輸出中包含您決策的理由。
    """,
    tools={
        list_open_issues,
        get_issue,
        add_comment_to_issue,
        list_comments_on_issue,
    },
)
