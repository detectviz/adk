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

# pylint: disable=g-importing-member

import os

from google.adk import Agent
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
if not GITHUB_TOKEN:
  raise ValueError("未設定 GITHUB_TOKEN 環境變數")

OWNER = os.getenv("OWNER", "google")
REPO = os.getenv("REPO", "adk-python")


def get_github_pr_info_http(pr_number: int) -> str | None:
  """透過傳送直接的 HTTP 請求來取得 GitHub 拉取請求的資訊。

  Args:
      pr_number (int): 拉取請求的編號。

  Returns:
      pr_message: 一個字串。
  """
  base_url = "https://api.github.com"

  headers = {
      "Accept": "application/vnd.github+json",
      "Authorization": f"Bearer {GITHUB_TOKEN}",
      "X-GitHub-Api-Version": "2022-11-28",
  }

  pr_message = ""

  # --- 1. 取得主要的 PR 詳細資訊 ---
  pr_url = f"{base_url}/repos/{OWNER}/{REPO}/pulls/{pr_number}"
  print(f"正在從以下網址取得 PR 詳細資訊：{pr_url}")
  try:
    response = requests.get(pr_url, headers=headers)
    response.raise_for_status()
    pr_data = response.json()
    pr_message += f"PR 標題為：{pr_data.get('title')}\n"
  except requests.exceptions.HTTPError as e:
    print(
        f"取得 PR 詳細資訊時發生 HTTP 錯誤：{e.response.status_code} - "
        f" {e.response.text}"
    )
    return None
  except requests.exceptions.RequestException as e:
    print(f"取得 PR 詳細資訊時發生網路或請求錯誤：{e}")
    return None
  except Exception as e:  # pylint: disable=broad-except
    print(f"發生未預期的錯誤：{e}")
    return None

  # --- 2. 取得相關的提交 (分頁) ---
  commits_url = pr_data.get(
      "commits_url"
  )  # 此 URL 在初始 PR 回應中提供
  if commits_url:
    print("\n--- 此 PR 中的相關提交：---")
    page = 1
    while True:
      # GitHub API 通常使用 'per_page' 和 'page' 進行分頁
      params = {
          "per_page": 100,
          "page": page,
      }  # 每頁最多取得 100 個提交
      try:
        response = requests.get(commits_url, headers=headers, params=params)
        response.raise_for_status()
        commits_data = response.json()

        if not commits_data:  # 沒有更多提交
          break

        pr_message += "相關的提交為：\n"
        for commit in commits_data:
          message = commit.get("commit", {}).get("message", "").splitlines()[0]
          if message:
            pr_message += message + "\n"

        # 檢查 'Link' 標頭以確定是否存在更多頁面
        # 這是 GitHub API 指示分頁的方式
        if "Link" in response.headers:
          link_header = response.headers["Link"]
          if 'rel="next"' in link_header:
            page += 1  # 前往下一頁
          else:
            break  # 沒有更多頁面
        else:
          break  # 沒有 Link 標頭，所以可能只有一頁

      except requests.exceptions.HTTPError as e:
        print(
            f"取得 PR 提交時發生 HTTP 錯誤 (第 {page} 頁)："
            f" {e.response.status_code} - {e.response.text}"
        )
        break
      except requests.exceptions.RequestException as e:
        print(
            f"取得 PR 提交時發生網路或請求錯誤 (第 {page} 頁)：{e}"
        )
        break
  else:
    print("在 PR 資料中找不到提交 URL。")

  return pr_message


system_prompt = """
您是一位樂於助人的助理，能為軟體工程師產生合理的拉取請求描述。

描述不應太短（例如：少於 3 個字），也不應太長（例如：超過 30 個字）。

產生的描述應以 `chore`、`docs`、`feat`、`fix`、`test` 或 `refactor` 開頭。
`feat` 代表新功能。
`fix` 代表錯誤修復。
`chore`、`docs`、`test` 和 `refactor` 代表改進。

一些好的描述範例如下：
1. feat: 為本地評估集管理器新增 `get_eval_case`、`update_eval_case` 和 `delete_eval_case` 的實作。
2. feat: 提供 `inject_session_state` 作為公用程式方法。

一些不好的描述範例如下：
1. fix: 這修復了錯誤。
2. feat: 這是一個新功能。

"""

root_agent = Agent(
    model="gemini-2.0-flash",
    name="github_pr_agent",
    description="為 ADK 產生拉取請求描述。",
    instruction=system_prompt,
)
