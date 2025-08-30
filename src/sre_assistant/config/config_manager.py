# src/sre_assistant/config/config_manager.py
"""
此檔案實現了一個多層次的配置管理系統, 用於 SRE Assistant.

它能夠從特定環境的 YAML 設定檔和環境變數中載入, 合併和驗證配置,
為系統提供極大的靈活性. Pydantic 模型被用來確保所有配置的
類型安全和結構正確.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator, ValidationInfo
from enum import Enum
import os
import yaml
from pathlib import Path

# Import shared contracts from the new single source of truth
from ..contracts import AuthProvider, AuthConfig

# --- 配置模型定義 (Pydantic Models) ---

class DeploymentPlatform(str, Enum):
    """
    定義可用的部署平台選項.
    使用 Enum 可以確保配置中的平台名稱是標準化且有效的.
    """
    AGENT_ENGINE = "agent_engine"
    CLOUD_RUN = "cloud_run"
    GKE = "gke"
    LOCAL = "local"

class MemoryBackend(str, Enum):
    """
    定義可用的記憶體後端選項.
    這允許系統在不同的向量數據庫或快取方案之間切換.
    """
    WEAVIATE = "weaviate"
    POSTGRESQL = "postgresql"
    VERTEX_AI = "vertex_ai"
    REDIS = "redis"
    MEMORY = "memory"  # 純記憶體, 僅供開發和測試使用

class DeploymentConfig(BaseModel):
    """
    定義與服務部署相關的所有配置.
    包含平台類型以及各平台特定的參數.
    """
    platform: DeploymentPlatform
    project_id: Optional[str] = None
    region: str = "us-central1"
    machine_type: str = "n1-standard-4"
    min_replicas: int = 2
    max_replicas: int = 10
    service_name: Optional[str] = "sre_assistant"
    memory: str = "2Gi"
    cpu: str = "2"
    concurrency: int = 100
    cluster_name: Optional[str] = None
    namespace: str = "sre_assistant"
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False

    @field_validator('project_id', mode='before')
    @classmethod
    def validate_project_id(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get('platform') == DeploymentPlatform.AGENT_ENGINE and not v:
            raise ValueError("project_id is required for Agent Engine deployment")
        return v

class MemoryConfig(BaseModel):
    """
    定義與長期記憶體 (RAG) 和短期快取相關的配置.
    """
    backend: MemoryBackend
    weaviate_url: Optional[str] = None
    weaviate_api_key: Optional[str] = None
    weaviate_class_name: str = "SREKnowledge"
    postgres_connection_string: Optional[str] = None
    postgres_pool_size: int = 10
    use_pgvector: bool = True
    vertex_index_endpoint: Optional[str] = None
    vertex_deployed_index_id: Optional[str] = None
    redis_url: Optional[str] = None
    redis_ttl_seconds: int = 3600
    embedding_model: str = "textembedding-gecko@003"
    embedding_dimension: int = 768
    chunk_size: int = 512
    chunk_overlap: int = 50

    @field_validator('weaviate_url', mode='before')
    @classmethod
    def validate_weaviate(cls, v: str, info: ValidationInfo) -> str:
        if info.data.get('backend') == MemoryBackend.WEAVIATE and not v:
            raise ValueError("weaviate_url is required for Weaviate backend")
        return v

class SessionBackend(str, Enum):
    """
    定義可用的會話後端選項 (用於短期記憶體).
    """
    POSTGRESQL = "postgresql"
    FIRESTORE = "firestore"
    IN_MEMORY = "in_memory"

class SREAssistantConfig(BaseModel):
    """
    應用程式的頂層配置模型.
    """
    deployment: DeploymentConfig
    memory: MemoryConfig
    auth: AuthConfig
    session_backend: SessionBackend = SessionBackend.IN_MEMORY
    firestore_project_id: Optional[str] = None
    firestore_collection: str = "sre_assistant_sessions"

    @model_validator(mode='after')
    def check_postgres_session_dependency(self) -> 'SREAssistantConfig':
        if self.session_backend == SessionBackend.POSTGRESQL:
            if not self.memory or not self.memory.postgres_connection_string:
                raise ValueError("postgres_connection_string is required for PostgreSQL session backend")
        return self

    llm_model: str = "gemini-1.5-pro-latest"
    temperature: float = 0.2
    enable_hitl: bool = True
    enable_a2a: bool = True
    log_level: str = "INFO"
    slo_targets: Dict[str, float] = Field(default_factory=lambda: {
        "availability": 0.999,
        "latency_p95": 30.0,
        "error_rate": 0.01
    })

class ConfigManager:
    """
    配置管理器, 負責載入, 合併, 驗證和提供配置.
    """

    def __init__(self):
        self.config: Optional[SREAssistantConfig] = None
        self._load_config()

    def _load_config(self) -> SREAssistantConfig:
        env = os.getenv("ENVIRONMENT", "development")
        env_config_path = f"src/sre_assistant/config/environments/{env}.yaml"
        merged_config = self._load_yaml(env_config_path)
        merged_config = self._apply_env_overrides(merged_config)
        self.config = SREAssistantConfig(**merged_config)
        return self.config

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        config_path = Path(path)
        if not config_path.exists():
            return {}
        with open(config_path) as f:
            return yaml.safe_load(f) or {}

    def _apply_env_overrides(self, config: Dict) -> Dict:
        if platform := os.getenv("DEPLOYMENT_PLATFORM"):
            config.setdefault("deployment", {})["platform"] = platform
        if backend := os.getenv("MEMORY_BACKEND"):
            config.setdefault("memory", {})["backend"] = backend
        if weaviate_url := os.getenv("WEAVIATE_URL"):
            config.setdefault("memory", {})["weaviate_url"] = weaviate_url
        if pg_conn := os.getenv("DATABASE_URL"):
            config.setdefault("memory", {})["postgres_connection_string"] = pg_conn
        return config

    def get_deployment_config(self) -> DeploymentConfig:
        return self.config.deployment

    def get_memory_config(self) -> MemoryConfig:
        return self.config.memory

    def get_auth_config(self) -> AuthConfig:
        return self.config.auth

config_manager = ConfigManager()
