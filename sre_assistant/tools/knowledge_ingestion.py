
# -*- coding: utf-8 -*-
# 知識匯入工具：讀檔→分塊→嵌入→寫入 pgvector
from __future__ import annotations
from typing import List, Dict, Any, Optional
import os, re, pathlib

from ..core.vectorstore_pg import init_schema, upsert_documents, upsert_chunks

def _load_text(path: str) -> str:
    p = pathlib.Path(path)
    if not p.exists():
        raise FileNotFoundError(f"檔案不存在: {path}")
    if p.suffix.lower() in {".md",".txt",".log"}:
        return p.read_text(encoding="utf-8", errors="ignore")
    # TODO：PDF/HTML/Code 可擴充；先以純文字讀取
    return p.read_text(encoding="utf-8", errors="ignore")

def _chunk(text: str, chunk_size: int = 800, overlap: int = 120) -> List[str]:
    """簡化分塊：以段落為單位最佳努力避免切句。"""
    units = re.split(r"(\n\n+)", text)
    merged, buf = [], ""
    for u in units:
        if len(buf)+len(u) <= chunk_size: buf += u
        else: merged.append(buf.strip()); buf = u[-chunk_size:]
    if buf.strip(): merged.append(buf.strip())
    out=[]
    for i, seg in enumerate(merged):
        prefix = merged[i-1][-overlap:] if i>0 else ""
        out.append((prefix + seg) if prefix else seg)
    return [s for s in out if s.strip()]

def _ensure_embedder():
    try:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("EMBED_MODEL","sentence-transformers/all-MiniLM-L6-v2")
        return SentenceTransformer(model_name)
    except Exception:
        return None

def _embed_texts(texts: List[str]) -> List[List[float]]:
    model = _ensure_embedder()
    if model:
        return model.encode(texts, normalize_embeddings=True).tolist()
    # 回退：HashEmbedding（僅供開發用）
    dim = int(os.getenv("EMBED_DIM","384"))
    return [[(hash(t)%1000)/1000.0 for _ in range(dim)] for t in texts]

def ingest_files(paths: List[str], title: Optional[str] = None, metadata: Optional[Dict[str,Any]] = None) -> Dict[str,Any]:
    init_schema()
    docs = [{"title": title or pathlib.Path(p).name, "metadata": metadata or {}} for p in paths]
    doc_ids = upsert_documents(docs)
    total_added = total_skipped = 0
    for p, doc_id in zip(paths, doc_ids):
        text = _load_text(p)
        chunks = _chunk(text)
        embeds = _embed_texts(chunks)
        added, skipped = upsert_chunks(doc_id, chunks, embeds)
        total_added += added; total_skipped += skipped
    return {"documents": len(doc_ids), "chunks_added": total_added, "chunks_skipped": total_skipped}
