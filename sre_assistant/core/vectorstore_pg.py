
# -*- coding: utf-8 -*-
# pgvector 向量儲存與檢索（最小可運行版）
# - 以 PG_DSN 連線 PostgreSQL（需安裝 pgvector 擴充）
# - 自動建立資料表與 IVFFlat 索引（cosine）
# - 以 content 的 SHA256 作為去重鍵；提供批量 upsert 與近鄰查詢
from __future__ import annotations
from typing import List, Dict, Any, Iterable, Optional, Tuple
import os, uuid, hashlib, contextlib

try:
    import psycopg
    from psycopg.rows import dict_row
except Exception:
    psycopg = None  # 未安裝時拋出於使用階段

EMBED_DIM = int(os.getenv("EMBED_DIM","384"))
PG_DSN = os.getenv("PG_DSN", "")

@contextlib.contextmanager
def _conn():
    # 建立同步連線；若缺依賴或 DSN，於呼叫端明確報錯
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`_conn` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    if not psycopg or not PG_DSN:
        raise RuntimeError("缺少 psycopg 或 PG_DSN 未設定，無法連線 PostgreSQL。")
    with psycopg.connect(PG_DSN, row_factory=dict_row) as c:
        yield c

def init_schema() -> None:
    """建立 extension / tables / indexes（若不存在）。"""
    with _conn() as c, c.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS documents (
          id UUID PRIMARY KEY,
          title TEXT,
          metadata JSONB DEFAULT '{}'::jsonb,
          created_at TIMESTAMPTZ DEFAULT now()
        );""")
        cur.execute(f"""
        CREATE TABLE IF NOT EXISTS chunks (
          id UUID PRIMARY KEY,
          doc_id UUID REFERENCES documents(id) ON DELETE CASCADE,
          content TEXT NOT NULL,
          content_hash TEXT NOT NULL,
          embedding vector({EMBED_DIM}) NOT NULL,
          metadata JSONB DEFAULT '{{}}'::jsonb,
          created_at TIMESTAMPTZ DEFAULT now()
        );""")
        # 以 cosine 相似度，IVFFlat 索引
        lists = int(os.getenv("PGVECTOR_LISTS","100"))
        cur.execute(f"CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = {lists});")
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_chunks_content_hash ON chunks(content_hash);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON chunks(doc_id);")
        c.commit()

def _hash(text: str) -> str:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`_hash` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `text`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def upsert_documents(docs: Iterable[Dict[str,Any]]) -> List[str]:
    """插入 documents 並回傳 id 清單。doc 欄位：title, metadata。"""
    ids=[]
    with _conn() as c, c.cursor() as cur:
        for d in docs:
            did = uuid.uuid4()
            cur.execute("INSERT INTO documents(id,title,metadata) VALUES(%s,%s,%s) RETURNING id;",
                        (did, d.get("title"), d.get("metadata", {})))
            ids.append(str(cur.fetchone()["id"]))
        c.commit()
    return ids

def upsert_chunks(doc_id: str, texts: List[str], embeds: List[List[float]], metadatas: Optional[List[Dict[str,Any]]] = None) -> Tuple[int,int]:
    """批量 upsert；以 content_hash 做去重。回傳 (新增數, 跳過數)。"""
    metadatas = metadatas or [{} for _ in texts]
    added=skipped=0
    with _conn() as c, c.cursor() as cur:
        for t,e,m in zip(texts, embeds, metadatas):
            h=_hash(t)
            try:
                cur.execute("INSERT INTO chunks(id,doc_id,content,content_hash,embedding,metadata) VALUES(%s,%s,%s,%s,%s,%s)",
                    (uuid.uuid4(), uuid.UUID(doc_id), t, h, e, m))
                added+=1
            except Exception:
                skipped+=1
        c.commit()
    return added, skipped

def search_similar(query_embed: List[float], top_k: int = 8, distance_threshold: float = 0.4) -> List[Dict[str,Any]]:
    """以 cosine 近鄰檢索；回傳 [{doc_id, content, metadata, score}]。"""
    with _conn() as c, c.cursor() as cur:
        cur.execute("""
            SELECT doc_id, content, metadata, 1 - (embedding <-> %s) AS score
            FROM chunks
            ORDER BY embedding <-> %s
            LIMIT %s;
        """, (query_embed, query_embed, top_k))
        rows = cur.fetchall()
    return [dict(r) for r in rows if float(r.get("score",0)) >= (1.0 - distance_threshold)]