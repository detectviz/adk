
# -*- coding: utf-8 -*-
# 政策閘包裝器：在工具執行前做靜態檢查（等效 before_tool_callback），對齊 ADK 建議
from __future__ import annotations
from typing import Callable, Any, Dict
from .policy import evaluate_tool_call
from .errors import PolicyDeniedError
from .persistence import DB

def wrap_tool(name: str, func: Callable[..., Any]) -> Callable[..., Any]:
    # 注意：HITL 邏輯由工具內部根據 adk.yaml.policy.risk_threshold 或 tools_require_approval 決定
    # 此包裝器僅進行 allowlist 的靜態拒絕與審計記錄
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
