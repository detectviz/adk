
# -*- coding: utf-8 -*-
# PromQL 查詢工具：優先使用環境變數連線真實 Prometheus；若未設定則回傳模擬資料。
from __future__ import annotations
import os, time
from typing import Any, Dict, List
from .common_http import HttpClient
from ..adk_compat.executor import ExecutionError

def promql_query_tool(query: str, range: str) -> Dict[str, Any]:
    """
    以 Prometheus HTTP API 的 /api/v1/query_range 進行查詢。
    參數：
      - query: PromQL 字串
      - range: RFC3339 時間範圍，例如：2025-08-01T00:00:00Z,2025-08-01T01:00:00Z,15s
    回傳：
      - series: 時間序列陣列（每列包含 metric 與 values）
      - stats: 查詢統計資訊（樣本量、耗時）
    例外：拋出 ExecutionError(E_BAD_QUERY/E_TIMEOUT/E_BACKEND/E_SCHEMA)
    """
    if not query or not isinstance(query, str):
        raise ExecutionError("E_BAD_QUERY", "查詢語句不可為空")
    parts = range.split(",") if range else []
    if len(parts) != 3:
        raise ExecutionError("E_SCHEMA", "range 需為 start,end,step 三段 RFC3339 與步長")

    base = os.getenv("PROM_BASE_URL")
    mock = os.getenv("PROM_MOCK", "1") == "1" or not base
    if mock:
        # 模擬輸出：提供簡單的 series 與統計資料
        now = int(time.time())
        values = [[now - i*15, 1.0] for i in range(4)][::-1]
        return {
            "series": [{"metric": {"__name__": query}, "values": values}],
            "stats": {"samples": len(values), "elapsed_ms": 3}
        }

    client = HttpClient(base_url=base)
    start, end, step = parts
    # Prometheus API 的 query_range 參數
    data = client.get("/api/v1/query_range", params={"query": query, "start": start, "end": end, "step": step})
    if data.get("status") != "success":
        raise ExecutionError("E_BACKEND", f"Prometheus 回傳非 success：{data}")
    result = data.get("data", {}).get("result", [])
    # 正規化輸出格式
    return {
        "series": [{"metric": r.get("metric", {}), "values": r.get("values", [])} for r in result],
        "stats": {"samples": sum(len(r.get("values", [])) for r in result), "elapsed_ms": data.get("data", {}).get("resultType", "matrix")}
    }
