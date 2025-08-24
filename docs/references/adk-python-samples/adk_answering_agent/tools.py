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
from typing import Dict
from typing import Optional

from adk_answering_agent.settings import OWNER
from adk_answering_agent.settings import REPO
from adk_answering_agent.utils import convert_gcs_to_https
from adk_answering_agent.utils import error_response
from adk_answering_agent.utils import run_graphql_query
import requests


def get_discussion_and_comments(discussion_number: int) -> dict[str, Any]:
  """使用 GitHub GraphQL API 取得討論及其留言。

  Args:
      discussion_number: GitHub 討論的編號。

  Returns:
      一個包含請求狀態和討論詳細資訊的字典。
  """
  print(f"正在嘗試取得討論 #{discussion_number} 及其留言")
  query = """
        query($owner: String!, $repo: String!, $discussionNumber: Int!) {
          repository(owner: $owner, name: $repo) {
            discussion(number: $discussionNumber) {
              id
              title
              body
              createdAt
              closed
              author {
                login
              }
              # 對於每個討論，取得最新的 20 個標籤。
              labels(last: 20) {
                nodes {
                  id
                  name
                }
              }
              # 對於每個討論，取得最新的 100 則留言。
              comments(last: 100) {
                nodes {
                  id
                  body
                  createdAt
                  author {
                    login
                  }
                  # 對於每個討論，取得最新的 50 則回覆
                  replies(last: 50) {
                    nodes {
                      id
                      body
                      createdAt
                      author {
                        login
                      }
                    }
                  }
                }
              }
            }
          }
        }
    """
  variables = {
      "owner": OWNER,
      "repo": REPO,
      "discussionNumber": discussion_number,
  }
  try:
    response = run_graphql_query(query, variables)
    if "errors" in response:
      return error_response(str(response["errors"]))
    discussion_data = (
        response.get("data", {}).get("repository", {}).get("discussion")
    )
    if not discussion_data:
      return error_response(f"找不到討論 #{discussion_number}。")
    return {"status": "success", "discussion": discussion_data}
  except requests.exceptions.RequestException as e:
    return error_response(str(e))


def add_comment_to_discussion(
    discussion_id: str, comment_body: str
) -> dict[str, Any]:
  """將留言新增至特定討論。

  Args:
      discussion_id: 討論的 GraphQL 節點 ID。
      comment_body: 留言的 Markdown 內容。

  Returns:
      請求的狀態和新留言的詳細資訊。
  """
  print(f"正在將留言新增至討論 {discussion_id}")
  query = """
        mutation($discussionId: ID!, $body: String!) {
          addDiscussionComment(input: {discussionId: $discussionId, body: $body}) {
            comment {
              id
              body
              createdAt
              author {
                login
              }
            }
          }
        }
    """
  if not comment_body.startswith("**來自 ADK 問答代理的回應"):
    comment_body = (
        "**來自 ADK 問答代理的回應 (實驗性，答案可能不準確)**\n\n"
        + comment_body
    )

  variables = {"discussionId": discussion_id, "body": comment_body}
  try:
    response = run_graphql_query(query, variables)
    if "errors" in response:
      return error_response(str(response["errors"]))
    new_comment = (
        response.get("data", {}).get("addDiscussionComment", {}).get("comment")
    )
    return {"status": "success", "comment": new_comment}
  except requests.exceptions.RequestException as e:
    return error_response(str(e))


def get_label_id(label_name: str) -> str | None:
  """輔助函式，用於尋找給定標籤名稱的 GraphQL 節點 ID。"""
  print(f"正在尋找標籤 '{label_name}' 的 ID...")
  query = """
    query($owner: String!, $repo: String!, $labelName: String!) {
      repository(owner: $owner, name: $repo) {
        label(name: $labelName) {
          id
        }
      }
    }
    """
  variables = {"owner": OWNER, "repo": REPO, "labelName": label_name}

  try:
    response = run_graphql_query(query, variables)
    if "errors" in response:
      print(
          f"[警告] 來自 GitHub API 對於標籤 '{label_name}' 的回應錯誤："
          f" {response['errors']}"
      )
      return None
    label_info = response["data"].get("repository", {}).get("label")
    if label_info:
      return label_info.get("id")
    print(f"[警告] 找不到標籤 '{label_name}' 的資訊。")
    return None
  except requests.exceptions.RequestException as e:
    print(f"[警告] 來自 GitHub API 的錯誤：{e}")
    return None


def add_label_to_discussion(
    discussion_id: str, label_name: str
) -> dict[str, Any]:
  """將標籤新增至特定討論。

  Args:
      discussion_id: 討論的 GraphQL 節點 ID。
      label_name: 要新增的標籤名稱（例如 "bug"）。

  Returns:
      請求的狀態和標籤詳細資訊。
  """
  print(
      f"正在嘗試將標籤 '{label_name}' 新增至討論 {discussion_id}..."
  )
  # 首先，透過其名稱取得標籤的 GraphQL ID
  label_id = get_label_id(label_name)
  if not label_id:
    return error_response(f"找不到標籤 '{label_name}'。")

  # 然後，執行突變以將標籤新增至討論
  mutation = """
    mutation AddLabel($discussionId: ID!, $labelId: ID!) {
      addLabelsToLabelable(input: {labelableId: $discussionId, labelIds: [$labelId]}) {
        clientMutationId
      }
    }
    """
  variables = {"discussionId": discussion_id, "labelId": label_id}
  try:
    response = run_graphql_query(mutation, variables)
    if "errors" in response:
      return error_response(str(response["errors"]))
    return {"status": "success", "label_id": label_id, "label_name": label_name}
  except requests.exceptions.RequestException as e:
    return error_response(str(e))


def convert_gcs_links_to_https(gcs_uris: list[str]) -> Dict[str, Optional[str]]:
  """將 GCS 檔案連結轉換為可公開存取的 HTTPS 連結。

  Args:
      gcs_uris: GCS 檔案連結列表，格式為
        'gs://bucket_name/prefix/relative_path'。

  Returns:
      一個將原始 GCS 檔案連結對應到轉換後的 HTTPS
      連結的字典。如果 GCS 連結無效，字典中對應的值
      將為 None。
  """
  return {gcs_uri: convert_gcs_to_https(gcs_uri) for gcs_uri in gcs_uris}
