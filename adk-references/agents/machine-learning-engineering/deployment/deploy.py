"""機器學習工程代理的部署腳本"""


import os

import vertexai
from absl import app, flags
from machine_learning_engineering.agent import root_agent
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP 專案 ID。")
flags.DEFINE_string("location", None, "GCP 地理位置。")
flags.DEFINE_string("bucket", None, "GCP 儲存貯體。")
flags.DEFINE_string("resource_id", None, "ReasoningEngine 資源 ID。")

flags.DEFINE_bool("list", False, "列出所有代理。")
flags.DEFINE_bool("create", False, "建立一個新代理。")
flags.DEFINE_bool("delete", False, "刪除一個現有代理。")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])


def create() -> None:
    """為 MLE-STAR 建立一個代理引擎。"""
    adk_app = AdkApp(agent=root_agent, enable_tracing=True)

    remote_agent = agent_engines.create(
        adk_app,
        display_name=root_agent.name,
        requirements=[
            "google-adk (>=1.5.0)",
            "google-cloud-aiplatform[adk,agent_engines] (>=1.93.0)",
            "google-genai (>=1.5.0,<2.0.0)",
            "pydantic (>=2.10.6,<3.0.0)",
            "absl-py (>=2.2.1,<3.0.0)",
            "numpy (>=2.2.3)",
            "pandas (>=2.3.1)",
            "scikit-learn (>=1.7.1)",
            "scipy (>=1.16.0)",
            "lightgbm (>=4.6.0)",
            "torch @ https://download.pytorch.org/whl/cpu-cxx11-abi/torch-2.7.1%2Bcpu.cxx11.abi-cp312-cp312-linux_x86_64.whl",
        ],
        extra_packages=[
            "./machine_learning_engineering",
        ],
    )
    print(f"已建立遠端代理：{remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    remote_agent = agent_engines.get(resource_id)
    remote_agent.delete(force=True)
    print(f"已刪除遠端代理：{resource_id}")


def list_agents() -> None:
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

    print(f"專案：{project_id}")
    print(f"位置：{location}")
    print(f"儲存貯體：{bucket}")

    if not project_id:
        print("缺少必要的環境變數：GOOGLE_CLOUD_PROJECT")
        return
    elif not location:
        print("缺少必要的環境變數：GOOGLE_CLOUD_LOCATION")
        return
    elif not bucket:
        print("缺少必要的環境變數：GOOGLE_CLOUD_STORAGE_BUCKET")
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
