
# -*- coding: utf-8 -*-
# 檔案：sre_assistant/rag/embeddings.py
# 角色：統一嵌入向量生成介面，支援 Vertex AI 與 Hash 後備；並提供維度驗證工具。
from __future__ import annotations
import os, hashlib, struct
from typing import List

def _hash_embedding(text: str, dim: int = 1536) -> List[float]:
    """
    自動產生註解時間：{ts}
    函式用途：以穩定 hash 方式產生固定維度的偽嵌入向量（測試/離線）。
    參數說明：
    - `text`：輸入文字。
    - `dim`：向量維度。
    回傳：`List[float]` 長度為 dim。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    out = [0.0]*dim
    # 簡易 rolling hash → 映射到 dim
    for i,ch in enumerate(text.encode('utf-8')):
        idx = i % dim
        out[idx] += ((ch/255.0) - 0.5)
    return out

def _vertexai_embedding(text: str, model: str = "textembedding-gecko@001") -> list[float]:
    """
    自動產生註解時間：{ts}
    函式用途：呼叫 Vertex AI Embeddings 取得向量（若環境未安裝套件或認證不可用則丟出例外）。
    參數說明：
    - `text`：輸入文字。
    - `model`：嵌入模型名稱，預設 gecko（範例）。
    回傳：向量陣列。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    # 依照當前 Vertex AI Python SDK（`google-cloud-aiplatform`）的常見用法
    try:
        from google.cloud import aiplatform
        aiplatform.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
        from vertexai.language_models import TextEmbeddingModel
        mdl = TextEmbeddingModel.from_pretrained(model)
        emb = mdl.get_embeddings([text])[0].values
        return list(emb)
    except Exception as e:
        raise RuntimeError(f"Vertex AI Embeddings 呼叫失敗：{e}")

def get_embedding(text: str, dim: int = 1536) -> list[float]:
    """
    自動產生註解時間：{ts}
    函式用途：根據環境變數選擇嵌入實作，預設使用 Vertex AI，失敗則回退 hash。
    參數說明：
    - `text`：輸入文字。
    - `dim`：期望的向量維度（用於後備 hash 與維度檢查）。
    回傳：`list[float]`。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    provider = os.getenv("RAG_EMBEDDINGS_PROVIDER","vertexai").lower()
    if provider == "vertexai":
        try:
            v = _vertexai_embedding(text, os.getenv("RAG_VERTEX_MODEL","text-embedding-005"))
            return v
        except Exception:
            # 回退 hash 嵌入，避免中斷流程
            return _hash_embedding(text, dim=dim)
    return _hash_embedding(text, dim=dim)

def ensure_dimension(vec: list[float], expected: int) -> list[float]:
    """
    自動產生註解時間：{ts}
    函式用途：確保向量長度符合 pgvector 欄位維度；不足則補 0，過長則截斷。
    參數說明：
    - `vec`：原始向量。
    - `expected`：預期維度。
    回傳：長度為 expected 的向量。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    if len(vec) == expected: 
        return vec
    if len(vec) > expected:
        return vec[:expected]
    return vec + [0.0]*(expected - len(vec))
