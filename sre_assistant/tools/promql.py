
# PromQL 查詢工具（真連接版）
# - 以 integrations.prometheus_http 呼叫 Prometheus /api/v1/query_range 或 /api/v1/query
# - 參數 range 格式："<RFC3339 start>,<RFC3339 end>,<step>"；若為 "instant@<RFC3339>" 則跑即時查詢
# - 回傳統一結構：{series: [...], stats: {...}} 或帶錯誤碼
from __future__ import annotations
from typing import Dict, Any
import time
from ..integrations.prometheus_http import PrometheusClient

def _parse_range(r: str):
    """
    2025-08-22 03:37:34Z
    函式用途：`_parse_range` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `r`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    if r.startswith("instant@"):
        ts = r.split("@",1)[1]
        return ("instant", ts, None, None)
    parts = r.split(",")
    if len(parts) != 3:
        raise ValueError("E_BAD_RANGE")
    return ("range", parts[0], parts[1], parts[2])

def promql_query_tool(query: str, range: str) -> Dict[str, Any]:
    """以 PromQL 查詢指標並回傳聚合結果（真連接 Prometheus）。"""
    client = PrometheusClient()
    mode, a, b, c = _parse_range(range)
    t0 = time.time()
    if mode == "instant":
        data, err = client.query_instant(query, ts=a)
    else:
        data, err = client.query_range(query, start=a, end=b, step=c)
    if err:
        return {"series": [], "stats": {"error": err, "elapsed_ms": int((time.time()-t0)*1000)}}
    result = data.get("data",{}).get("result",[])
    series = []
    for it in result:
        metric = it.get("metric", {})
        values = it.get("values") or []
        if it.get("value"):
            # instant 格式
            v = it["value"]
            values = [[v[0], v[1]]]
        series.append({"metric": metric, "values": values})
    return {"series": series, "stats": {"elapsed_ms": int((time.time()-t0)*1000), "result_len": len(series)}}