from sre_assistant.rag.embeddings import get_embedding, ensure_dimension

# 知識匯入工具：將文字以嵌入後寫入 pgvector
from __future__ import annotations
from typing import Dict, Any
from sentence_transformers import SentenceTransformer
from ..rag.vectorstore_pg import upsert_document

_model = None
def get_model():
    
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")  # 正式嵌入模型
    return _model

def ingest_text(doc_id: str, text: str, metadata: Dict[str,Any]|None=None) -> Dict[str,Any]:
    
    emb = get_model().encode(text).tolist()
    upsert_document(doc_id, text, emb, metadata or {})
    return {"ok": True, "doc_id": doc_id}

class IngestError(Exception): pass

def ingest_to_pg_tx(conn, source_id: str, version: int, content: str, dim: int = 1536) -> dict:
    """
    {ts}
    函式用途：於單一交易內完成嵌入與 upsert。提供清晰錯誤碼。
    參數說明：同 `ingest_to_pg`。
    回傳：{{ok:bool, error_code:str|None}}。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    try:
        vec = ensure_dimension(get_embedding(content, dim=dim), expected=dim)
        with conn:
            with conn.cursor() as cur:
                cur.execute("""                    INSERT INTO documents(source_id, version, content, embedding)
                    VALUES (%s,%s,%s,%s)                """, (source_id, version, content, vec))
        return {"ok": True, "error_code": None}
    except Exception as e:
        return {"ok": False, "error_code": "E_DB", "message": str(e)}
