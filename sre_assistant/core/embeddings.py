
# 嵌入器（Embeddings）
# - EMBEDDER=st  → 使用 sentence-transformers（需安裝）
# - EMBEDDER=hash → 使用內建 Hash-based（離線可運作）
# - 預設依序嘗試 st，失敗則回退 hash
from __future__ import annotations
from typing import List
import os, math, hashlib, random

class BaseEmbedder:
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        
        raise NotImplementedError

class HashEmbedder(BaseEmbedder):
    def __init__(self, dim: int = 384):
        
        self.dim = dim
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        
        vecs = []
        for t in texts:
            seed = int(hashlib.sha1(t.encode("utf-8")).hexdigest()[:8], 16)
            random.seed(seed)
            v = [random.random()*2-1 for _ in range(self.dim)]
            n = math.sqrt(sum(x*x for x in v)) or 1.0
            vecs.append([x/n for x in v])
        return vecs

class STEmbedder(BaseEmbedder):
    def __init__(self, model_name: str = None):
        # 延遲匯入，避免未安裝套件報錯
        
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name or os.getenv("ST_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        
        emb = self.model.encode(texts, normalize_embeddings=True)
        return [list(map(float, row)) for row in emb]

def get_embedder() -> BaseEmbedder:
    
    prefer = os.getenv("EMBEDDER")
    if prefer == "hash":
        return HashEmbedder(dim=int(os.getenv("EMBED_DIM","384")))
    # 預設優先 st，失敗再回退
    if prefer in (None, "", "st"):
        try:
            return STEmbedder(model_name=os.getenv("ST_MODEL"))
        except Exception:
            return HashEmbedder(dim=int(os.getenv("EMBED_DIM","384")))
    return HashEmbedder(dim=int(os.getenv("EMBED_DIM","384")))