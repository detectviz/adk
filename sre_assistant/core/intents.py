
# -*- coding: utf-8 -*-
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
