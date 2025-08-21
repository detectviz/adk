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
# 為此模組新增文件字串
"""客戶服務代理的工具模組。"""

import logging
import uuid
from datetime import datetime, timedelta
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def send_call_companion_link(phone_number: str) -> str:
    """
    發送連結至使用者的電話號碼以啟動視訊會話。

    Args:
        phone_number (str): 要發送連結的電話號碼。

    Returns:
        dict: 一個包含狀態和訊息的字典。

    Example:
        >>> send_call_companion_link(phone_number='+12065550123')
        {'status': 'success', 'message': 'Link sent to +12065550123'}
    """

    logger.info("正在發送通話夥伴連結至 %s", phone_number)

    return {"status": "success", "message": f"連結已發送至 {phone_number}"}


def approve_discount(discount_type: str, value: float, reason: str) -> str:
    """
    批准使用者要求的固定金額或百分比折扣。

    Args:
        discount_type (str): 折扣類型，可以是「percentage」或「flat」。
        value (float): 折扣的數值。
        reason (str): 折扣的原因。

    Returns:
        str: 一個表示批准狀態的 JSON 字串。

    Example:
        >>> approve_discount(type='percentage', value=10.0, reason='Customer loyalty')
        '{"status": "ok"}'
    """
    if value > 10:
        logger.info("正在拒絕 %s 的折扣 %s", discount_type, value)
        # 回傳錯誤原因，以便模型可以復原。
        return {"status": "rejected",
                "message": "折扣金額過大。必須為 10 或更少。"}
    logger.info(
        "正在批准 %s 的折扣 %s，原因為 %s", discount_type, value, reason
    )
    return {"status": "ok"}

def sync_ask_for_approval(discount_type: str, value: float, reason: str) -> str:
    """
    向經理請求折扣批准。

    Args:
        discount_type (str): 折扣類型，可以是「percentage」或「flat」。
        value (float): 折扣的數值。
        reason (str): 折扣的原因。

    Returns:
        str: 一個表示批准狀態的 JSON 字串。

    Example:
        >>> sync_ask_for_approval(type='percentage', value=15, reason='Customer loyalty')
        '{"status": "approved"}'
    """
    logger.info(
        "正在請求批准 %s 的折扣 %s，原因為 %s",
        discount_type,
        value,
        reason,
    )
    return {"status": "approved"}


def update_salesforce_crm(customer_id: str, details: dict) -> dict:
    """
    使用客戶詳細資訊更新 Salesforce CRM。

    Args:
        customer_id (str): 客戶的 ID。
        details (str): 要在 Salesforce 中更新的詳細資訊字典。

    Returns:
        dict: 一個包含狀態和訊息的字典。

    Example:
        >>> update_salesforce_crm(customer_id='123', details={
            'appointment_date': '2024-07-25',
            'appointment_time': '9-12',
            'services': 'Planting',
            'discount': '15% off planting',
            'qr_code': '10% off next in-store purchase'})
        {'status': 'success', 'message': 'Salesforce record updated.'}
    """
    logger.info(
        "正在為客戶 ID %s 更新 Salesforce CRM，詳細資訊：%s",
        customer_id,
        details,
    )
    return {"status": "success", "message": "Salesforce 記錄已更新。"}


def access_cart_information(customer_id: str) -> dict:
    """
    Args:
        customer_id (str): 客戶的 ID。

    Returns:
        dict: 一個表示購物車內容的字典。

    Example:
        >>> access_cart_information(customer_id='123')
        {'items': [{'product_id': 'soil-123', 'name': 'Standard Potting Soil', 'quantity': 1}, {'product_id': 'fert-456', 'name': 'General Purpose Fertilizer', 'quantity': 1}], 'subtotal': 25.98}
    """
    logger.info("正在存取客戶 ID 的購物車資訊：%s", customer_id)

    # 模擬 API 回應 - 請替換為實際的 API 呼叫
    mock_cart = {
        "items": [
            {
                "product_id": "soil-123",
                "name": "Standard Potting Soil",
                "quantity": 1,
            },
            {
                "product_id": "fert-456",
                "name": "General Purpose Fertilizer",
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

    Args:
        customer_id (str): 客戶的 ID。
        items_to_add (list): 一個字典列表，每個字典包含 'product_id' 和 'quantity'。
        items_to_remove (list): 要移除的 product_id 列表。

    Returns:
        dict: 一個表示購物車修改狀態的字典。
    Example:
        >>> modify_cart(customer_id='123', items_to_add=[{'product_id': 'soil-456', 'quantity': 1}, {'product_id': 'fert-789', 'quantity': 1}], items_to_remove=[{'product_id': 'fert-112', 'quantity': 1}])
        {'status': 'success', 'message': 'Cart updated successfully.', 'items_added': True, 'items_removed': True}
    """

    logger.info("正在為客戶 ID 修改購物車：%s", customer_id)
    logger.info("正在新增商品：%s", items_to_add)
    logger.info("正在移除商品：%s", items_to_remove)
    # 模擬 API 回應 - 請替換為實際的 API 呼叫
    return {
        "status": "success",
        "message": "購物車已成功更新。",
        "items_added": True,
        "items_removed": True,
    }


def get_product_recommendations(plant_type: str, customer_id: str) -> dict:
    """根據植物類型提供產品推薦。

    Args:
        plant_type: 植物的類型（例如，「Petunias」、「Sun-loving annuals」）。
        customer_id: 可選的客戶 ID，用於個人化推薦。

    Returns:
        一個推薦產品的字典。範例：
        {'recommendations': [
            {'product_id': 'soil-456', 'name': 'Bloom Booster Potting Mix', 'description': '...'},
            {'product_id': 'fert-789', 'name': 'Flower Power Fertilizer', 'description': '...'}
        ]}
    """
    #
    logger.info(
        "正在為植物類型：%s 和客戶 %s 獲取產品推薦",
        plant_type,
        customer_id,
    )
    # 模擬 API 回應 - 請替換為實際的 API 呼叫或推薦引擎
    if plant_type.lower() == "petunias":
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-456",
                    "name": "Bloom Booster Potting Mix",
                    "description": "提供矮牽牛喜愛的額外養分。",
                },
                {
                    "product_id": "fert-789",
                    "name": "Flower Power Fertilizer",
                    "description": "專為開花一年生植物配製。",
                },
            ]
        }
    else:
        recommendations = {
            "recommendations": [
                {
                    "product_id": "soil-123",
                    "name": "Standard Potting Soil",
                    "description": "一種優良的通用盆栽土。",
                },
                {
                    "product_id": "fert-456",
                    "name": "General Purpose Fertilizer",
                    "description": "適用於多種植物。",
                },
            ]
        }
    return recommendations


def check_product_availability(product_id: str, store_id: str) -> dict:
    """檢查指定商店（或自取）的產品庫存情況。

    Args:
        product_id: 要檢查的產品 ID。
        store_id: 商店的 ID（或「pickup」表示自取庫存）。

    Returns:
        一個表示庫存情況的字典。範例：
        {'available': True, 'quantity': 10, 'store': 'Main Store'}

    Example:
        >>> check_product_availability(product_id='soil-456', store_id='pickup')
        {'available': True, 'quantity': 10, 'store': 'pickup'}
    """
    logger.info(
        "正在檢查產品 ID：%s 在商店：%s 的庫存情況",
        product_id,
        store_id,
    )
    # 模擬 API 回應 - 請替換為實際的 API 呼叫
    return {"available": True, "quantity": 10, "store": store_id}


def schedule_planting_service(
    customer_id: str, date: str, time_range: str, details: str
) -> dict:
    """安排種植服務預約。

    Args:
        customer_id: 客戶的 ID。
        date:  期望的日期（YYYY-MM-DD）。
        time_range: 期望的時間範圍（例如，「9-12」）。
        details: 任何額外的詳細資訊（例如，「種植矮牽牛」）。

    Returns:
        一個表示排程狀態的字典。範例：
        {'status': 'success', 'appointment_id': '12345', 'date': '2024-07-29', 'time': '9:00 AM - 12:00 PM'}

    Example:
        >>> schedule_planting_service(customer_id='123', date='2024-07-29', time_range='9-12', details='Planting Petunias')
        {'status': 'success', 'appointment_id': 'some_uuid', 'date': '2024-07-29', 'time': '9-12', 'confirmation_time': '2024-07-29 9:00'}
    """
    logger.info(
        "正在為客戶 ID：%s 安排種植服務，日期：%s (%s)",
        customer_id,
        date,
        time_range,
    )
    logger.info("詳細資訊：%s", details)
    # 模擬 API 回應 - 請替換為您排程系統的實際 API 呼叫
    # 根據日期和時間範圍計算確認時間
    start_time_str = time_range.split("-")[0]  # 取得開始時間（例如，「9」）
    confirmation_time_str = (
        f"{date} {start_time_str}:00"  # 例如，「2024-07-29 9:00」
    )

    return {
        "status": "success",
        "appointment_id": str(uuid.uuid4()),
        "date": date,
        "time": time_range,
        "confirmation_time": confirmation_time_str,  # 用於日曆的格式化時間
    }


def get_available_planting_times(date: str) -> list:
    """擷取給定日期的可用種植服務時間段。

    Args:
        date: 要檢查的日期（YYYY-MM-DD）。

    Returns:
        一個可用時間範圍的列表。

    Example:
        >>> get_available_planting_times(date='2024-07-29')
        ['9-12', '13-16']
    """
    logger.info("正在擷取 %s 的可用種植時間", date)
    # 模擬 API 回應 - 請替換為實際的 API 呼叫
    # 產生一些模擬的時間段，確保它們的格式正確：
    return ["9-12", "13-16"]


def send_care_instructions(
    customer_id: str, plant_type: str, delivery_method: str
) -> dict:
    """透過電子郵件或簡訊發送特定植物類型的護理說明。

    Args:
        customer_id:  客戶的 ID。
        plant_type: 植物的類型。
        delivery_method: 'email'（預設）或 'sms'。

    Returns:
        一個表示狀態的字典。

    Example:
        >>> send_care_instructions(customer_id='123', plant_type='Petunias', delivery_method='email')
        {'status': 'success', 'message': 'Care instructions for Petunias sent via email.'}
    """
    logger.info(
        "正在透過 %s 向客戶 %s 發送 %s 的護理說明",
        delivery_method,
        customer_id,
        plant_type,
    )
    # 模擬 API 回應 - 請替換為實際的 API 呼叫或電子郵件/簡訊發送邏輯
    return {
        "status": "success",
        "message": f"已透過 {delivery_method} 發送 {plant_type} 的護理說明。",
    }


def generate_qr_code(
    customer_id: str,
    discount_value: float,
    discount_type: str,
    expiration_days: int,
) -> dict:
    """產生折扣的 QR code。

    Args:
        customer_id: 客戶的 ID。
        discount_value: 折扣的數值（例如，10 表示 10%）。
        discount_type: "percentage"（預設）或 "fixed"。
        expiration_days: QR code 到期的天數。

    Returns:
        一個包含 QR code 資料（或其連結）的字典。範例：
        {'status': 'success', 'qr_code_data': '...', 'expiration_date': '2024-08-28'}

    Example:
        >>> generate_qr_code(customer_id='123', discount_value=10.0, discount_type='percentage', expiration_days=30)
        {'status': 'success', 'qr_code_data': 'MOCK_QR_CODE_DATA', 'expiration_date': '2024-08-24'}
    """
    
    # 驗證自動批准折扣金額是否可接受的防護機制。
    # 深度防禦，以防止可能規避系統指令並獲得任意折扣的惡意提示。
    if discount_type == "" or discount_type == "percentage":
        if discount_value > 10:
            return "無法為此金額產生 QR code，必須為 10% 或更少"
    if discount_type == "fixed" and discount_value > 20:
        return "無法為此金額產生 QR code，必須為 20 或更少"
    
    logger.info(
        "正在為客戶 %s 產生 %s - %s 的折扣 QR code。",
        customer_id,
        discount_value,
        discount_type,
    )
    # 模擬 API 回應 - 請替換為實際的 QR code 產生函式庫
    expiration_date = (
        datetime.now() + timedelta(days=expiration_days)
    ).strftime("%Y-%m-%d")
    return {
        "status": "success",
        "qr_code_data": "MOCK_QR_CODE_DATA",  # 請替換為實際的 QR code
        "expiration_date": expiration_date,
    }
