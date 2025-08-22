
# -*- coding: utf-8 -*-
# 政策閘包裝器：在工具執行前做靜態檢查（等效 before_tool_callback），對齊 ADK 建議
from __future__ import annotations
from typing import Callable, Any, Dict
from .policy import evaluate_tool_call
from .errors import PolicyDeniedError, HitlPendingError
from .persistence import DB

def wrap_tool(name: str, func: Callable[..., Any]) -> Callable[..., Any]:
    RISK_ORDER = {"Low":0, "Medium":1, "High":2, "Critical":3}
    THRESH = os.getenv("POLICY_HITL_THRESHOLD","High")
    """回傳包裝後的工具函式。執行前做政策評估，拒絕則丟出 PolicyDeniedError。
    - 若屬於需審批工具（require_approval=True），不在此阻擋，交由工具內部自行觸發 request_credential。
    - 將評估結果以 audit 事件寫入（便於追蹤與回放）。
    """
    def wrapped(*args, **kwargs):
        ok, reason, risk, require_approval = evaluate_tool_call(name, kwargs)
        # 審計紀錄（不依賴 ToolContext 以降低耦合）
        try:
            sess = kwargs.get("session_id") or kwargs.get("session") or ""
            DB.write_audit(sess or "unknown", "policy", "POLICY_EVAL", {
                "tool": name, "ok": ok, "reason": reason, "risk": risk, "require_approval": require_approval
            })
        except Exception:
            pass
        if not ok:
            raise PolicyDeniedError(f"政策拒絕：{reason}")
        # 風險達門檻或 require_approval 時，若可取得 ToolContext，先觸發 HITL，再以待審錯誤阻斷
        need_hitl = require_approval or (RISK_ORDER.get(risk,0) >= RISK_ORDER.get(THRESH,2))
        if need_hitl:
            ctx = None
            for a in args:
                if hasattr(a, "request_credential"):
                    ctx = a; break
            if ctx is None:
                for v in kwargs.values():
                    if hasattr(v, "request_credential"):
                        ctx = v; break
            if ctx is not None:
                try:
                    ctx.request_credential(prompt=f"操作 {name} 需要人工核可，風險等級={risk}", fields={"tool": name, "risk": risk, "params": kwargs})
                except Exception:
                    pass
            # 阻斷工具執行，等待前端核可流程
            raise HitlPendingError()
        return func(*args, **kwargs)
    wrapped.__name__ = getattr(func, "__name__", name)
    wrapped.__doc__ = getattr(func, "__doc__", f"policy-wrapped {name}")
    return wrapped

def wrap_tools_allowlist(tool_map: Dict[str, Callable[..., Any]], allowlist: list[str]|None) -> list[Callable[..., Any]]:
    """依 allowlist 篩選工具並套用政策包裝。allowlist 為空則保留全部。"""
    names = allowlist or list(tool_map.keys())
    out = []
    for n in names:
        if n in tool_map:
            out.append(wrap_tool(n, tool_map[n]))
    return out
