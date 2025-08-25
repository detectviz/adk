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

"""測試學術研究代理在代理引擎上的部署。"""

import os

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines

# 定義命令列旗標
FLAGS = flags.FLAGS

flags.DEFINE_string("project_id", None, "GCP 專案 ID。")
flags.DEFINE_string("location", None, "GCP 位置。")
flags.DEFINE_string("bucket", None, "GCP 儲存桶。")
flags.DEFINE_string(
    "resource_id",
    None,
    "ReasoningEngine 資源 ID（部署代理後返回）",
)
flags.DEFINE_string("user_id", None, "使用者 ID（可以是任何字串）。")
# 將 resource_id 和 user_id 標記為必要旗標
flags.mark_flag_as_required("resource_id")
flags.mark_flag_as_required("user_id")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument
    """腳本主函式。"""
    # 從 .env 檔案載入環境變數
    load_dotenv()

    # 從旗標或環境變數中獲取 GCP 設定
    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    bucket = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
    )

    # 檢查是否已設定必要的環境變數
    if not project_id:
        print("缺少必要的環境變數：GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("缺少必要的環境變數：GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print(
            "缺少必要的環境變數：GOOGLE_CLOUD_STORAGE_BUCKET"
        )
        return

    # 初始化 Vertex AI
    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    # 獲取已部署的代理
    agent = agent_engines.get(FLAGS.resource_id)
    print(f"找到具有資源 ID 的代理：{FLAGS.resource_id}")
    # 為指定的使用者 ID 建立一個新的對話工作階段
    session = agent.create_session(user_id=FLAGS.user_id)
    print(f"為使用者 ID 建立的工作階段：{FLAGS.user_id}")
    print("輸入 'quit' 以退出。")
    # 進入與代理互動的迴圈
    while True:
        user_input = input("輸入：")
        if user_input == "quit":
            break

        # 將使用者輸入串流查詢到代理並處理回應
        for event in agent.stream_query(
            user_id=FLAGS.user_id, session_id=session["id"], message=user_input
        ):
            if "content" in event:
                if "parts" in event["content"]:
                    parts = event["content"]["parts"]
                    for part in parts:
                        if "text" in part:
                            text_part = part["text"]
                            print(f"回應：{text_part}")

    # 刪除對話工作階段
    agent.delete_session(user_id=FLAGS.user_id, session_id=session["id"])
    print(f"已為使用者 ID 刪除工作階段：{FLAGS.user_id}")


if __name__ == "__main__":
    app.run(main)
