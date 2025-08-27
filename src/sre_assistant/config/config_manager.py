# src/sre_assistant/config/config_manager.py
"""
此檔案實現了一個多層次的配置管理系統，用於 SRE Assistant。

它能夠從特定環境的 YAML 設定檔和環境變數中載入、合併和驗證配置，
為系統提供極大的靈活性。Pydantic 模型被用來確保所有配置的
類型安全和結構正確。
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from enum import Enum
import os
import yaml
from pathlib import Path

# --- 配置模型定義 (Pydantic Models) ---

class DeploymentPlatform(str, Enum):
    """
    定義可用的部署平台選項。
    使用 Enum 可以確保配置中的平台名稱是標準化且有效的。
    """
    AGENT_ENGINE = "agent_engine"
    CLOUD_RUN = "cloud_run"
    GKE = "gke"
    LOCAL = "local"

class MemoryBackend(str, Enum):
    """
    定義可用的記憶體後端選項。
    這允許系統在不同的向量數據庫或快取方案之間切換。
    """
    WEAVIATE = "weaviate"
    POSTGRESQL = "postgresql"
    VERTEX_AI = "vertex_ai"
    REDIS = "redis"
    MEMORY = "memory"  # 純記憶體，僅供開發和測試使用

class DeploymentConfig(BaseModel):
    """
    定義與服務部署相關的所有配置。
    包含平台類型以及各平台特定的參數。
    """
    platform: DeploymentPlatform

    # Agent Engine 特定配置
    project_id: Optional[str] = None
    region: str = "us-central1"
    machine_type: str = "n1-standard-4"
    min_replicas: int = 2
    max_replicas: int = 10

    # Cloud Run 特定配置
    service_name: Optional[str] = "sre_assistant"
    memory: str = "2Gi"
    cpu: str = "2"
    concurrency: int = 100

    # GKE 特定配置
    cluster_name: Optional[str] = None
    namespace: str = "sre_assistant"

    # 本地開發配置
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False

    @field_validator('project_id', mode='before')
    @classmethod
    def validate_project_id(cls, v: str, info: ValidationInfo) -> str:
        """
        驗證器：確保在部署到 Agent Engine 時，project_id 已被提供。

        Args:
            v (str): `project_id` 欄位的值。
            info (ValidationInfo): 包含其他欄位資料的 Pydantic 驗證資訊物件。

        Returns:
            str: 原始的 `project_id` 值。

        Raises:
            ValueError: 如果平台是 Agent Engine 但 `project_id` 為空。
        """
        if info.data.get('platform') == DeploymentPlatform.AGENT_ENGINE and not v:
            raise ValueError("project_id is required for Agent Engine deployment")
        return v

class MemoryConfig(BaseModel):
    """
    定義與長期記憶體 (RAG) 和短期快取相關的配置。
    """
    backend: MemoryBackend

    # Weaviate 配置
    weaviate_url: Optional[str] = None
    weaviate_api_key: Optional[str] = None
    weaviate_class_name: str = "SREKnowledge"

    # PostgreSQL 配置
    postgres_connection_string: Optional[str] = None
    postgres_pool_size: int = 10
    use_pgvector: bool = True

    # Vertex AI 配置
    vertex_index_endpoint: Optional[str] = None
    vertex_deployed_index_id: Optional[str] = None

    # Redis 配置
    redis_url: Optional[str] = None
    redis_ttl_seconds: int = 3600

    # 通用 RAG 配置
    embedding_model: str = "textembedding-gecko@003"
    embedding_dimension: int = 768
    chunk_size: int = 512
    chunk_overlap: int = 50

    @field_validator('weaviate_url', mode='before')
    @classmethod
    def validate_weaviate(cls, v: str, info: ValidationInfo) -> str:
        """
        驗證器：確保在使用 Weaviate 後端時，weaviate_url 已被提供。

        Args:
            v (str): `weaviate_url` 欄位的值。
            info (ValidationInfo): 包含其他欄位資料的 Pydantic 驗證資訊物件。

        Returns:
            str: 原始的 `weaviate_url` 值。

        Raises:
            ValueError: 如果後端是 Weaviate 但 `weaviate_url` 為空。
        """
        if info.data.get('backend') == MemoryBackend.WEAVIATE and not v:
            raise ValueError("weaviate_url is required for Weaviate backend")
        return v

class AuthProvider(str, Enum):
    """
    定義可用的認證提供者選項。
    """
    GOOGLE_IAM = "google_iam"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    MTLS = "mtls"
    LOCAL = "local"  # 開發用

class AuthConfig(BaseModel):
    """
    定義與認證和授權相關的所有配置。
    """
    provider: AuthProvider

    # Google IAM 配置
    service_account_path: Optional[str] = None
    impersonate_service_account: Optional[str] = None

    # OAuth2 配置
    oauth_client_id: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    oauth_redirect_uri: Optional[str] = None
    oauth_scopes: List[str] = Field(default_factory=list)

    # JWT 配置
    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    jwt_expiry_seconds: int = 3600

    # API Key 配置
    api_key_header: str = "X-API-Key"
    api_keys_file: Optional[str] = None

    # mTLS 配置
    mtls_cert_path: Optional[str] = None
    mtls_key_path: Optional[str] = None
    mtls_ca_path: Optional[str] = None

    # 通用安全配置
    enable_rbac: bool = True
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60
    enable_audit_logging: bool = True

    @field_validator('service_account_path', mode='before')
    @classmethod
    def validate_google_iam(cls, v: str, info: ValidationInfo) -> str:
        """
        驗證器：確保在使用 Google IAM 提供者時，service_account_path 已被提供。

        Args:
            v (str): `service_account_path` 欄位的值。
            info (ValidationInfo): 包含其他欄位資料的 Pydantic 驗證資訊物件。

        Returns:
            str: 原始的 `service_account_path` 值。

        Raises:
            ValueError: 如果提供者是 Google IAM 但 `service_account_path` 為空。
        """
        if info.data.get('provider') == AuthProvider.GOOGLE_IAM and not v:
            raise ValueError("service_account_path is required for Google IAM provider")
        return v

class SessionBackend(str, Enum):
    """
    定義可用的會話後端選項 (用於短期記憶體)。
    """
    FIRESTORE = "firestore"
    IN_MEMORY = "in_memory"

class SREAssistantConfig(BaseModel):
    """
    應用程式的頂層配置模型。

    這個模型將所有子配置（部署、記憶體、認證等）組合在一起，
    形成一個單一、完整、經過驗證的配置物件。
    """
    deployment: DeploymentConfig
    memory: MemoryConfig
    auth: AuthConfig
    session_backend: SessionBackend = SessionBackend.IN_MEMORY

    # Firestore 特定配置
    firestore_project_id: Optional[str] = None
    firestore_collection: str = "sre_assistant_sessions"

    # LLM 相關配置
    llm_model: str = "gemini-1.5-pro-latest"
    temperature: float = 0.2
    enable_hitl: bool = True
    enable_a2a: bool = True
    log_level: str = "INFO"

    # SRE 特定配置
    slo_targets: Dict[str, float] = Field(default_factory=lambda: {
        "availability": 0.999,
        "latency_p95": 30.0,
        "error_rate": 0.01
    })

class ConfigManager:
    """
    配置管理器，負責載入、合併、驗證和提供配置。

    這是一個單例 (Singleton) 模式的實現，確保整個應用程式
    在運行時只使用一份一致的配置。
    """

    def __init__(self):
        """
        初始化 ConfigManager。
        在實例化時，會自動觸發配置的載入流程。
        """
        self.config: Optional[SREAssistantConfig] = None
        self._load_config()

    def _load_config(self) -> SREAssistantConfig:
        """
        執行多層次的配置載入和合併。

        載入順序（後者覆蓋前者）:
        1. 環境特定的 YAML 檔案 (例如 `development.yaml`)
        2. 環境變數 (例如 `WEAVIATE_URL`)

        Returns:
            SREAssistantConfig: 一個經過 Pydantic 驗證的完整配置物件。
        """
        # 步驟 1: 確定當前環境 (預設為 development)
        env = os.getenv("ENVIRONMENT", "development")

        # 步驟 2: 載入環境特定的 YAML 配置檔
        env_config_path = f"src/sre_assistant/config/environments/{env}.yaml"
        merged_config = self._load_yaml(env_config_path)

        # 步驟 3: 應用環境變數覆寫，賦予最高的優先級
        merged_config = self._apply_env_overrides(merged_config)

        # 步驟 4: 使用 Pydantic 模型進行驗證和類型轉換
        self.config = SREAssistantConfig(**merged_config)
        return self.config

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """
        從指定的路徑安全地載入一個 YAML 檔案。

        如果檔案不存在，會返回一個空字典而不是引發錯誤。

        Args:
            path (str): YAML 檔案的路徑。

        Returns:
            Dict[str, Any]: 從 YAML 檔案解析出的字典。
        """
        config_path = Path(path)
        if not config_path.exists():
            return {}
        with open(config_path) as f:
            return yaml.safe_load(f) or {}

    def _apply_env_overrides(self, config: Dict) -> Dict:
        """
        檢查特定的環境變數，並用其值覆蓋現有的配置。

        這使得在容器化環境 (如 Kubernetes, Cloud Run) 中
        可以輕鬆地動態修改配置，而無需更改設定檔。

        Args:
            config (Dict): 從 YAML 檔案載入的配置字典。

        Returns:
            Dict: 已被環境變數覆蓋後的配置字典。
        """
        # 部署平台覆寫
        if platform := os.getenv("DEPLOYMENT_PLATFORM"):
            config.setdefault("deployment", {})["platform"] = platform

        # 記憶體後端覆寫
        if backend := os.getenv("MEMORY_BACKEND"):
            config.setdefault("memory", {})["backend"] = backend

        # Weaviate URL 覆寫
        if weaviate_url := os.getenv("WEAVIATE_URL"):
            config.setdefault("memory", {})["weaviate_url"] = weaviate_url

        # PostgreSQL 覆寫
        if pg_conn := os.getenv("DATABASE_URL"):
            config.setdefault("memory", {})["postgres_connection_string"] = pg_conn

        return config

    def get_deployment_config(self) -> DeploymentConfig:
        """
        提供對部署配置的安全訪問。

        Returns:
            DeploymentConfig: 部署相關的配置物件。
        """
        return self.config.deployment

    def get_memory_config(self) -> MemoryConfig:
        """
        提供對記憶體配置的安全訪問。

        Returns:
            MemoryConfig: 記憶體相關的配置物件。
        """
        return self.config.memory

    def get_auth_config(self) -> AuthConfig:
        """
        提供對認證配置的安全訪問。

        Returns:
            AuthConfig: 認證相關的配置物件。
        """
        return self.config.auth

# 創建 ConfigManager 的單例，供整個應用程式導入和使用。
config_manager = ConfigManager()
