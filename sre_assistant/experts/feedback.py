
# -*- coding: utf-8 -*-
# FeedbackAgent：把一次成功的處理流程萃取為知識條目，寫入 RAG（狀態：draft）。
from __future__ import annotations
from typing import Dict, Any, List
from ..core.rag import rag_create_entry

class FeedbackAgent:
    def __init__(self, author: str = "system"):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `author`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.author = author

    def capture_runbook(self, title: str, steps: List[str], tags: list[str] | None = None) -> Dict[str, Any]:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`capture_runbook` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `title`：參數用途請描述。
        - `steps`：參數用途請描述。
        - `tags`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        content = "\n".join(f"- {s}" for s in steps)
        entry = rag_create_entry(title=title, content=content, author=self.author, tags=tags or ["auto","runbook"], status="draft")
        return {"ok": True, "entry": entry}