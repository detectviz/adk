
# -*- coding: utf-8 -*-
# 設定模組：集中管理環境變數與預設值
import os

class Config:
    HOST: str = os.getenv("SRE_API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("SRE_API_PORT", "8000"))
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "/mnt/data/sre_assistant.db")
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "1") == "1"
    ENABLE_TRACING: bool = os.getenv("ENABLE_TRACING", "0") == "1"
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    RAG_CORPUS: str | None = os.getenv("RAG_CORPUS")
    RATE_CAPACITY: int = int(os.getenv("RATE_CAPACITY", "120"))
    RATE_REFILL: float = float(os.getenv("RATE_REFILL", "2.0"))
    DEBOUNCE_TTL: int = int(os.getenv("DEBOUNCE_TTL", "10"))
    CACHE_TTL_DEFAULT: int = int(os.getenv("CACHE_TTL_DEFAULT", "20"))
