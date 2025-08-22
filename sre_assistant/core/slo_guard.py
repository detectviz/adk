
# SLO 守門器：針對端到端延遲設定閾值，超過時回傳降級建議。
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class DegradeAdvice:
    # 是否應降級執行（例如跳過非必要步驟）
    should_degrade: bool
    reason: str

class SLOGuardian:
    def __init__(self, p95_ms: int = 30000):
        # 端到端 P95 目標（毫秒）
        
        self.target_ms = p95_ms

    def evaluate(self, e2e_ms: int) -> DegradeAdvice:
        
        if e2e_ms > self.target_ms:
            return DegradeAdvice(True, f"E2E {e2e_ms}ms 超過目標 {self.target_ms}ms，建議降級")
        return DegradeAdvice(False, "OK")