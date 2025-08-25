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

"""潛在客戶開發代理的部署腳本。"""


import os
import sys
import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

# 將專案根目錄新增至 Python 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from LeadGenerationResearch.agent import root_agent


FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP 專案 ID。")
flags.DEFINE_string("location", None, "GCP 地區。")
flags.DEFINE_string("bucket", None, "GCP 儲存桶。")
flags.DEFINE_string("resource_id", None, "ReasoningEngine 資源 ID。")

flags.DEFINE_bool("list", False, "列出所有代理。")
flags.DEFINE_bool("create", False, "建立一個新代理。")
flags.DEFINE_bool("delete", False, "刪除一個現有代理。")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])


def create() -> None:
    """為潛在客戶開發代理建立一個代理引擎。"""
    # 定義要在已部署代理的環境中設定的環境變數。
    # 這些變數會從本機環境（例如您的 .env 檔案）中讀取。
    env_vars = {
        "GEN_FAST_MODEL": os.getenv("GEN_FAST_MODEL", "gemini-1.5-flash"),
        "GEN_ADVANCED_MODEL": os.getenv("GEN_ADVANCED_MODEL", "gemini-1.5-pro"),
        "GOOGLE_GENAI_USE_VERTEXAI": os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "True"),
    }
    adk_app = AdkApp(
        agent=root_agent,
        env_vars=env_vars,
        enable_tracing=True,
    )

    remote_agent = agent_engines.create(
        adk_app,
        display_name=root_agent.name,
        requirements=[
            "google-adk>=1.0.0",
            "google-cloud-aiplatform[agent_engines]>=1.91.0,!=1.92.0",
            "google-genai>=0.5.0",
            "python-dotenv>=1.0.0",
            "pydantic>=2.10.6,<3.0.0",
            "cloudpickle==3.1.1",
            "json5>=0.9.0",
            "pandas>=2.0.0",
            "requests>=2.31.0",
            "typing-extensions>=4.5.0",
            "absl-py>=2.2.1",
        ],
        extra_packages=["./LeadGenerationResearch"],
    )
    print(f"已建立遠端代理： {remote_agent.resource_name}")
    print(f"使用環境變數： {env_vars}")


def delete(resource_id: str) -> None:
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"已刪除遠端代理： {resource_id}")


def list_agents() -> None:
    remote_agents = agent_engines.list()
    template = """
{agent.name} ("{agent.display_name}")
- 建立時間： {agent.create_time}
- 更新時間： {agent.update_time}
"""
    remote_agents_string = "\n".join(
        template.format(agent=agent) for agent in remote_agents
    )
    print(f"所有遠端代理：\n{remote_agents_string}")


def main(argv: list[str]) -> None:
    del argv  # 未使用
    load_dotenv()

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

    print(f"PROJECT: {project_id}")
    print(f"LOCATION: {location}")
    print(f"BUCKET: {bucket}")

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

    vertexai.init(
        project=project_id,
        location=location,
        staging_bucket=f"gs://{bucket}",
    )

    if FLAGS.list:
        list_agents()
    elif FLAGS.create:
        create()
    elif FLAGS.delete:
        if not FLAGS.resource_id:
            print("刪除操作需要 resource_id")
            return
        delete(FLAGS.resource_id)
    else:
        print("未知的指令")


if __name__ == "__main__":
    app.run(main)
