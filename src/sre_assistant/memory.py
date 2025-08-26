# src/sre_assistant/memory.py
from typing import Dict, List
from .config.config_manager import config_manager
from .memory.backend_factory import MemoryBackendFactory
from vertexai.language_models import TextEmbeddingModel

class SREMemorySystem:
    """
    記憶體系統 - 自動根據配置選擇後端。
    整合了官方的 Vertex AI 嵌入模型。
    """

    def __init__(self):
        """初始化記憶體系統"""
        # 1. 從配置管理器取得配置
        memory_config = config_manager.get_memory_config()

        # 2. 使用工廠創建後端
        self.backend = MemoryBackendFactory.create(memory_config)

        # 3. 初始化官方嵌入模型
        self.embedding_model_name = memory_config.embedding_model
        self.embedding_model = TextEmbeddingModel.from_pretrained(
            self.embedding_model_name
        )

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        使用官方 API 生成嵌入。

        Args:
            texts: 需要生成嵌入的文本列表。

        Returns:
            一個包含浮點數列表的列表，代表每個文本的嵌入。
        """
        # 使用官方 API 生成嵌入
        embeddings = self.embedding_model.get_embeddings(texts)
        return [emb.values for emb in embeddings]

    async def store_incident(self, incident_data: Dict):
        """
        儲存單個事件，包括其描述的嵌入。

        Args:
            incident_data: 包含事件資訊的字典，必須有 'description' 鍵。

        Returns:
            後端 upsert 操作的結果。
        """
        description = incident_data.get("description")
        if not description:
            raise ValueError("incident_data must contain a 'description' field.")

        # 生成嵌入
        embedding = self._generate_embeddings([description])[0]

        # 儲存到後端（自動使用配置的後端）
        return await self.backend.upsert(
            embeddings=[embedding],
            metadata=[incident_data]
        )

    async def search_similar_incidents(self, query: str, k: int = 5) -> List[Dict]:
        """
        根據查詢文本搜尋相似的事件。

        Args:
            query: 用於搜尋的查詢字符串。
            k: 返回的最相似結果的數量。

        Returns:
            一個包含相似事件的字典列表。
        """
        # 生成查詢的嵌入
        query_embedding = self._generate_embeddings([query])[0]

        # 透明地使用配置的後端進行搜尋
        return await self.backend.search(query_embedding, k=k)
