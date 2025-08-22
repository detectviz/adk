
# -*- coding: utf-8 -*-
# 標準錯誤型別（對齊 ADK 工具錯誤分類語意，並保留 code 便於觀測）
from __future__ import annotations

class ToolExecutionError(Exception):
    """工具執行失敗（一般性）。"""
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

class PolicyDeniedError(Exception):
    """策略閘拒絕。"""
    def __init__(self, code: str = "E_POLICY_DENIED", message: str = "policy denied"):
        super().__init__(message); self.code = code

class HitlRejectedError(Exception):
    """HITL 拒絕或逾時。"""
    def __init__(self, code: str = "E_HITL_REJECTED", message: str = "HITL rejected or expired"):
        super().__init__(message); self.code = code


class HitlPendingError(Exception):
    """人工核可待審中。呼叫端應等待或引導前端呈現憑證表單。"""
    def __init__(self, message: str = "HITL 待審中", code: str = "E_HITL_PENDING"):
        super().__init__(message)
        self.code = code
