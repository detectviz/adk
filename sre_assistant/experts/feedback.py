
# FeedbackAgent：把一次成功的處理流程萃取為知識條目，寫入 RAG（狀態：draft）。
from __future__ import annotations
from typing import Dict, Any, List
from ..core.rag import rag_create_entry

class FeedbackAgent:
    def __init__(self, author: str = "system"):
        
        self.author = author

    def capture_runbook(self, title: str, steps: List[str], tags: list[str] | None = None) -> Dict[str, Any]:
        
        content = "\n".join(f"- {s}" for s in steps)
        entry = rag_create_entry(title=title, content=content, author=self.author, tags=tags or ["auto","runbook"], status="draft")
        return {"ok": True, "entry": entry}