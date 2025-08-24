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

"""BigQuery 資料表建立腳本。"""

import csv
from collections.abc import Sequence

from absl import app, flags
from google.cloud import bigquery
from google.cloud.exceptions import Conflict, GoogleCloudError, NotFound

FLAGS = flags.FLAGS
flags.DEFINE_string("project_id", None, "GCP 專案 ID。")
flags.DEFINE_string("dataset_id", None, "BigQuery 資料集 ID。")
flags.DEFINE_string("data_file", None, "資料檔案的路徑。")
flags.DEFINE_string("location", "us-central1", "資料集的位置。")
flags.mark_flags_as_required(["project_id", "dataset_id"])


def create_bigquery_dataset(
    client: bigquery.Client,
    dataset_id: str,
    location: str,
    description: str = None,
    exists_ok: bool = True,
) -> bigquery.Dataset:
    """建立一個新的 BigQuery 資料集。

    Args:
        client: 一個 BigQuery 用戶端物件。
        dataset_id: 要建立的資料集的 ID。
        location: 資料集的位置 (例如 "US", "EU")。
            預設為 "US"。
        description: 資料集的選擇性描述。
        exists_ok: 如果為 True，則如果資料集已存在，則不引發例外狀況。

    Returns:
        新建立的 bigquery.Dataset 物件。

    Raises:
        google.cloud.exceptions.Conflict: 如果資料集已存在且
            exists_ok 為 False。
        Exception: 對於任何其他錯誤。
    """

    dataset_ref = bigquery.DatasetReference(client.project, dataset_id)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = location
    if description:
        dataset.description = description

    try:
        dataset = client.create_dataset(dataset)
        print(f"資料集 {dataset.dataset_id} 已在 {dataset.location} 建立。")
        return dataset
    except Conflict as e:
        if exists_ok:
            print(f"資料集 {dataset.dataset_id} 已存在。")
            return client.get_dataset(dataset_ref)
        else:
            raise e


def create_bigquery_table(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str,
    schema: list[bigquery.SchemaField],
    description: str = None,
    exists_ok: bool = False,
) -> bigquery.Table:
    """建立一個新的 BigQuery 資料表。

    Args:
        client: 一個 BigQuery 用戶端物件。
        dataset_id: 包含資料表的資料集的 ID。
        table_id: 要建立的資料表的 ID。
        schema: 一個定義資料表結構的 bigquery.SchemaField 物件列表。
        description: 資料表的選擇性描述。
        exists_ok: 如果為 True，則如果資料表已存在，則不引發例外狀況。

    Returns:
        新建立的 bigquery.Table 物件。

    Raises:
        ValueError: 如果結構為空。
        google.cloud.exceptions.Conflict: 如果資料表已存在且
            exists_ok 為 False。
        google.cloud.exceptions.NotFound: 如果資料集不存在。
        Exception: 對於任何其他錯誤。
    """

    if not schema:
        raise ValueError("結構不得為空。")

    table_ref = bigquery.TableReference(
        bigquery.DatasetReference(client.project, dataset_id), table_id
    )
    table = bigquery.Table(table_ref, schema=schema)

    if description:
        table.description = description

    try:
        table = client.create_table(table)
        print(
            f"資料表 {table.project}.{table.dataset_id}.{table.table_id} "
            "已建立。"
        )
        return table
    except Exception as e:  # pylint: disable=broad-exception-caught
        if isinstance(e, NotFound):
            raise NotFound(
                f"在專案 {client.project} 中找不到資料集 {dataset_id}"
            ) from e
        if "Already Exists" in str(e) and exists_ok:
            print(
                f"資料表 {table.project}.{table.dataset_id}.{table.table_id} "
                "已存在。"
            )
            return client.get_table(table_ref)
        else:
            # pylint: disable=broad-exception-raised
            raise Exception(f"建立資料表時發生錯誤：{e}") from e


def insert_csv_to_bigquery(
    client: bigquery.Client,
    table: bigquery.Table,
    csv_filepath: str,
    write_disposition: str = "WRITE_APPEND",
) -> None:
    """
    讀取 CSV 檔案並將其內容插入 BigQuery 資料表。

    Args:
        client: 一個 BigQuery 用戶端物件。
        table: 一個 BigQuery 資料表物件。
        csv_filepath: CSV 檔案的路徑。
        write_disposition: 指定如果目標資料表已存在時發生的動作。
            有效值為：
                - "WRITE_APPEND": 將資料附加到資料表。
                - "WRITE_TRUNCATE": 覆寫資料表資料。
                - "WRITE_EMPTY": 僅在資料表為空時寫入。
            預設為 "WRITE_APPEND"。

    Raises:
        FileNotFoundError: 如果 CSV 檔案不存在。
        ValueError: 如果 write_disposition 無效。
        google.cloud.exceptions.GoogleCloudError: 如果在 BigQuery 操作期間發生任何其他錯誤。
    """

    if write_disposition not in [
        "WRITE_APPEND",
        "WRITE_TRUNCATE",
        "WRITE_EMPTY",
    ]:
        raise ValueError(
            f"無效的 write_disposition：{write_disposition}。"
            "必須是 'WRITE_APPEND'、'WRITE_TRUNCATE' 或 'WRITE_EMPTY' 之一。"
        )

    try:
        with open(csv_filepath, "r", encoding="utf-8") as csvfile:
            csv_reader = csv.DictReader(csvfile)
            rows_to_insert = list(csv_reader)

    except FileNotFoundError:
        raise FileNotFoundError(f"找不到 CSV 檔案：{csv_filepath}") from None

    if not rows_to_insert:
        print("CSV 檔案為空。無需插入。")
        return

    errors = client.insert_rows_json(
        table, rows_to_insert, row_ids=[None] * len(rows_to_insert)
    )

    if errors:
        raise GoogleCloudError(
            f"插入資料列時發生錯誤：{errors}"
        )
    else:
        print(
            f"已成功將 {len(rows_to_insert)} 列插入 "
            f"{table.table_id}。"
        )


def main(argv: Sequence[str]) -> None:  # pylint: disable=unused-argument

    # 定義資料表結構
    data_table_name = "timeseries_data"
    data_table_schema = [
        bigquery.SchemaField("timeseries_code", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("value", "FLOAT", mode="REQUIRED"),
    ]
    data_table_description = "時間序列資料"

    client = bigquery.Client(project=FLAGS.project_id)

    dataset = create_bigquery_dataset(
        client,
        FLAGS.dataset_id,
        FLAGS.location,
        description="時間序列資料集",
    )

    data_table = create_bigquery_table(
        client,
        dataset.dataset_id,
        data_table_name,
        data_table_schema,
        data_table_description,
    )

    if FLAGS.data_file:
        insert_csv_to_bigquery(client, data_table, FLAGS.data_file)


if __name__ == "__main__":
    app.run(main)
