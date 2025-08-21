
# -*- coding: utf-8 -*-
# PromQL 查詢工具（強化版）：
# 1) 嚴格檢查 Prometheus 回應的 status 與 resultType
# 2) 簡單語法健檢（在無後端時，以 PROM_STRICT=1 啟用）
# 3) 明確錯誤碼：E_BAD_QUERY / E_TIMEOUT / E_BACKEND / E_SCHEMA
from __future__ import annotations
import os, time, re
from typing import Any, Dict
from .common_http import HttpClient
from ..adk_compat.executor import ExecutionError

_BAD_TOKEN_RE = re.compile(r"[^a-zA-Z0-9_:{}()\[\]\-+/*%<>=!,\.\s]" )

def _heuristic_query_check(q: str):
    # 簡單健檢：非法字元與括號平衡
    if _BAD_TOKEN_RE.search(q):
        raise ExecutionError("E_BAD_QUERY", "疑似非法字元")
    if q.count("(") != q.count(")"):
        raise ExecutionError("E_BAD_QUERY", "括號不平衡")

def promql_query_tool(query: str, range: str) -> Dict[str, Any]:
    if not query or not isinstance(query, str):
        raise ExecutionError("E_BAD_QUERY", "查詢語句不可為空")
    parts = range.split(",") if range else []
    if len(parts) != 3:
        raise ExecutionError("E_SCHEMA", "range 需為 start,end,step 三段 RFC3339 與步長")
    start, end, step = parts

    base = os.getenv("PROM_BASE_URL")
    strict = os.getenv("PROM_STRICT", "0") == "1"
    mock = os.getenv("PROM_MOCK", "1") == "1" or not base

    if mock:
        if strict:
            _heuristic_query_check(query)
        # 模擬輸出
        now = int(time.time())
        values = [[now - i*15, 1.0] for i in range(4)][::-1]
        return {"series": [{"metric": {"__name__": query}, "values": values}], "stats": {"samples": len(values), "elapsed_ms": 3}}

    client = HttpClient(base_url=base)
    data = client.get("/api/v1/query_range", params={"query": query, "start": start, "end": end, "step": step})
    # 檢查 status 與錯誤
    status = data.get("status")
    if status == "error":
        e_type = data.get("errorType","")
        e_msg  = data.get("error","未知錯誤")
        if e_type == "bad_data":
            raise ExecutionError("E_BAD_QUERY", e_msg)
        raise ExecutionError("E_BACKEND", f"{e_type}: {e_msg}")
    if status != "success":
        raise ExecutionError("E_BACKEND", f"非 success：{status}")

    d = data.get("data", {})
    rtype = d.get("resultType", "matrix")
    if rtype != "matrix":
        raise ExecutionError("E_SCHEMA", f"resultType 應為 matrix，實得 {rtype}")
    result = d.get("result", [])
    return {
        "series": [{"metric": r.get("metric", {}), "values": r.get("values", [])} for r in result],
        "stats": {"samples": sum(len(r.get("values", [])) for r in result), "elapsed_ms": int(d.get("elapsed", 0)*1000) if isinstance(d.get("elapsed"), (int,float)) else None}
    }
