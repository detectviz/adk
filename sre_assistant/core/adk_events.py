
# ADK 事件嚴格型別解析器：將 Runner 串流事件統一為標準種類，避免啟發式歧義
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

# 定義標準事件種類（與 ADK 常見命名對齊）
AGENT_STARTED = "AgentStarted"
AGENT_FINISHED = "AgentFinished"
TOOL_CALL_STARTED = "ToolCallStarted"
TOOL_CALL_FINISHED = "ToolCallFinished"
REQUEST_CREDENTIAL = "RequestCredential"
PLANNER_PLAN_CREATED = "PlannerPlanCreated"

KNOWN_TYPES = {AGENT_STARTED, AGENT_FINISHED, TOOL_CALL_STARTED, TOOL_CALL_FINISHED, REQUEST_CREDENTIAL, PLANNER_PLAN_CREATED,
    'FunctionCallStarted','FunctionCallFinished','AgentError','PlannerStarted','PlannerFinished'}

def _extract_event_type(e: Any) -> str:
    """嚴格提取事件型別：優先 class 名稱，其次 e.type 或 e.name。"""
    # 1) 類名
    t = e.__class__.__name__
    if t in KNOWN_TYPES:
        return t
    # 2) 欄位 'type'
    t2 = getattr(e, "type", None) or getattr(e, "event_type", None)
    if isinstance(t2, str) and t2 in KNOWN_TYPES:
        return t2
    # 3) 欄位 'name'
    n = getattr(e, "name", None)
    if isinstance(n, str) and n in KNOWN_TYPES:
        return n
    return t  # 回傳類名便於偵錯

def _to_dict(e: Any) -> Dict[str, Any]:
    if hasattr(e, "to_dict"):
        try: return e.to_dict()
        except Exception: pass
    try:
        return dict(e.__dict__)
    except Exception:
        return {"_repr": repr(e)}

@dataclass
class DecisionRecord:
    agent_name: str
    decision_type: str
    input_json: Dict[str, Any]
    output_json: Dict[str, Any]
    latency_ms: Optional[int] = None

def extract_decision(e: Any) -> Optional[DecisionRecord]:
    """僅在屬於『決策邊界事件』時回傳 DecisionRecord。"""
    et = _extract_event_type(e)
    d = _to_dict(e)
    # AgentFinished：視為一次完整決策完成
    if et == AGENT_FINISHED:
        agent_name = d.get("agent",{}).get("name") or d.get("agent_name") or "main"
        # input 可取該 agent 的輸入或上一步上下文（此處保留事件全貌）
        input_json = {k:v for k,v in d.items() if k not in ("output","result","latency_ms")}
        output_json = d.get("output") or d.get("result") or {}
        return DecisionRecord(agent_name, et, input_json, output_json, d.get("latency_ms"))
    # ToolCallFinished：視為工具級決策
    if et == TOOL_CALL_FINISHED:
        tool = d.get("tool",{}) or {}
        agent_name = d.get("agent",{}).get("name") or "main"
        input_json = {"tool": tool, "args": d.get("args")}
        output_json = {"result": d.get("result"), "error": d.get("error")}
        return DecisionRecord(agent_name, et, input_json, output_json, d.get("latency_ms"))
        if et == 'FunctionCallFinished':
        agent_name = d.get('agent',{}).get('name') or 'main'
        input_json = {"function": d.get('function'), "args": d.get('args')}
        output_json = {"result": d.get('result'), "error": d.get('error')}
        return DecisionRecord(agent_name, et, input_json, output_json, d.get('latency_ms'))
    return None

def is_request_credential(e: Any) -> bool:
    return _extract_event_type(e) == REQUEST_CREDENTIAL

def coerce_sse_payload(e: Any) -> Dict[str, Any]:
    """將事件轉換為 SSE 傳輸的安全 JSON（含明確 type）。"""
    d = _to_dict(e)
    d["type"] = _extract_event_type(e)
    return d
