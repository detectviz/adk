
# -*- coding: utf-8 -*-
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
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `p95_ms`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.target_ms = p95_ms

    def evaluate(self, e2e_ms: int) -> DegradeAdvice:
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`evaluate` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `e2e_ms`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        if e2e_ms > self.target_ms:
            return DegradeAdvice(True, f"E2E {e2e_ms}ms 超過目標 {self.target_ms}ms，建議降級")
        return DegradeAdvice(False, "OK")