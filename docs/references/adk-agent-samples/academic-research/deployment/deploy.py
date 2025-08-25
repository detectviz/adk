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

"""學術研究的部署腳本"""


import os

import vertexai
from absl import app, flags
from academic_research.agent import root_agent
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# 定義命令列旗標
FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP 專案 ID。")
flags.DEFINE_string("location", None, "GCP 位置。")
flags.DEFINE_string("bucket", None, "GCP 儲存桶。")
flags.DEFINE_string("resource_id", None, "ReasoningEngine 資源 ID。")

# 定義互斥的命令列旗標，用於指定操作
flags.DEFINE_bool("list", False, "列出所有代理。")
flags.DEFINE_bool("create", False, "建立一個新代理。")
flags.DEFINE_bool("delete", False, "刪除一個現有代理。")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete", "list"])


def create() -> None:
    """為學術研究建立一個代理引擎。"""
    # 使用 AdkApp 包裝根代理
    adk_app = AdkApp(agent=root_agent, enable_tracing=True)

    # 建立遠端代理
    remote_agent = agent_engines.create(
        adk_app,
        display_name=root_agent.name,
        # 指定代理執行所需的 Python 套件
        requirements=[
            "google-adk (>=0.0.2)",
            "google-cloud-aiplatform[agent_engines] (>=1.91.0,!=1.92.0)",
            "google-genai (>=1.5.0,<2.0.0)",
            "pydantic (>=2.10.6,<3.0.0)",
            "absl-py (>=2.2.1,<3.0.0)",
        ],
        #        extra_packages=[""],
    )
    print(f"已建立遠端代理：{remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """刪除指定的代理引擎。"""
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"已刪除遠端代理：{resource_id}")


def list_agents() -> None:
    """列出所有可用的代理引擎。"""
    remote_agents = agent_engines.list()
    template = """
{agent.name} ("{agent.display_name}")
- 建立時間：{agent.create_time}
- 更新時間：{agent.update_time}
"""
    remote_agents_string = "\n".join(
        template.format(agent=agent) for agent in remote_agents
    )
    print(f"所有遠端代理：\n{remote_agents_string}")


def main(argv: list[str]) -> None:
    """腳本主函式。"""
    del argv  # 未使用
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

    print(f"專案：{project_id}")
    print(f"位置：{location}")
    print(f"儲存桶：{bucket}")

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

    # 根據命令列旗標執行相應的操作
    if FLAGS.list:
        list_agents()
    elif FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("刪除需要 resource_id")
            return
        delete(FLAGS.resource_id)
    else:
        print("未知的指令，請使用 --list, --create, 或 --delete")


if __name__ == "__main__":
    app.run(main)
