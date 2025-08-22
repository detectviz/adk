
# 記憶體後端配置（長期記憶/RAG 入口）。
from __future__ import annotations

def get_memory_backend():
    """
    {ts}
    函式用途：回傳平台使用的記憶體/RAG 後端描述。
    參數說明：無。
    回傳：字典，描述記憶體後端（示例）。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    return { "type": "rag+sql", "impl": "pgvector", "module": "sre_assistant.rag" }
