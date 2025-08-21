
# 遷移指引

## SQLite 追蹤欄位
- v12 新增 decisions/tool_executions 的 `trace_id`、`span_id` 欄位。
- 程式會於啟動時嘗試 `ALTER TABLE` 新增，舊資料不受影響。

## PostgreSQL
- `sre_assistant/core/persistence_pg.py` 提供等價 schema，請以 Alembic 或手動 SQL 進行遷移。
- RAG `rag_chunks` 表由 `core/vectorstore_pg.py` 初始化（需 `CREATE EXTENSION vector`）。
