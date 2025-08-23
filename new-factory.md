## 架構設計：完全解耦的部署與記憶體配置

### 1. **配置架構總覽**

```yaml
# config/environments/production.yaml
deployment:
  platform: "agent_engine"  # agent_engine | cloud_run | gke | local
  
memory:
  backend: "weaviate"  # weaviate | postgresql | vertex_ai | redis
  
# 完全解耦，可自由組合
```

### 2. **實作多層配置系統**

```python
# sre-assistant/config/config_manager.py
from typing import Dict, Any, Optional
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
    region: Optional[str] = "us-central1"
    machine_type: str = "n1-standard-4"
    min_replicas: int = 2
    max_replicas: int = 10
    
    # Cloud Run 特定配置
    service_name: Optional[str] = "sre-assistant"
    memory: str = "2Gi"
    cpu: str = "2"
    concurrency: int = 100
    
    # GKE 特定配置
    cluster_name: Optional[str] = None
    namespace: str = "sre-assistant"
    
    # 本地開發配置
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    
    @validator('project_id')
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
    
    @validator('weaviate_url')
    def validate_weaviate(cls, v, values):
        if values.get('backend') == MemoryBackend.WEAVIATE and not v:
            raise ValueError("weaviate_url required for Weaviate backend")
        return v

class SREAssistantConfig(BaseModel):
    """完整配置"""
    deployment: DeploymentConfig
    memory: MemoryConfig
    
    # 額外配置
    llm_model: str = "gemini-2.0-flash"
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
        base_config = self._load_yaml("config/base.yaml")
        
        # 3. 載入環境特定配置
        env_config = self._load_yaml(f"config/environments/{env}.yaml")
        
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

# 單例模式
config_manager = ConfigManager()
```

### 3. **記憶體後端工廠模式**

```python
# sre-assistant/memory/backend_factory.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import weaviate
import asyncpg
from redis import Redis
from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint

class VectorBackend(ABC):
    """統一的向量後端介面"""
    
    @abstractmethod
    async def upsert(self, embeddings: List[List[float]], 
                    metadata: List[Dict[str, Any]]) -> bool:
        """插入或更新向量"""
        pass
    
    @abstractmethod
    async def search(self, query_embedding: List[float], 
                    k: int = 10) -> List[Dict[str, Any]]:
        """搜尋相似向量"""
        pass
    
    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """刪除向量"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康檢查"""
        pass

class WeaviateBackend(VectorBackend):
    """Weaviate 實作"""
    
    def __init__(self, config: MemoryConfig):
        self.client = weaviate.Client(
            url=config.weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(config.weaviate_api_key)
        )
        self.class_name = config.weaviate_class_name
        self._ensure_schema()
    
    def _ensure_schema(self):
        """確保 schema 存在"""
        schema = {
            "class": self.class_name,
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "metadata", "dataType": ["text"]},
                {"name": "timestamp", "dataType": ["date"]}
            ],
            "vectorizer": "none"  # 我們提供自己的向量
        }
        if not self.client.schema.exists(self.class_name):
            self.client.schema.create_class(schema)
    
    async def upsert(self, embeddings, metadata):
        batch = self.client.batch
        for emb, meta in zip(embeddings, metadata):
            batch.add_data_object(
                data_object=meta,
                class_name=self.class_name,
                vector=emb
            )
        return batch.flush()
    
    async def search(self, query_embedding, k=10):
        result = self.client.query.get(
            self.class_name, 
            ["content", "metadata"]
        ).with_near_vector({
            "vector": query_embedding
        }).with_limit(k).do()
        
        return result["data"]["Get"][self.class_name]
    
    async def health_check(self):
        return self.client.is_ready()

class PostgreSQLBackend(VectorBackend):
    """PostgreSQL + pgvector 實作"""
    
    def __init__(self, config: MemoryConfig):
        self.connection_string = config.postgres_connection_string
        self.pool: Optional[asyncpg.Pool] = None
        self.dimension = config.embedding_dimension
    
    async def initialize(self):
        """初始化連接池和表格"""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20
        )
        
        async with self.pool.acquire() as conn:
            # 啟用 pgvector
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # 建立表格
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS sre_embeddings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    embedding vector({self.dimension}),
                    content TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # 建立索引
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS embedding_idx 
                ON sre_embeddings 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)
    
    async def upsert(self, embeddings, metadata):
        async with self.pool.acquire() as conn:
            for emb, meta in zip(embeddings, metadata):
                await conn.execute("""
                    INSERT INTO sre_embeddings (embedding, content, metadata)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (id) DO UPDATE
                    SET embedding = $1, metadata = $3
                """, emb, meta.get("content", ""), meta)
        return True
    
    async def search(self, query_embedding, k=10):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT content, metadata, 
                       1 - (embedding <=> $1::vector) as similarity
                FROM sre_embeddings
                ORDER BY embedding <=> $1::vector
                LIMIT $2
            """, query_embedding, k)
            
            return [dict(row) for row in rows]

class VertexAIBackend(VectorBackend):
    """Vertex AI Vector Search 實作"""
    
    def __init__(self, config: MemoryConfig):
        self.index_endpoint = MatchingEngineIndexEndpoint(
            index_endpoint_name=config.vertex_index_endpoint
        )
        self.deployed_index_id = config.vertex_deployed_index_id
    
    async def upsert(self, embeddings, metadata):
        datapoints = []
        for i, (emb, meta) in enumerate(zip(embeddings, metadata)):
            datapoints.append({
                "datapoint_id": str(meta.get("id", i)),
                "feature_vector": emb,
                "restricts": [{"namespace": "sre_knowledge"}]
            })
        
        response = await self.index_endpoint.upsert_datapoints(datapoints)
        return response.success
    
    async def search(self, query_embedding, k=10):
        response = await self.index_endpoint.find_neighbors(
            deployed_index_id=self.deployed_index_id,
            queries=[query_embedding],
            num_neighbors=k
        )
        return response.neighbors[0]

class MemoryBackendFactory:
    """記憶體後端工廠"""
    
    @staticmethod
    def create(config: MemoryConfig) -> VectorBackend:
        """根據配置創建對應的後端"""
        
        backend_map = {
            MemoryBackend.WEAVIATE: WeaviateBackend,
            MemoryBackend.POSTGRESQL: PostgreSQLBackend,
            MemoryBackend.VERTEX_AI: VertexAIBackend,
            # MemoryBackend.REDIS: RedisBackend,  # 可擴展
        }
        
        backend_class = backend_map.get(config.backend)
        if not backend_class:
            raise ValueError(f"Unsupported backend: {config.backend}")
        
        return backend_class(config)
```

### 4. **部署策略工廠**

```python
# sre-assistant/deployment/deployment_factory.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import subprocess
import json

class DeploymentStrategy(ABC):
    """部署策略介面"""
    
    @abstractmethod
    async def deploy(self, config: DeploymentConfig) -> Dict[str, Any]:
        """執行部署"""
        pass
    
    @abstractmethod
    async def update(self, config: DeploymentConfig) -> Dict[str, Any]:
        """更新部署"""
        pass
    
    @abstractmethod
    async def rollback(self) -> Dict[str, Any]:
        """回滾部署"""
        pass

class AgentEngineDeployment(DeploymentStrategy):
    """Vertex AI Agent Engine 部署策略"""
    
    async def deploy(self, config: DeploymentConfig):
        from google.cloud.aiplatform.preview import agents
        
        # 初始化 Vertex AI
        aiplatform.init(
            project=config.project_id,
            location=config.region
        )
        
        # 創建 Agent
        agent = agents.Agent.create(
            display_name="sre-assistant",
            model="gemini-2.0-flash",
            system_instruction=GLOBAL_SRE_PROMPT
        )
        
        # 部署配置
        endpoint = agent.deploy(
            machine_type=config.machine_type,
            min_replica_count=config.min_replicas,
            max_replica_count=config.max_replicas,
            service_account=f"sre-assistant@{config.project_id}.iam.gserviceaccount.com",
            environment_variables=self._get_env_vars()
        )
        
        return {
            "status": "deployed",
            "endpoint_url": endpoint.resource_name,
            "platform": "agent_engine"
        }
    
    def _get_env_vars(self):
        """取得環境變數（包含記憶體配置）"""
        memory_config = config_manager.get_memory_config()
        return {
            "MEMORY_BACKEND": memory_config.backend.value,
            "WEAVIATE_URL": memory_config.weaviate_url,
            # ... 其他環境變數
        }

class CloudRunDeployment(DeploymentStrategy):
    """Cloud Run 部署策略"""
    
    async def deploy(self, config: DeploymentConfig):
        # 建構映像
        subprocess.run([
            "gcloud", "builds", "submit",
            "--tag", f"gcr.io/{config.project_id}/{config.service_name}"
        ])
        
        # 部署到 Cloud Run
        result = subprocess.run([
            "gcloud", "run", "deploy", config.service_name,
            "--image", f"gcr.io/{config.project_id}/{config.service_name}",
            "--platform", "managed",
            "--region", config.region,
            "--memory", config.memory,
            "--cpu", config.cpu,
            "--concurrency", str(config.concurrency),
            "--set-env-vars", self._format_env_vars(),
            "--allow-unauthenticated"
        ], capture_output=True, text=True)
        
        return {
            "status": "deployed",
            "service_url": self._extract_service_url(result.stdout),
            "platform": "cloud_run"
        }

class GKEDeployment(DeploymentStrategy):
    """GKE 部署策略"""
    
    async def deploy(self, config: DeploymentConfig):
        # 應用 Kubernetes 資源
        subprocess.run([
            "kubectl", "apply", "-f", "deployment/k8s/",
            "--namespace", config.namespace
        ])
        
        # 等待部署就緒
        subprocess.run([
            "kubectl", "rollout", "status",
            "deployment/sre-assistant",
            "--namespace", config.namespace
        ])
        
        return {
            "status": "deployed",
            "platform": "gke",
            "namespace": config.namespace
        }

class LocalDeployment(DeploymentStrategy):
    """本地開發部署策略"""
    
    async def deploy(self, config: DeploymentConfig):
        import uvicorn
        from sre_assistant import create_app
        
        app = create_app()
        uvicorn.run(
            app,
            host=config.host,
            port=config.port,
            reload=config.debug
        )
        
        return {
            "status": "running",
            "url": f"http://{config.host}:{config.port}",
            "platform": "local"
        }

class DeploymentFactory:
    """部署工廠"""
    
    @staticmethod
    def create(config: DeploymentConfig) -> DeploymentStrategy:
        """根據配置創建部署策略"""
        
        strategy_map = {
            DeploymentPlatform.AGENT_ENGINE: AgentEngineDeployment,
            DeploymentPlatform.CLOUD_RUN: CloudRunDeployment,
            DeploymentPlatform.GKE: GKEDeployment,
            DeploymentPlatform.LOCAL: LocalDeployment
        }
        
        strategy_class = strategy_map.get(config.platform)
        if not strategy_class:
            raise ValueError(f"Unsupported platform: {config.platform}")
        
        return strategy_class()
```

### 5. **整合到主系統**

```python
# sre-assistant/memory.py
from memory.backend_factory import MemoryBackendFactory
from config.config_manager import config_manager

class SREMemorySystem:
    """記憶體系統 - 自動根據配置選擇後端"""
    
    def __init__(self):
        # 從配置管理器取得配置
        memory_config = config_manager.get_memory_config()
        
        # 使用工廠創建後端
        self.backend = MemoryBackendFactory.create(memory_config)
        
        # 初始化嵌入模型
        self.embedding_model = self._init_embedding_model(
            memory_config.embedding_model
        )
    
    async def store_incident(self, incident_data: Dict):
        """儲存事件 - 不管後端是什麼"""
        # 生成嵌入
        embedding = await self.embedding_model.embed(
            incident_data.get("description", "")
        )
        
        # 儲存到後端（自動使用配置的後端）
        return await self.backend.upsert(
            embeddings=[embedding],
            metadata=[incident_data]
        )
    
    async def search_similar_incidents(self, query: str, k: int = 5):
        """搜尋相似事件 - 透明地使用配置的後端"""
        query_embedding = await self.embedding_model.embed(query)
        return await self.backend.search(query_embedding, k)
```

### 6. **配置檔案範例**

```yaml
# config/base.yaml - 基礎配置
deployment:
  platform: "local"
  host: "0.0.0.0"
  port: 8080

memory:
  backend: "memory"
  embedding_model: "textembedding-gecko@003"
  embedding_dimension: 768

llm_model: "gemini-2.0-flash"
temperature: 0.2
```

```yaml
# config/environments/development.yaml
deployment:
  platform: "local"
  debug: true

memory:
  backend: "postgresql"
  postgres_connection_string: "postgresql://localhost/sre_dev"
```

```yaml
# config/environments/production.yaml
deployment:
  platform: "agent_engine"
  project_id: "my-gcp-project"
  region: "us-central1"
  min_replicas: 3
  max_replicas: 20

memory:
  backend: "weaviate"
  weaviate_url: "https://sre-assistant.weaviate.network"
  weaviate_api_key: "${WEAVIATE_API_KEY}"  # 從環境變數讀取
```

### 7. **使用範例**

```bash
# 開發環境：本地 + PostgreSQL
ENVIRONMENT=development python main.py

# 測試環境：Cloud Run + Weaviate
ENVIRONMENT=staging \
  DEPLOYMENT_PLATFORM=cloud_run \
  MEMORY_BACKEND=weaviate \
  python deploy.py

# 生產環境：Agent Engine + Vertex AI
ENVIRONMENT=production \
  DEPLOYMENT_PLATFORM=agent_engine \
  MEMORY_BACKEND=vertex_ai \
  python deploy.py

# 臨時覆寫：Agent Engine + PostgreSQL
ENVIRONMENT=production \
  MEMORY_BACKEND=postgresql \
  DATABASE_URL="postgresql://prod-db/sre" \
  python deploy.py
```

## 優點總結

1. **完全解耦**：部署和記憶體選擇互不影響
2. **環境彈性**：不同環境可用不同組合
3. **易於測試**：本地可用 PostgreSQL，生產用 Weaviate
4. **成本優化**：可根據需求選擇最合適方案
5. **零停機遷移**：可逐步從一個後端遷移到另一個
6. **統一介面**：應用程式碼不需要知道具體後端

這個設計讓您可以在任何環境靈活組合最適合的方案！