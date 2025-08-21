"""測試將機器學習工程代理部署到 Agent Engine。"""

import os

import vertexai
from absl import app, flags
from dotenv import load_dotenv
from vertexai import agent_engines

FLAGS = flags.FLAGS

flags.DEFINE_string("project_id", None, "GCP 專案 ID。")
flags.DEFINE_string("location", None, "GCP 地理位置。")
flags.DEFINE_string("bucket", None, "GCP 儲存貯體。")
flags.DEFINE_string(
    "resource_id",
    None,
    "ReasoningEngine 資源 ID (部署代理後返回)",
)
flags.DEFINE_string("user_id", None, "使用者 ID (可以是任何字串)。")
flags.mark_flag_as_required("user_id")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument

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

    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")
    bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

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

    agent = agent_engines.get(FLAGS.resource_id)
    print(f"找到資源 ID 為 {FLAGS.resource_id} 的代理")
    session = agent.create_session(user_id=FLAGS.user_id)
    print(f"已為使用者 ID {FLAGS.user_id} 建立工作階段")
    print("輸入 'quit' 以離開。")
    while True:
        user_input = input("輸入: ")
        if user_input == "quit":
            break

        for event in agent.stream_query(
            user_id=FLAGS.user_id, session_id=session["id"], message=user_input
        ):
            if "content" in event:
                if "parts" in event["content"]:
                    parts = event["content"]["parts"]
                    for part in parts:
                        if "text" in part:
                            text_part = part["text"]
                            print(f"回應: {text_part}")

    agent.delete_session(user_id=FLAGS.user_id, session_id=session["id"])
    print(f"已刪除使用者 ID {FLAGS.user_id} 的工作階段")


if __name__ == "__main__":
    app.run(main)
