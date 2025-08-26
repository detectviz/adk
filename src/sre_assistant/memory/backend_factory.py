# sre_assistant/memory/backend_factory.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import weaviate
import asyncpg
from redis import Redis
from google.cloud.aiplatform.matching_engine import MatchingEngineIndexEndpoint
from ..config.config_manager import MemoryConfig

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

    async def delete(self, ids: List[str]) -> bool:
        # Weaviate delete is more complex, often by ID or filter.
        # This is a simplified placeholder.
        # For a real implementation, you'd use client.data_object.delete()
        # with the object's UUID.
        print(f"Delete functionality for Weaviate needs specific UUIDs.")
        return False

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
        if self.pool:
            return
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
        await self.initialize()
        async with self.pool.acquire() as conn:
            for emb, meta in zip(embeddings, metadata):
                await conn.execute("""
                    INSERT INTO sre_embeddings (embedding, content, metadata)
                    VALUES ($1, $2, $3)
                """, emb, meta.get("content", ""), meta)
        return True

    async def search(self, query_embedding, k=10):
        await self.initialize()
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(f"""
                SELECT content, metadata,
                       1 - (embedding <=> $1::vector) as similarity
                FROM sre_embeddings
                ORDER BY embedding <=> $1::vector
                LIMIT $2
            """, query_embedding, k)

            return [dict(row) for row in rows]

    async def delete(self, ids: List[str]) -> bool:
        await self.initialize()
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM sre_embeddings WHERE id = ANY($1::UUID[])", ids)
        return True

    async def health_check(self) -> bool:
        try:
            await self.initialize()
            async with self.pool.acquire() as conn:
                return await conn.fetchval('SELECT 1') == 1
        except Exception:
            return False


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

        # This is a synchronous method in the library, wrapping in async call
        # In a real scenario, you might use asyncio.to_thread
        self.index_endpoint.upsert_datapoints(datapoints)
        return True

    async def search(self, query_embedding, k=10):
        response = self.index_endpoint.find_neighbors(
            deployed_index_id=self.deployed_index_id,
            queries=[query_embedding],
            num_neighbors=k
        )
        # Assuming the response format provides a list of neighbors
        return response[0] if response else []

    async def delete(self, ids: List[str]) -> bool:
        self.index_endpoint.delete_datapoints(ids)
        return True

    async def health_check(self) -> bool:
        # The library doesn't provide a direct health check.
        # A simple check might involve listing indexes or a similar light operation.
        try:
            # A simple check to see if the endpoint object is valid
            return self.index_endpoint.project is not None
        except Exception:
            return False

class MemoryBackendFactory:
    """記憶體後端工廠"""

    @staticmethod
    def create(config: MemoryConfig) -> VectorBackend:
        """根據配置創建對應的後端"""

        # A local memory backend for development/testing
        class InMemoryBackend(VectorBackend):
            def __init__(self):
                self.vectors = []
                self.metadata = []
            async def upsert(self, embeddings, metadata):
                self.vectors.extend(embeddings)
                self.metadata.extend(metadata)
                return True
            async def search(self, query_embedding, k=10):
                # This is a simplistic search, not a real vector search
                return self.metadata[:k]
            async def delete(self, ids: List[str]) -> bool:
                return True
            async def health_check(self) -> bool:
                return True

        backend_map = {
            "weaviate": WeaviateBackend,
            "postgresql": PostgreSQLBackend,
            "vertex_ai": VertexAIBackend,
            "memory": InMemoryBackend
        }

        backend_class = backend_map.get(config.backend.value)
        if not backend_class:
            raise ValueError(f"Unsupported backend: {config.backend.value}")

        if config.backend.value == "memory":
            return InMemoryBackend()

        return backend_class(config)
