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
"""客戶實體模組。"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class Address(BaseModel):
    """
    代表客戶的地址。
    """

    street: str
    city: str
    state: str
    zip: str
    model_config = ConfigDict(from_attributes=True)


class Product(BaseModel):
    """
    代表客戶購買記錄中的產品。
    """

    product_id: str
    name: str
    quantity: int
    model_config = ConfigDict(from_attributes=True)


class Purchase(BaseModel):
    """
    代表客戶的購買。
    """

    date: str
    items: List[Product]
    total_amount: float
    model_config = ConfigDict(from_attributes=True)


class CommunicationPreferences(BaseModel):
    """
    代表客戶的通訊偏好。
    """

    email: bool = True
    sms: bool = True
    push_notifications: bool = True
    model_config = ConfigDict(from_attributes=True)


class GardenProfile(BaseModel):
    """
    代表客戶的花園設定檔。
    """

    type: str
    size: str
    sun_exposure: str
    soil_type: str
    interests: List[str]
    model_config = ConfigDict(from_attributes=True)


class Customer(BaseModel):
    """
    代表一位客戶。
    """

    account_number: str
    customer_id: str
    customer_first_name: str
    customer_last_name: str
    email: str
    phone_number: str
    customer_start_date: str
    years_as_customer: int
    billing_address: Address
    purchase_history: List[Purchase]
    loyalty_points: int
    preferred_store: str
    communication_preferences: CommunicationPreferences
    garden_profile: GardenProfile
    scheduled_appointments: Dict = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> str:
        """
        將 Customer 物件轉換為 JSON 字串。

        傳回：
            代表 Customer 物件的 JSON 字串。
        """
        return self.model_dump_json(indent=4)

    @staticmethod
    def get_customer(current_customer_id: str) -> Optional["Customer"]:
        """
        根據客戶 ID 擷取客戶。

        參數：
            customer_id：要擷取之客戶的 ID。

        傳回：
            如果找到，則為 Customer 物件，否則為 None。
        """
        # 在真實的應用程式中，這會涉及資料庫查詢。
        # 在此範例中，我們只會傳回一個虛擬客戶。
        return Customer(
            customer_id=current_customer_id,
            account_number="428765091",
            customer_first_name="Alex",
            customer_last_name="Johnson",
            email="alex.johnson@example.com",
            phone_number="+1-702-555-1212",
            customer_start_date="2022-06-10",
            years_as_customer=2,
            billing_address=Address(
                street="123 Main St", city="Anytown", state="CA", zip="12345"
            ),
            purchase_history=[  # 範例購買記錄
                Purchase(
                    date="2023-03-05",
                    items=[
                        Product(
                            product_id="fert-111",
                            name="通用肥料",
                            quantity=1,
                        ),
                        Product(
                            product_id="trowel-222",
                            name="園藝鏝刀",
                            quantity=1,
                        ),
                    ],
                    total_amount=35.98,
                ),
                Purchase(
                    date="2023-07-12",
                    items=[
                        Product(
                            product_id="seeds-333",
                            name="番茄種子（綜合包）",
                            quantity=2,
                        ),
                        Product(
                            product_id="pots-444",
                            name="陶土盆（6 英寸）",
                            quantity=4,
                        ),
                    ],
                    total_amount=42.5,
                ),
                Purchase(
                    date="2024-01-20",
                    items=[
                        Product(
                            product_id="gloves-555",
                            name="園藝手套（皮革）",
                            quantity=1,
                        ),
                        Product(
                            product_id="pruner-666",
                            name="修枝剪",
                            quantity=1,
                        ),
                    ],
                    total_amount=55.25,
                ),
            ],
            loyalty_points=133,
            preferred_store="任何鎮花園商店",
            communication_preferences=CommunicationPreferences(
                email=True, sms=False, push_notifications=True
            ),
            garden_profile=GardenProfile(
                type="後院",
                size="中等",
                sun_exposure="全日照",
                soil_type="未知",
                interests=["花卉", "蔬菜"],
            ),
            scheduled_appointments={},
        )
