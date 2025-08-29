# src/sre_assistant/memory/chroma_backend.py
"""
此檔案實現了 ChromaDB 作為向量數據庫後端的具體邏輯。

它遵循由 `VectorBackend` 定義的統一介面，使得 SRE Assistant
的長期記憶體 (RAG) 功能可以無縫地使用 ChromaDB 作為其
底層的向量儲存和搜尋引擎。
"""

from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer

from .backend_factory import VectorBackend
from ..config.config_manager import MemoryConfig

class ChromaBackend(VectorBackend):
    """
    使用 ChromaDB 的向量數據庫後端實現。
    這是一個輕量級、本地優先的向量數據庫，適合快速開發和部署。
    """

    def __init__(self, config: MemoryConfig):
        """
        初始化 ChromaDB 後端。

        Args:
            config (MemoryConfig): 包含嵌入模型等相關配置。
        """
        # 1. 初始化 ChromaDB 客戶端
        #    - 使用 `PersistentClient` 將數據持久化到磁碟
        #    - 數據將儲存在 `./chroma_db` 目錄下
        self.client = chromadb.PersistentClient(path="./chroma_db")

        # 2. 初始化句子轉換器模型，用於將文本轉換為向量
        #    - 使用配置中指定的模型，例如 'multi-qa-MiniLM-L6-cos-v1'
        self.embedding_model = SentenceTransformer(config.embedding_model)

        # 3. 獲取或創建一個 ChromaDB 集合 (Collection)
        #    - 集合類似於 SQL 中的資料表
        #    - 我們使用配置中指定的 class_name，預設為 "SREKnowledge"
        self.collection_name = config.weaviate_class_name  # 重用 weaviate_class_name
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # 指定使用餘弦相似度
        )

    async def upsert(self, embeddings: List[List[float]],
                    metadata: List[Dict[str, Any]]) -> bool:
        """
        將向量和中繼資料批量插入或更新到 ChromaDB 集合中。

        Args:
            embeddings (List[List[float]]): 要插入的向量列表。
            metadata (List[Dict[str, Any]]): 與每個向量對應的中繼資料列表。

        Returns:
            bool: 操作是否成功。
        """
        ids = [str(meta.get("id", i)) for i, meta in enumerate(metadata)]
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadata
        )
        return True

    async def search(self, query_embedding: List[float],
                    k: int = 10) -> List[Dict[str, Any]]:
        """
        在 ChromaDB 中執行向量相似度搜尋。

        Args:
            query_embedding (List[float]): 用於查詢的單個向量。
            k (int): 要返回的相似結果數量。

        Returns:
            List[Dict[str, Any]]: 搜尋結果列表，包含中繼資料和相似度分數。
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        # 結果格式轉換，以符合應用程式的預期
        # ChromaDB 返回的 `results` 是一個包含 `ids`, `distances`, `metadatas` 等鍵的字典
        if not results or not results.get('ids'):
            return []

        # results 字典中的每個值都是一個列表的列表，因為可以同時查詢多個向量
        # 我們只查詢了一個，所以取第一個元素 `[0]`
        ids = results['ids'][0]
        distances = results['distances'][0]
        metadatas = results['metadatas'][0]

        # 將結果組合成應用程式期望的格式
        output = []
        for i, doc_id in enumerate(ids):
            meta = metadatas[i]
            meta['id'] = doc_id
            meta['similarity'] = 1 - distances[i]  # 將距離轉換為相似度
            output.append(meta)

        return output


    async def delete(self, ids: List[str]) -> bool:
        """
        根據 ID 從 ChromaDB 集合中刪除向量。

        Args:
            ids (List[str]): 要刪除的向量的唯一 ID 列表。

        Returns:
            bool: 操作是否成功。
        """
        self.collection.delete(ids=ids)
        return True

    async def health_check(self) -> bool:
        """
        檢查 ChromaDB 後端的健康狀況。
        對於本地 ChromaDB，我們主要檢查心跳 (heartbeat)。

        Returns:
            bool: 如果後端服務健康，返回 True。
        """
        try:
            # `heartbeat()` 返回一個時間戳（奈秒），如果服務正常則表示健康
            return self.client.heartbeat() is not None
        except Exception:
            return False
