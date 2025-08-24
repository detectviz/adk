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


import os
from pathlib import Path

from dotenv import load_dotenv
from google.cloud import bigquery

# 定義 .env 檔案的路徑
env_file_path = Path(__file__).parent.parent.parent / ".env"
print(env_file_path)

# 從指定的 .env 檔案載入環境變數
load_dotenv(dotenv_path=env_file_path)


def load_csv_to_bigquery(data_project_id,
                         dataset_name,
                         table_name,
                         csv_filepath):
    """將 CSV 檔案載入至 BigQuery 資料表。

    Args:
        data_project_id: 用於 BQ 資料的 GCP 專案。
        dataset_name: BigQuery 資料集的名稱。
        table_name: BigQuery 資料表的名稱。
        csv_filepath: CSV 檔案的路徑。
    """

    client = bigquery.Client(project=data_project_id)

    dataset_ref = client.dataset(dataset_name)
    table_ref = dataset_ref.table(table_name)

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # 略過標頭列
        autodetect=True,  # 自動偵測結構
    )

    with open(csv_filepath, "rb") as source_file:
        job = client.load_table_from_file(
            source_file, table_ref, job_config=job_config
        )

    job.result()  # 等待工作完成

    print(f"已載入 {job.output_rows} 列至 "
          f"{dataset_name}.{table_name}")


def create_dataset_if_not_exists(compute_project_id,
                                 data_project_id,
                                 dataset_name):
    """如果 BigQuery 資料集不存在，則建立它。

    Args:
        compute_project_id: 用於 BQ 運算的 GCP 專案。
        data_project_id: 用於 BQ 資料的 GQP 專案。
        dataset_name: BigQuery 資料集的名稱。
    """
    client = bigquery.Client(project=compute_project_id)
    dataset_full_name = f"{data_project_id}.{dataset_name}"

    try:
        client.get_dataset(dataset_full_name)  # 發出 API 請求。
        print(f"資料集 {dataset_full_name} 已存在")
    except Exception:
        dataset = bigquery.Dataset(dataset_full_name)
        dataset.location = "US"  # 設定位置 (例如 "US", "EU")
        dataset = client.create_dataset(dataset, timeout=30)  # 發出 API 請求。
        print(f"已建立資料集 {dataset_full_name}")


def main():

    current_directory = os.getcwd()
    print(f"目前工作目錄：{current_directory}")

    """將 CSV 檔案載入 BigQuery 的主要函式。"""
    data_project_id = os.getenv("BQ_DATA_PROJECT_ID")
    compute_project_id = os.getenv("BQ_COMPUTE_PROJECT_ID")
    if not data_project_id:
        raise ValueError("尚未設定 BQ_DATA_PROJECT_ID 環境變數。")
    if not compute_project_id:
        raise ValueError("尚未設定 BQ_COMPUTE_PROJECT_ID 環境變數。")

    dataset_name = "forecasting_sticker_sales"
    train_csv_filepath = "data_science/utils/data/train.csv"
    test_csv_filepath = "data_science/utils/data/test.csv"

    # 如果資料集不存在，則建立它
    print("正在建立資料集。")
    create_dataset_if_not_exists(compute_project_id,
                                 data_project_id,
                                 dataset_name)

    # 載入訓練資料
    print("正在載入訓練資料表。")
    load_csv_to_bigquery(data_project_id,
                         dataset_name,
                         "train",
                         train_csv_filepath)

    # 載入測試資料
    print("正在載入測試資料表。")
    load_csv_to_bigquery(data_project_id,
                         dataset_name,
                         "test",
                         test_csv_filepath)


if __name__ == "__main__":
    main()
