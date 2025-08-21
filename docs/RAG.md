
# RAG 向量化（pgvector）

## 需求
- PostgreSQL 15+ 與 `pgvector` 擴充
- 以環境變數 `PG_DSN` 提供連線字串

## 匯入
- 工具：`KnowledgeIngestionTool`（YAML 規格已存在）
- 實作：`sre_assistant/tools/knowledge_ingestion.py`
- 流程：切片 → 嵌入 → `rag_entries`（SQLite）與 `rag_chunks`（PG）寫入

## 檢索
- 工具：`RAGRetrieveTool`
- 實作：`sre_assistant/tools/rag_retrieve.py`
- 機制：若存在 `PG_DSN` → 使用 pgvector 相似度；否則回退 SQLite FTS5

## 嵌入器
- `core/embeddings.py` Hash-based 範例，保證離線可運作
- 生產環境建議替換為 HuggingFace/VertexAI 等嵌入模型
