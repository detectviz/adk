# src/sre_assistant/memory/backend_factory.py
"""
此檔案實現了向量數據庫後端的工廠模式。

它定義了一個統一的 `VectorBackend` 抽象介面，並為多種向量數據庫
（如 Weaviate, PostgreSQL with pgvector, Vertex AI Vector Search）
提供了具體的實現。`MemoryBackendFactory` 則根據配置動態創建
對應的後端實例。

這使得 SRE Assistant 的長期記憶體 (RAG) 功能可以輕鬆地在
不同的底層技術之間切換，以適應不同的部署環境和需求。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import weaviate
import asyncpg
from redis import Redis
from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint
from ..config.config_manager import MemoryConfig
from .chroma_backend import ChromaBackend

class VectorBackend(ABC):
    """
    統一的向量數據庫後端抽象基礎類別 (Interface)。
    所有具體的後端實現都必須繼承此類別。
    """

    @abstractmethod
    async def upsert(self, embeddings: List[List[float]],
                    metadata: List[Dict[str, Any]]) -> bool:
        """
        插入或更新向量及其中繼資料。

        Args:
            embeddings (List[List[float]]): 要插入的向量列表。
            metadata (List[Dict[str, Any]]): 與每個向量對應的中繼資料列表。

        Returns:
            bool: 操作是否成功。
        """
        pass

    @abstractmethod
    async def search(self, query_embedding: List[float],
                    k: int = 10) -> List[Dict[str, Any]]:
        """
        根據查詢向量，搜尋最相似的 k 個結果。

        Args:
            query_embedding (List[float]): 用於查詢的單個向量。
            k (int): 要返回的相似結果數量。

        Returns:
            List[Dict[str, Any]]: 一個包含相似結果（通常包括中繼資料和相似度分數）的列表。
        """
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> bool:
        """
        根據提供的 ID 列表刪除向量。

        Args:
            ids (List[str]): 要刪除的向量的唯一 ID 列表。

        Returns:
            bool: 操作是否成功。
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        檢查向量數據庫後端的健康狀況。

        Returns:
            bool: 如果後端服務健康，返回 True。
        """
        pass

class WeaviateBackend(VectorBackend):
    """Weaviate 向量數據庫的具體實現。"""

    def __init__(self, config: MemoryConfig):
        """
        初始化 Weaviate 後端。

        Args:
            config (MemoryConfig): 包含 Weaviate URL 和 API Key 的配置。
        """
        self.client = weaviate.Client(
            url=config.weaviate_url,
            auth_client_secret=weaviate.AuthApiKey(api_key=config.weaviate_api_key)
        )
        self.class_name = config.weaviate_class_name
        self._ensure_schema()

    def _ensure_schema(self):
        """
        確保 Weaviate 中存在所需的資料綱要 (Schema)。
        如果指定的 class 不存在，則會自動創建。
        """
        schema = {
            "class": self.class_name,
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "metadata", "dataType": ["text"]},
                {"name": "timestamp", "dataType": ["date"]}
            ],
            "vectorizer": "none"  # 表示我們將提供自己的向量
        }
        if not self.client.schema.exists(self.class_name):
            self.client.schema.create_class(schema)

    async def upsert(self, embeddings, metadata):
        """
        使用 Weaviate 的批次處理功能，高效地插入或更新數據。

        Args:
            embeddings (List[List[float]]): 向量列表。
            metadata (List[Dict[str, Any]]): 中繼資料列表。

        Returns:
            bool: 操作是否成功。
        """
        with self.client.batch as batch:
            for emb, meta in zip(embeddings, metadata):
                batch.add_data_object(
                    data_object=meta,
                    class_name=self.class_name,
                    vector=emb
                )
        return True # Assuming flush() on exit is successful

    async def search(self, query_embedding, k=10):
        """
        在 Weaviate 中執行近鄰搜尋。

        Args:
            query_embedding (List[float]): 查詢向量。
            k (int): 返回的結果數量。

        Returns:
            List[Dict[str, Any]]: 搜尋結果列表。
        """
        result = self.client.query.get(
            self.class_name,
            ["content", "metadata"]
        ).with_near_vector({
            "vector": query_embedding
        }).with_limit(k).do()
        return result.get("data", {}).get("Get", {}).get(self.class_name, [])

    async def delete(self, ids: List[str]) -> bool:
        """
        從 Weaviate 中刪除數據。

        注意：此處為簡化實現。真實的 Weaviate 刪除操作需要
        使用物件的 UUID，通常透過過濾器來完成。

        Args:
            ids (List[str]): 要刪除的物件 UUID 列表。

        Returns:
            bool: 操作是否成功。
        """
        # Production implementation would use client.data_object.delete() with UUIDs.
        print(f"Delete functionality for Weaviate needs specific UUIDs: {ids}")
        return False

    async def health_check(self):
        """
        檢查 Weaviate 服務是否準備就緒。

        Returns:
            bool: 如果服務健康，返回 True。
        """
        return self.client.is_ready()

class PostgreSQLBackend(VectorBackend):
    """使用 PostgreSQL 和 pgvector 擴展的向量數據庫實現。"""

    def __init__(self, config: MemoryConfig):
        """
        初始化 PostgreSQL 後端。

        Args:
            config (MemoryConfig): 包含資料庫連接字串和向量維度的配置。
        """
        self.connection_string = config.postgres_connection_string
        self.pool: Optional[asyncpg.Pool] = None
        self.dimension = config.embedding_dimension

    async def initialize(self):
        """
        初始化資料庫連接池，並確保 pgvector 擴展和資料表已創建。
        """
        if self.pool:
            return
        self.pool = await asyncpg.create_pool(self.connection_string, min_size=5, max_size=20)
        async with self.pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS sre_embeddings (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    embedding vector({self.dimension}),
                    content TEXT,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS embedding_idx
                ON sre_embeddings
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """)

    async def upsert(self, embeddings, metadata):
        """
        將向量和中繼資料插入到 PostgreSQL 資料表中。

        Args:
            embeddings (List[List[float]]): 向量列表。
            metadata (List[Dict[str, Any]]): 中繼資料列表。

        Returns:
            bool: 操作是否成功。
        """
        await self.initialize()
        async with self.pool.acquire() as conn:
            for emb, meta in zip(embeddings, metadata):
                await conn.execute(
                    "INSERT INTO sre_embeddings (embedding, content, metadata) VALUES ($1, $2, $3)",
                    emb, meta.get("content", ""), meta
                )
        return True

    async def search(self, query_embedding, k=10):
        """
        在 PostgreSQL 中使用 pgvector 執行向量相似度搜尋。

        Args:
            query_embedding (List[float]): 查詢向量。
            k (int): 返回的結果數量。

        Returns:
            List[Dict[str, Any]]: 搜尋結果列表，包含相似度分數。
        """
        await self.initialize()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT content, metadata, 1 - (embedding <=> $1::vector) as similarity FROM sre_embeddings ORDER BY embedding <=> $1::vector LIMIT $2",
                query_embedding, k
            )
            return [dict(row) for row in rows]

    async def delete(self, ids: List[str]) -> bool:
        """
        根據 UUID 從 PostgreSQL 中刪除記錄。

        Args:
            ids (List[str]): 要刪除的記錄的 UUID 列表。

        Returns:
            bool: 操作是否成功。
        """
        await self.initialize()
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM sre_embeddings WHERE id = ANY($1::UUID[])", ids)
        return True

    async def health_check(self) -> bool:
        """
        檢查與 PostgreSQL 資料庫的連接是否正常。

        Returns:
            bool: 如果連接正常，返回 True。
        """
        try:
            await self.initialize()
            async with self.pool.acquire() as conn:
                return await conn.fetchval('SELECT 1') == 1
        except Exception:
            return False

class VertexAIBackend(VectorBackend):
    """Google Cloud Vertex AI Vector Search 的具體實現。"""

    def __init__(self, config: MemoryConfig):
        """
        初始化 Vertex AI 後端。

        Args:
            config (MemoryConfig): 包含 Vertex AI 端點和索引 ID 的配置。
        """
        self.index_endpoint = MatchingEngineIndexEndpoint(index_endpoint_name=config.vertex_index_endpoint)
        self.deployed_index_id = config.vertex_deployed_index_id

    async def upsert(self, embeddings, metadata):
        """
        將數據點（向量和中繼資料）上傳到 Vertex AI 索引。

        Args:
            embeddings (List[List[float]]): 向量列表。
            metadata (List[Dict[str, Any]]): 中繼資料列表。

        Returns:
            bool: 操作是否成功。
        """
        datapoints = [
            {"datapoint_id": str(meta.get("id", i)), "feature_vector": emb, "restricts": [{"namespace": "sre_knowledge"}]}
            for i, (emb, meta) in enumerate(zip(embeddings, metadata))
        ]
        self.index_endpoint.upsert_datapoints(datapoints)
        return True

    async def search(self, query_embedding, k=10):
        """
        在 Vertex AI 中執行近鄰搜尋。

        Args:
            query_embedding (List[float]): 查詢向量。
            k (int): 返回的結果數量。

        Returns:
            List[Dict[str, Any]]: 搜尋結果列表。
        """
        response = self.index_endpoint.find_neighbors(
            deployed_index_id=self.deployed_index_id,
            queries=[query_embedding],
            num_neighbors=k
        )
        return response[0] if response else []

    async def delete(self, ids: List[str]) -> bool:
        """
        從 Vertex AI 索引中刪除數據點。

        Args:
            ids (List[str]): 要刪除的數據點 ID 列表。

        Returns:
            bool: 操作是否成功。
        """
        self.index_endpoint.delete_datapoints(ids)
        return True

    async def health_check(self) -> bool:
        """
        檢查 Vertex AI Vector Search 端點的健康狀態。

        注意：這是一個簡化的檢查，真實場景可能需要更複雜的 API 調用。

        Returns:
            bool: 如果端點看似有效，返回 True。
        """
        try:
            return self.index_endpoint.project is not None
        except Exception:
            return False

class MemoryBackendFactory:
    """記憶體後端工廠類別。"""

    @staticmethod
    def create(config: MemoryConfig) -> VectorBackend:
        """
        根據配置，創建並返回一個對應的 VectorBackend 實例。

        Args:
            config (MemoryConfig): 包含 `backend` 名稱的配置物件。

        Raises:
            ValueError: 如果配置中指定的後端不被支援。

        Returns:
            VectorBackend: 一個具體的向量數據庫後端實例。
        """
        class InMemoryBackend(VectorBackend):
            """一個純記憶體的後端，用於本地開發和快速測試。"""
            def __init__(self):
                self.vectors = []
                self.metadata = []
            async def upsert(self, embeddings, metadata):
                self.vectors.extend(embeddings)
                self.metadata.extend(metadata)
                return True
            async def search(self, query_embedding, k=10):
                # 這是一個簡化的搜尋，不是真正的向量搜尋。
                return self.metadata[:k]
            async def delete(self, ids: List[str]) -> bool:
                return True
            async def health_check(self) -> bool:
                return True

        backend_map = {
            "weaviate": WeaviateBackend,
            "postgresql": PostgreSQLBackend,
            "vertex_ai": VertexAIBackend,
            "memory": InMemoryBackend,
            "chroma": ChromaBackend
        }
        backend_class = backend_map.get(config.backend.value)
        if not backend_class:
            raise ValueError(f"Unsupported backend: {config.backend.value}")
        if config.backend.value == "memory":
            return InMemoryBackend()
        return backend_class(config)
