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
"""客戶服務代理 (Agent) 的工具模組。"""

import logging
import uuid
from datetime import datetime, timedelta
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def send_call_companion_link(phone_number: str) -> str:
    """
    將連結傳送到使用者的電話號碼以開始視訊會話。

    參數：
        phone_number (str)：要傳送連結的電話號碼。

    傳回：
        dict：一個包含狀態和訊息的字典。

    範例：
        >>> send_call_companion_link(phone_number='+12065550123')
        {'status': 'success', 'message': '連結已傳送到 +12065550123'}
    """

    logger.info("Sending call companion link to %s", phone_number)

    return {"status": "success", "message": f"連結已傳送到 {phone_number}"}


def approve_discount(discount_type: str, value: float, reason: str) -> str:
    """
    批准使用者要求的固定費率或百分比折扣。

    參數：
        discount_type (str)：折扣類型，可以是「percentage」或「flat」。
        value (float)：折扣值。
        reason (str)：折扣原因。

    傳回：
        str：一個指示批准狀態的 JSON 字串。

    範例：
        >>> approve_discount(type='percentage', value=10.0, reason='客戶忠誠度')
        '{"status": "ok"}'
    """
    if value > 10:
        logger.info("Denying %s discount of %s", discount_type, value)
        # 傳回錯誤原因，以便模型可以恢復。
        return {"status": "rejected",
                "message": "折扣太大。必須小於或等於 10。"}
    logger.info(
        "Approving a %s discount of %s because %s", discount_type, value, reason
    )
    return {"status": "ok"}

def sync_ask_for_approval(discount_type: str, value: float, reason: str) -> str:
    """
    向經理請求折扣批准。

    參數：
        discount_type (str)：折扣類型，可以是「percentage」或「flat」。
        value (float)：折扣值。
        reason (str)：折扣原因。

    傳回：
        str：一個指示批准狀態的 JSON 字串。

    範例：
        >>> sync_ask_for_approval(type='percentage', value=15, reason='客戶忠誠度')
        '{"status": "approved"}'
    """
    logger.info(
        "Asking for approval for a %s discount of %s because %s",
        discount_type,
        value,
        reason,
    )
    return {"status": "approved"}


def update_salesforce_crm(customer_id: str, details: dict) -> dict:
    """
    使用客戶詳細資訊更新 Salesforce CRM。

    參數：
        customer_id (str)：客戶 ID。
        details (str)：要在 Salesforce 中更新的詳細資訊字典。

    傳回：
        dict：一個包含狀態和訊息的字典。

    範例：
        >>> update_salesforce_crm(customer_id='123', details={
            'appointment_date': '2024-07-25',
            'appointment_time': '9-12',
            'services': '種植',
            'discount': '種植服務 85 折',
            'qr_code': '下次店內消費 9 折'})
        {'status': 'success', 'message': 'Salesforce 記錄已更新。'}
    """
    logger.info(
        "Updating Salesforce CRM for customer ID %s with details: %s",
        customer_id,
        details,
    )
    return {"status": "success", "message": "Salesforce 記錄已更新。"}


def access_cart_information(customer_id: str) -> dict:
    """
    參數：
        customer_id (str)：客戶 ID。

    傳回：
        dict：一個代表購物車內容的字典。

    範例：
        >>> access_cart_information(customer_id='123')
        {'items': [{'product_id': 'soil-123', 'name': '標準盆栽土', 'quantity': 1}, {'product_id': 'fert-456', 'name': '通用肥料', 'quantity': 1}], 'subtotal': 25.98}
    """
    logger.info("Accessing cart information for customer ID: %s", customer_id)

    # 模擬 API 回應 - 請替換為實際的 API 呼叫
    mock_cart = {
        "items": [
            {
                "product_id": "soil-123",
                "name": "標準盆栽土",
                "quantity": 1,
            },
            {
                "product_id": "fert-456",
                "name": "通用肥料",
                "quantity": 1,
            },
        ],
        "subtotal": 25.98,
    }
    return mock_cart


def modify_cart(
    customer_id: str, items_to_add: list[dict], items_to_remove: list[dict]
) -> dict:
    """透過新增和/或移除商品來修改使用者的購物車。

    參數：
        customer_id (str)：客戶 ID。
        items_to_add (list)：一個字典列表，每個字典包含 'product_id' 和 'quantity'。
        items_to_remove (list)：要移除的 product_id 列表。

    傳回：
        dict：一個指示購物車修改狀態的字典。
    範例：
        >>> modify_cart(customer_id='123', items_to_add=[{'product_id': 'soil-456', 'quantity': 1}, {'product_id': 'fert-789', 'quantity': 1}], items_to_remove=[{'product_id': 'fert-112', 'quantity': 1}])
        {'status': 'success', 'message': '購物車已成功更新。', 'items_added': True, 'items_removed': True}
    """

    logger.info("Modifying cart for customer ID: %s", customer_id)
    logger.info("Adding items: %s", items_to_add)
    logger.info("Removing items: %s", items_to_remove)
    # 模擬 API 回應 - 請替換為實際的 API 呼叫
    return {
        "status": "success",
        "message": "購物車已成功更新。",
        "items_added": True,
        "items_removed": True,
    }


def get_product_recommendations(plant_type: str, customer_id: str) -> dict:
    """根據植物類型提供產品推薦。

    參數：
        plant_type：植物類型（例如，'矮牽牛'、'喜陽一年生植物'）。
        customer_id：可選的客戶 ID，用於個人化推薦。

    傳回：
        一個推薦產品的字典。範例：
        {'recommendations': [
            {'product_id': 'soil-456', 'name': '開花專用盆栽土', 'description': '...'},
            {'product_id': 'fert-789', 'name': '開花專用肥料', 'description': '...'}
        ]}
    """
    #
    logger.info(
        "Getting product recommendations for plant " "type: %s and customer %s",
        plant_type,
        customer_id,
    )
    # 模擬 API 回應 - 請替換為實際的 API 呼叫或推薦引擎
    if plant_type.lower() == "petunias":
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-456",
                    "name": "開花專用盆栽土",
                    "description": "提供矮牽牛喜愛的額外養分。",
                },
                {
                    "product_id": "fert-789",
                    "name": "開花專用肥料",
                    "description": "專為開花一年生植物配製。",
                },
            ]
        }
    else:
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-123",
                    "name": "標準盆栽土",
                    "description": "一種優良的通用盆栽土。",
                },
                {
                    "product_id": "fert-456",
                    "name": "通用肥料",
                    "description": "適用於多種植物。",
                },
            ]
        }
    return recommendations


def check_product_availability(product_id: str, store_id: str) -> dict:
    """檢查指定商店（或自取）的產品供應情況。

    參數：
        product_id：要檢查的產品 ID。
        store_id：商店 ID（或 'pickup' 表示自取供應情況）。

    傳回：
        一個指示供應情況的字典。範例：
        {'available': True, 'quantity': 10, 'store': '總店'}

    範例：
        >>> check_product_availability(product_id='soil-456', store_id='pickup')
        {'available': True, 'quantity': 10, 'store': 'pickup'}
    """
    logger.info(
        "Checking availability of product ID: %s at store: %s",
        product_id,
        store_id,
    )
    # 模擬 API 回應 - 請替換為實際的 API 呼叫
    return {"available": True, "quantity": 10, "store": store_id}


def schedule_planting_service(
    customer_id: str, date: str, time_range: str, details: str
) -> dict:
    """預約種植服務。

    參數：
        customer_id：客戶 ID。
        date：期望的日期 (YYYY-MM-DD)。
        time_range：期望的時間範圍（例如，「9-12」）。
        details：任何其他詳細資訊（例如，「種植矮牽牛」）。

    傳回：
        一個指示排程狀態的字典。範例：
        {'status': 'success', 'appointment_id': '12345', 'date': '2024-07-29', 'time': '上午 9:00 - 中午 12:00'}

    範例：
        >>> schedule_planting_service(customer_id='123', date='2024-07-29', time_range='9-12', details='種植矮牽牛')
        {'status': 'success', 'appointment_id': 'some_uuid', 'date': '2024-07-29', 'time': '9-12', 'confirmation_time': '2024-07-29 9:00'}
    """
    logger.info(
        "Scheduling planting service for customer ID: %s on %s (%s)",
        customer_id,
        date,
        time_range,
    )
    logger.info("Details: %s", details)
    # 模擬 API 回應 - 請替換為實際的 API 呼叫到您的排程系統
    # 根據日期和時間範圍計算確認時間
    start_time_str = time_range.split("-")[0]  # 取得開始時間 (例如 "9")
    confirmation_time_str = (
        f"{date} {start_time_str}:00"  # 例如 "2024-07-29 9:00"
    )

    return {
        "status": "success",
        "appointment_id": str(uuid.uuid4()),
        "date": date,
        "time": time_range,
        "confirmation_time": confirmation_time_str,  # 用於行事曆的格式化時間
    }


def get_available_planting_times(date: str) -> list:
    """擷取給定日期的可用種植服務時間段。

    參數：
        date：要檢查的日期 (YYYY-MM-DD)。

    傳回：
        一個可用時間範圍的列表。

    範例：
        >>> get_available_planting_times(date='2024-07-29')
        ['9-12', '13-16']
    """
    logger.info("Retrieving available planting times for %s", date)
    # 模擬 API 回應 - 請替換為實際的 API 呼叫
    # 產生一些模擬的時間段，確保它們的格式正確：
    return ["9-12", "13-16"]


def send_care_instructions(
    customer_id: str, plant_type: str, delivery_method: str
) -> dict:
    """透過電子郵件或簡訊傳送特定植物類型的護理說明。

    參數：
        customer_id：客戶 ID。
        plant_type：植物類型。
        delivery_method：'email'（預設）或 'sms'。

    傳回：
        一個指示狀態的字典。

    範例：
        >>> send_care_instructions(customer_id='123', plant_type='矮牽牛', delivery_method='email')
        {'status': 'success', 'message': '矮牽牛的護理說明已透過電子郵件傳送。'}
    """
    logger.info(
        "Sending care instructions for %s to customer: %s via %s",
        plant_type,
        customer_id,
        delivery_method,
    )
    # 模擬 API 回應 - 請替換為實際的 API 呼叫或電子郵件/簡訊傳送邏輯
    return {
        "status": "success",
        "message": f"{plant_type} 的護理說明已透過 {delivery_method} 傳送。",
    }


def generate_qr_code(
    customer_id: str,
    discount_value: float,
    discount_type: str,
    expiration_days: int,
) -> dict:
    """為折扣產生 QR 碼。

    參數：
        customer_id：客戶 ID。
        discount_value：折扣值（例如，10 表示 10%）。
        discount_type：「percentage」（預設）或「fixed」。
        expiration_days：QR 碼到期前的天數。

    傳回：
        一個包含 QR 碼資料（或其連結）的字典。範例：
        {'status': 'success', 'qr_code_data': '...', 'expiration_date': '2024-08-28'}

    範例：
        >>> generate_qr_code(customer_id='123', discount_value=10.0, discount_type='percentage', expiration_days=30)
        {'status': 'success', 'qr_code_data': 'MOCK_QR_CODE_DATA', 'expiration_date': '2024-08-24'}
    """
    
    # 驗證折扣金額是否可接受自動批准折扣的防護措施。
    # 深度防禦，以防止可能規避系統指令並
    # 能夠獲得任意折扣的惡意提示。
    if discount_type == "" or discount_type == "percentage":
        if discount_value > 10:
            return "無法為此金額產生 QR 碼，必須小於或等於 10%"
    if discount_type == "fixed" and discount_value > 20:
        return "無法為此金額產生 QR 碼，必須小於或等於 20"
    
    logger.info(
        "Generating QR code for customer: %s with %s - %s discount.",
        customer_id,
        discount_value,
        discount_type,
    )
    # 模擬 API 回應 - 請替換為實際的 QR 碼產生程式庫
    expiration_date = (
        datetime.now() + timedelta(days=expiration_days)
    ).strftime("%Y-%m-%d")
    return {
        "status": "success",
        "qr_code_data": "MOCK_QR_CODE_DATA",  # 請替換為實際的 QR 碼
        "expiration_date": expiration_date,
    }
