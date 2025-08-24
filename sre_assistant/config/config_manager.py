# sre_assistant/config/config_manager.py
# 說明：此檔案實作了一個多層次的配置管理系統，用於 SRE Assistant。
# 它能夠從基礎設定檔、特定環境設定檔和環境變數中載入、合併和驗證配置，
# 為系統提供極大的靈活性。

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum
import os
import yaml
from pathlib import Path

class DeploymentPlatform(str, Enum):
    """部署平台選項"""
    AGENT_ENGINE = "agent_engine"
    CLOUD_RUN = "cloud_run"
    GKE = "gke"
    LOCAL = "local"

class MemoryBackend(str, Enum):
    """記憶體後端選項"""
    WEAVIATE = "weaviate"
    POSTGRESQL = "postgresql"
    VERTEX_AI = "vertex_ai"
    REDIS = "redis"
    MEMORY = "memory"  # 純記憶體，開發用

class DeploymentConfig(BaseModel):
    """部署配置"""
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

    @validator('project_id', always=True)
    def validate_project_id(cls, v, values):
        if values.get('platform') == DeploymentPlatform.AGENT_ENGINE and not v:
            raise ValueError("project_id required for Agent Engine deployment")
        return v

class MemoryConfig(BaseModel):
    """記憶體配置"""
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

    # 通用配置
    embedding_model: str = "textembedding-gecko@003"
    embedding_dimension: int = 768
    chunk_size: int = 512
    chunk_overlap: int = 50

    @validator('weaviate_url', always=True)
    def validate_weaviate(cls, v, values):
        if values.get('backend') == MemoryBackend.WEAVIATE and not v:
            raise ValueError("weaviate_url required for Weaviate backend")
        return v

class AuthProvider(str, Enum):
    """認證提供者選項"""
    GOOGLE_IAM = "google_iam"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    JWT = "jwt"
    MTLS = "mtls"
    LOCAL = "local"  # 開發用

class AuthConfig(BaseModel):
    """認證配置"""
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

    # 通用配置
    enable_rbac: bool = True
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60
    enable_audit_logging: bool = True

    @validator('service_account_path')
    def validate_google_iam(cls, v, values):
        if values.get('provider') == AuthProvider.GOOGLE_IAM and not v:
            raise ValueError("service_account_path required for Google IAM")
        return v

class SessionBackend(str, Enum):
    """會話後端選項"""
    FIRESTORE = "firestore"
    IN_MEMORY = "in_memory"

class SREAssistantConfig(BaseModel):
    """完整配置"""
    deployment: DeploymentConfig
    memory: MemoryConfig
    auth: AuthConfig  # 新增認證配置
    session_backend: SessionBackend = SessionBackend.IN_MEMORY

    # Firestore 特定配置
    firestore_project_id: Optional[str] = None
    firestore_collection: str = "sre_assistant_sessions"

    # 額外配置
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
    """配置管理器 - 支援多環境和覆寫"""

    def __init__(self):
        self.config: Optional[SREAssistantConfig] = None
        self._load_config()

    def _load_config(self) -> SREAssistantConfig:
        """載入配置：環境變數 > 環境配置檔 > 預設值"""

        # 1. 確定環境
        env = os.getenv("ENVIRONMENT", "development")

        # 2. 載入基礎配置
        base_config = self._load_yaml("sre_assistant/config/base.yaml")

        # 3. 載入環境特定配置
        env_config_path = f"sre_assistant/config/environments/{env}.yaml"
        env_config = self._load_yaml(env_config_path)

        # 4. 合併配置
        merged = self._deep_merge(base_config, env_config)

        # 5. 環境變數覆寫
        merged = self._apply_env_overrides(merged)

        # 6. 驗證並創建配置物件
        self.config = SREAssistantConfig(**merged)
        return self.config

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """載入 YAML 配置檔"""
        config_path = Path(path)
        if not config_path.exists():
            return {}

        with open(config_path) as f:
            return yaml.safe_load(f) or {}

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """深度合併配置"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _apply_env_overrides(self, config: Dict) -> Dict:
        """應用環境變數覆寫"""
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
        """取得部署配置"""
        return self.config.deployment

    def get_memory_config(self) -> MemoryConfig:
        """取得記憶體配置"""
        return self.config.memory

    def get_auth_config(self) -> AuthConfig:
        """取得認證配置"""
        return self.config.auth

# 單例模式：在應用程式中共享同一個配置實例
config_manager = ConfigManager()
