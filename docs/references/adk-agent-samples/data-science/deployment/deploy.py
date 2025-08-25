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

"""資料科學代理的部署腳本。"""

import logging
import os

import vertexai
from absl import app, flags
from data_science.agent import root_agent
from dotenv import load_dotenv
from google.api_core import exceptions as google_exceptions
from google.cloud import storage
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP 專案 ID。")
flags.DEFINE_string("location", None, "GCP 位置。")
flags.DEFINE_string(
    "bucket", None, "GCP 儲存桶名稱（不含 gs:// 前綴）。"
)  # 更改了旗標描述
flags.DEFINE_string("resource_id", None, "ReasoningEngine 資源 ID。")

flags.DEFINE_bool("create", False, "建立新代理。")
flags.DEFINE_bool("delete", False, "刪除現有代理。")
flags.mark_bool_flags_as_mutual_exclusive(["create", "delete"])

AGENT_WHL_FILE = "data_science-0.1-py3-none-any.whl"

# 設定日誌記錄
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_staging_bucket(
    project_id: str, location: str, bucket_name: str
) -> str:
    """
    檢查暫存儲存桶是否存在，如果不存在則建立。

    Args:
        project_id: GCP 專案 ID。
        location: 儲存桶的 GCP 位置。
        bucket_name: 儲存桶的預期名稱（不含 gs:// 前綴）。

    Returns:
        完整的儲存桶路徑 (gs://<bucket_name>)。

    Raises:
        google_exceptions.GoogleCloudError: 如果儲存桶建立失敗。
    """
    storage_client = storage.Client(project=project_id)
    try:
        # 檢查儲存桶是否存在
        bucket = storage_client.lookup_bucket(bucket_name)
        if bucket:
            logger.info("暫存儲存桶 gs://%s 已存在。", bucket_name)
        else:
            logger.info(
                "找不到暫存儲存桶 gs://%s。正在建立...", bucket_name
            )
            # 如果儲存桶不存在則建立
            new_bucket = storage_client.create_bucket(
                bucket_name, project=project_id, location=location
            )
            logger.info(
                "已在 %s 成功建立暫存儲存桶 gs://%s。",
                new_bucket.name,
                location,
            )
            # 為求簡單，啟用統一的儲存桶層級存取權
            new_bucket.iam_configuration.uniform_bucket_level_access_enabled = (
                True
            )
            new_bucket.patch()
            logger.info(
                "已為 gs://%s 啟用統一的儲存桶層級存取權。",
                new_bucket.name,
            )

    except google_exceptions.Forbidden as e:
        logger.error(
            (
                "儲存桶 gs://%s 的權限遭拒錯誤。"
                "請確保服務帳號具有「儲存空間管理員」角色。錯誤：%s"
            ),
            bucket_name,
            e,
        )
        raise
    except google_exceptions.Conflict as e:
        logger.warning(
            (
                "儲存桶 gs://%s 可能已存在但由其他專案擁有或最近已刪除。錯誤：%s"
            ),
            bucket_name,
            e,
        )
        # 假設如果它存在，即使有衝突警告也可以繼續
    except google_exceptions.ClientError as e:
        logger.error(
            "建立或存取儲存桶 gs://%s 失敗。錯誤：%s",
            bucket_name,
            e,
        )
        raise

    return f"gs://{bucket_name}"


def create(env_vars: dict[str, str]) -> None:
    """建立並部署代理。"""
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=False,
    )

    if not os.path.exists(AGENT_WHL_FILE):
        logger.error("在以下位置找不到代理 wheel 檔案：%s", AGENT_WHL_FILE)
        # 考慮在此處新增有關如何建置 wheel 檔案的說明
        raise FileNotFoundError(f"找不到代理 wheel 檔案：{AGENT_WHL_FILE}")

    logger.info("正在使用代理 wheel 檔案：%s", AGENT_WHL_FILE)

    remote_agent = agent_engines.create(
        adk_app,
        requirements=[AGENT_WHL_FILE],
        extra_packages=[AGENT_WHL_FILE],
        env_vars=env_vars
    )
    logger.info("已建立遠端代理：%s", remote_agent.resource_name)
    print(f"\n已成功建立代理：{remote_agent.resource_name}")


def delete(resource_id: str) -> None:
    """刪除指定的代理。"""
    logger.info("正在嘗試刪除代理：%s", resource_id)
    try:
        remote_agent = agent_engines.get(resource_id)
        remote_agent.delete(force=True)
        logger.info("已成功刪除遠端代理：%s", resource_id)
        print(f"\n已成功刪除代理：{resource_id}")
    except google_exceptions.NotFound:
        logger.error("找不到資源 ID 為 %s 的代理。", resource_id)
        print(f"\n找不到代理 {resource_id}。")
        print(f"\n找不到代理：{resource_id}")
    except Exception as e:
        logger.error(
            "刪除代理 %s 時發生錯誤：%s", resource_id, e
        )
        print(f"\n刪除代理 {resource_id} 時發生錯誤：{e}")


def main(argv: list[str]) -> None:  # pylint: disable=unused-argument
    """主要執行函式。"""
    load_dotenv()
    env_vars = {}

    project_id = (
        FLAGS.project_id
        if FLAGS.project_id
        else os.getenv("GOOGLE_CLOUD_PROJECT")
    )
    location = (
        FLAGS.location if FLAGS.location else os.getenv("GOOGLE_CLOUD_LOCATION")
    )
    # 如果未提供，則預設儲存桶名稱慣例
    default_bucket_name = f"{project_id}-adk-staging" if project_id else None
    bucket_name = (
        FLAGS.bucket
        if FLAGS.bucket
        else os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET", default_bucket_name)
    )
    # 部署到 Agent Engine 時，請勿設定 "GOOGLE_CLOUD_PROJECT" 或 "GOOGLE_CLOUD_LOCATION"。
    # 這些是由後端設定的。
    env_vars["ROOT_AGENT_MODEL"] = os.getenv("ROOT_AGENT_MODEL")
    env_vars["ANALYTICS_AGENT_MODEL"] = os.getenv("ANALYTICS_AGENT_MODEL")
    env_vars["BASELINE_NL2SQL_MODEL"] = os.getenv("BASELINE_NL2SQL_MODEL")
    env_vars["BIGQUERY_AGENT_MODEL"] = os.getenv("BIGQUERY_AGENT_MODEL")
    env_vars["BQML_AGENT_MODEL"] = os.getenv("BQML_AGENT_MODEL")
    env_vars["CHASE_NL2SQL_MODEL"] = os.getenv("CHASE_NL2SQL_MODEL")
    env_vars["BQ_DATASET_ID"] = os.getenv("BQ_DATASET_ID")
    env_vars["BQ_DATA_PROJECT_ID"] = os.getenv("BQ_DATA_PROJECT_ID")
    env_vars["BQ_COMPUTE_PROJECT_ID"] = os.getenv("BQ_COMPUTE_PROJECT_ID")
    env_vars["BQML_RAG_CORPUS_NAME"] = os.getenv("BQML_RAG_CORPUS_NAME")
    env_vars["CODE_INTERPRETER_EXTENSION_NAME"] = os.getenv(
        "CODE_INTERPRETER_EXTENSION_NAME")
    env_vars["NL2SQL_METHOD"] = os.getenv("NL2SQL_METHOD")

    logger.info("正在使用專案：%s", project_id)
    logger.info("正在使用位置：%s", location)
    logger.info("正在使用儲存桶名稱：%s", bucket_name)

    # --- 輸入驗證 ---
    if not project_id:
        print("\n錯誤：缺少必要的 GCP 專案 ID。")
        print(
            "請設定 GOOGLE_CLOUD_PROJECT 環境變數或使用 --project_id 旗標。"
        )
        return
    if not location:
        print("\n錯誤：缺少必要的 GCP 位置。")
        print(
            "請設定 GOOGLE_CLOUD_LOCATION 環境變數或使用 --location 旗標。"
        )
        return
    if not bucket_name:
        print("\n錯誤：缺少必要的 GCS 儲存桶名稱。")
        print(
            "請設定 GOOGLE_CLOUD_STORAGE_BUCKET 環境變數或使用 --bucket 旗標。"
        )
        return
    if not FLAGS.create and not FLAGS.delete:
        print("\n錯誤：您必須指定 --create 或 --delete 旗標。")
        return
    if FLAGS.delete and not FLAGS.resource_id:
        print(
            "\n錯誤：使用 --delete 旗標時需要 --resource_id。"
        )
        return
    # --- 結束輸入驗證 ---

    try:
        # 設定暫存儲存桶
        staging_bucket_uri=None
        if FLAGS.create:
            staging_bucket_uri = setup_staging_bucket(
                project_id, location, bucket_name
            )

        # 在儲存桶設定和驗證後初始化 Vertex AI
        vertexai.init(
            project=project_id,
            location=location,
            staging_bucket=staging_bucket_uri,  # 暫存儲存桶現在直接傳遞給 create/update 方法
        )

        if FLAGS.create:
            create(env_vars)
        elif FLAGS.delete:
            delete(FLAGS.resource_id)

    except google_exceptions.Forbidden as e:
        print(
            "權限錯誤：請確保服務帳號/使用者具有必要的權限（例如，儲存空間管理員、Vertex AI 使用者）。"
            f"\n詳細資訊：{e}"
        )
    except FileNotFoundError as e:
        print(f"\n檔案錯誤：{e}")
        print(
            "請確保代理 wheel 檔案存在於 'deployment' 目錄中，且您已執行建置腳本"
            "（例如，poetry build --format=wheel --output=deployment'）。"
        )
    except Exception as e:
        print(f"\n發生未預期的錯誤：{e}")
        logger.exception(
            "main 中未處理的例外狀況："
        )  # 記錄完整的追蹤


if __name__ == "__main__":

    app.run(main)
