"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import datetime
from typing import Dict, List, Any
from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1 import FieldFilter
from google.cloud.firestore_v1.base_query import And
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from settings import get_settings
from google import genai

SETTINGS = get_settings()
DB_CLIENT = firestore.Client(
    project=SETTINGS.GCLOUD_PROJECT_ID
)  # 將使用「(default)」資料庫
COLLECTION = DB_CLIENT.collection(SETTINGS.DB_COLLECTION_NAME)
GENAI_CLIENT = genai.Client(
    vertexai=True, location=SETTINGS.GCLOUD_LOCATION, project=SETTINGS.GCLOUD_PROJECT_ID
)
EMBEDDING_DIMENSION = 768
EMBEDDING_FIELD_NAME = "embedding"
INVALID_ITEMS_FORMAT_ERR = """
品項格式無效。必須是包含「name」、「price」和「quantity」鍵的字典列表。"""
RECEIPT_DESC_FORMAT = """
商店名稱：{store_name}
交易時間：{transaction_time}
總金額：{total_amount}
幣別：{currency}
購買品項：
{purchased_items}
收據圖片 ID：{receipt_id}
"""


def sanitize_image_id(image_id: str) -> str:
    """透過移除任何前置/後置空格來清理圖片 ID。"""
    if image_id.startswith("[IMAGE-"):
        image_id = image_id.split("ID ")[1].split("]")[0]

    return image_id.strip()


def store_receipt_data(
    image_id: str,
    store_name: str,
    transaction_time: str,
    total_amount: float,
    purchased_items: List[Dict[str, Any]],
    currency: str = "IDR",
) -> str:
    """
    將收據資料儲存在資料庫中。

    參數：
        image_id (str)：圖片的唯一識別碼。例如 IMAGE-POSITION 0-ID 12345，
            圖片的 ID 為 12345。
        store_name (str)：商店的名稱。
        transaction_time (str)：購買時間，採用 ISO 格式 ("YYYY-MM-DDTHH:MM:SS.ssssssZ")。
        total_amount (float)：花費的總金額。
        purchased_items (List[Dict[str, Any]])：購買的品項及其價格的列表。每個品項必須包含：
            - name (str)：品項的名稱。
            - price (float)：品項的價格。
            - quantity (int, optional)：品項的數量。如果未提供，預設為 1。
        currency (str, optional)：交易的幣別，可從商店位置推斷。
            如果不確定，預設為 "IDR"。

    傳回：
        str：包含收據 ID 的成功訊息。

    引發：
        Exception：如果操作失敗或輸入無效。
    """
    try:
        # 如果提供完整的圖片佔位符，則擷取 id 字串
        image_id = sanitize_image_id(image_id)

        # 檢查收據是否已存在
        doc = get_receipt_data_by_image_id(image_id)

        if doc:
            return f"ID 為 {image_id} 的收據已存在"

        # 驗證交易時間
        if not isinstance(transaction_time, str):
            raise ValueError(
                "交易時間無效：必須是 ISO 格式 'YYYY-MM-DDTHH:MM:SS.ssssssZ' 的字串"
            )
        try:
            datetime.datetime.fromisoformat(transaction_time.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(
                "交易時間格式無效。必須是 ISO 格式 'YYYY-MM-DDTHH:MM:SS.ssssssZ'"
            )

        # 驗證品項格式
        if not isinstance(purchased_items, list):
            raise ValueError(INVALID_ITEMS_FORMAT_ERR)

        for _item in purchased_items:
            if (
                not isinstance(_item, dict)
                or "name" not in _item
                or "price" not in _item
            ):
                raise ValueError(INVALID_ITEMS_FORMAT_ERR)

            if "quantity" not in _item:
                _item["quantity"] = 1

        # 從所有收據資訊建立組合文字以取得更好的嵌入
        result = GENAI_CLIENT.models.embed_content(
            model="text-embedding-004",
            contents=RECEIPT_DESC_FORMAT.format(
                store_name=store_name,
                transaction_time=transaction_time,
                total_amount=total_amount,
                currency=currency,
                purchased_items=purchased_items,
                receipt_id=image_id,
            ),
        )

        embedding = result.embeddings[0].values

        doc = {
            "receipt_id": image_id,
            "store_name": store_name,
            "transaction_time": transaction_time,
            "total_amount": total_amount,
            "currency": currency,
            "purchased_items": purchased_items,
            EMBEDDING_FIELD_NAME: Vector(embedding),
        }

        COLLECTION.add(doc)

        return f"已成功儲存 ID 為 {image_id} 的收據"
    except Exception as e:
        raise Exception(f"儲存收據失敗：{str(e)}")


def search_receipts_by_metadata_filter(
    start_time: str,
    end_time: str,
    min_total_amount: float = -1.0,
    max_total_amount: float = -1.0,
) -> str:
    """
    在特定時間範圍內，並可選擇性地依金額篩選收據。

    參數：
        start_time (str)：篩選的開始日期時間（採用 ISO 格式，例如 'YYYY-MM-DDTHH:MM:SS.ssssssZ'）。
        end_time (str)：篩選的結束日期時間（採用 ISO 格式，例如 'YYYY-MM-DDTHH:MM:SS.ssssssZ'）。
        min_total_amount (float)：篩選的最小總金額（含）。預設為 -1。
        max_total_amount (float)：篩選的最大總金額（含）。預設為 -1。

    傳回：
        str：一個字串，其中包含符合所有已套用篩選條件的收據資料清單。

    引發：
        Exception：如果搜尋失敗或輸入無效。
    """
    try:
        # 驗證開始和結束時間
        if not isinstance(start_time, str) or not isinstance(end_time, str):
            raise ValueError("start_time 和 end_time 必須是 ISO 格式的字串")
        try:
            datetime.datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            datetime.datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("start_time 和 end_time 必須是 ISO 格式的字串")

        # 從基本集合參考開始
        query = COLLECTION

        # 透過適當地串連條件來建構複合查詢
        # 注意，此範例假設只有 1 位使用者，
        # 需要為多位使用者重構查詢
        filters = [
            FieldFilter("transaction_time", ">=", start_time),
            FieldFilter("transaction_time", "<=", end_time),
        ]

        # 新增可選篩選器
        if min_total_amount != -1:
            filters.append(FieldFilter("total_amount", ">=", min_total_amount))

        if max_total_amount != -1:
            filters.append(FieldFilter("total_amount", "<=", max_total_amount))

        # 套用篩選器
        composite_filter = And(filters=filters)
        query = query.where(filter=composite_filter)

        # 執行查詢並收集結果
        search_result_description = "依中繼資料搜尋結果：\n"
        for doc in query.stream():
            data = doc.to_dict()
            data.pop(
                EMBEDDING_FIELD_NAME, None
            )  # 移除嵌入，因為顯示時不需要

            search_result_description += f"\n{RECEIPT_DESC_FORMAT.format(**data)}"

        return search_result_description
    except Exception as e:
        raise Exception(f"篩選收據時發生錯誤：{str(e)}")


def search_relevant_receipts_by_natural_language_query(
    query_text: str, limit: int = 5
) -> str:
    """
    使用向量搜尋，搜尋內容與查詢最相似的收據。
    此工具可用於難以轉換為中繼資料篩選器的使用者查詢。
    例如對字串比對敏感的商店名稱或品項名稱。
    如果您無法使用依中繼資料篩選工具，請使用此工具。

    參數：
        query_text (str)：搜尋文字（例如「咖啡」、「晚餐」、「雜貨」）。
        limit (int, optional)：要傳回的最大結果數（預設值：5）。

    傳回：
        str：一個字串，其中包含與內容相關的收據資料清單。

    引發：
        Exception：如果搜尋失敗或輸入無效。
    """
    try:
        # 為查詢文字產生嵌入
        result = GENAI_CLIENT.models.embed_content(
            model="text-embedding-004", contents=query_text
        )
        query_embedding = result.embeddings[0].values

        # 注意，此範例假設只有 1 位使用者，
        # 需要為多位使用者重構查詢
        vector_query = COLLECTION.find_nearest(
            vector_field=EMBEDDING_FIELD_NAME,
            query_vector=Vector(query_embedding),
            distance_measure=DistanceMeasure.EUCLIDEAN,
            limit=limit,
        )

        # 執行查詢並收集結果
        search_result_description = "依內容關聯性搜尋結果：\n"
        for doc in vector_query.stream():
            data = doc.to_dict()
            data.pop(
                EMBEDDING_FIELD_NAME, None
            )  # 移除嵌入，因為顯示時不需要
            search_result_description += f"\n{RECEIPT_DESC_FORMAT.format(**data)}"

        return search_result_description
    except Exception as e:
        raise Exception(f"搜尋收據時發生錯誤：{str(e)}")


def get_receipt_data_by_image_id(image_id: str) -> Dict[str, Any]:
    """
    使用 image_id 從資料庫擷取收據資料。

    參數：
        image_id (str)：收據圖片的唯一識別碼。例如，如果佔位符是
            [IMAGE-ID 12345]，要使用的 ID 是 12345。

    傳回：
        Dict[str, Any]：一個字典，其中包含具有下列索引鍵的收據資料：
            - receipt_id (str)：收據圖片的唯一識別碼。
            - store_name (str)：商店的名稱。
            - transaction_time (str)：世界標準時間 (UTC) 的購買時間。
            - total_amount (float)：花費的總金額。
            - currency (str)：交易的幣別。
            - purchased_items (List[Dict[str, Any]])：購買的品項及其詳細資料的清單。
        如果找不到收據，則傳回一個空字典。
    """
    # 如果提供完整的圖片佔位符，則擷取 id 字串
    image_id = sanitize_image_id(image_id)

    # 查詢收據集合中具有相符 receipt_id (image_id) 的文件
    # 注意，此範例假設只有 1 位使用者，
    # 需要為多位使用者重構查詢
    query = COLLECTION.where(filter=FieldFilter("receipt_id", "==", image_id)).limit(1)
    docs = list(query.stream())

    if not docs:
        return {}

    # 取得第一個相符的文件
    doc_data = docs[0].to_dict()
    doc_data.pop(EMBEDDING_FIELD_NAME, None)

    return doc_data
