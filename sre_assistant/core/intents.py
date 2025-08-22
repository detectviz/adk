# 檔案：sre_assistant/core/intents.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, Any

class Intent(BaseModel):
    type: str = Field(..., description="diagnostic|remediation|postmortem|provisioning")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.7
    raw_input: str = ""

class Step(BaseModel):
    tool: str
    args: Dict[str, Any]
    require_approval: bool = False
    timeout_seconds: int = 60

class StepResult(BaseModel):
    ok: bool
    data: Dict[str, Any] | None = None
    error_code: str | None = None
    latency_ms: int = 0
