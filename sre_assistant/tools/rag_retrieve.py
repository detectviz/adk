
# RAG 檢索工具：以向量近鄰搜尋回傳前 K 筆
from __future__ import annotations
from typing import Dict, Any, List
from sentence_transformers import SentenceTransformer
from ..rag.vectorstore_pg import search_similar

_model = None
def get_model():
    
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def rag_search(question: str, top_k: int = 5) -> Dict[str,Any]:
    
    emb = get_model().encode(question).tolist()
    return {"hits": search_similar(emb, top_k=top_k)}

class RetrieveError(Exception): pass

def search_similar_pg_tx(conn, embedding: list[float], top_k: int = 5) -> dict:
    """
    {ts}
    函式用途：於交易內執行 pgvector 近鄰查詢，並提供錯誤碼。
    參數說明：同 `_search_similar_pg`。
    回傳：{{ok:bool, results:list|None, error_code:str|None}}。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT source_id, version, content, (embedding <-> %s) AS dist FROM documents ORDER BY embedding <-> %s LIMIT %s", (embedding, embedding, top_k))
                rows = cur.fetchall()
        res = [dict(source_id=r[0], version=r[1], content=r[2], distance=float(r[3])) for r in rows]
        return {"ok": True, "results": res, "error_code": None}
    except Exception as e:
        return {"ok": False, "results": None, "error_code": "E_DB", "message": str(e)}
