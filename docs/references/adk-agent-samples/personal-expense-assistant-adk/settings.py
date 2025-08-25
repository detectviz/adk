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

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    YamlConfigSettingsSource,
    PydanticBaseSettingsSource,
)
from typing import Type, Tuple


class Settings(BaseSettings):
    """從 YAML 和環境變數載入的應用程式設定。

    此類別定義應用程式的設定綱要，設定
    從 settings.yaml 檔案載入，並可透過環境變數覆寫。

    屬性：
        GCLOUD_LOCATION：API 服務的 Google Cloud 位置。
        GCLOUD_PROJECT_ID：Google Cloud 專案識別碼。
        BACKEND_URL：後端服務 API 端點的 URL。
        STORAGE_BUCKET_NAME：用於儲存收據的 Google Cloud Storage 儲存貯體名稱。
        DB_COLLECTION_NAME：用於儲存收據的 Firestore 集合名稱。
    """

    GCLOUD_LOCATION: str
    GCLOUD_PROJECT_ID: str
    BACKEND_URL: str = "http://localhost:8081/chat"
    STORAGE_BUCKET_NAME: str = "personal-expense-assistant-receipts"
    DB_COLLECTION_NAME: str = "personal-expense-assistant-receipts"

    model_config = SettingsConfigDict(
        yaml_file="settings.yaml", yaml_file_encoding="utf-8"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """自訂設定來源及其優先順序。

        此方法定義載入設定時檢查不同設定來源的順序：
        1. 環境變數
        2. YAML 設定檔
        3. 建構函式提供的值

        參數：
            settings_cls：Settings 類別類型。
            init_settings：來自類別初始化的設定。
            env_settings：來自環境變數的設定。
            dotenv_settings：來自 .env 檔案的設定（未使用）。
            file_secret_settings：來自秘密檔案的設定（未使用）。

        傳回：
            一個依優先順序排列的設定來源元組。
        """
        return (
            env_settings,  # 環境變數為第一優先
            YamlConfigSettingsSource(
                settings_cls
            ),  # YAML 設定檔為第二優先
            init_settings,  # 建構函式提供的值為最後優先
        )


def get_settings() -> Settings:
    """建立並傳回一個載入設定的 Settings 執行個體。

    初始化一個 Settings 物件，該物件從
    環境變數和 YAML 設定檔載入設定值，其中環境
    變數優先。

    傳回：
        一個包含所有應用程式設定的完整設定 Settings 執行個體。
    """
    return Settings()
