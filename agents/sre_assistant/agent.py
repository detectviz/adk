
# -*- coding: utf-8 -*-
# 說明：SRE 主助理，改用 runtime.ToolRunner 與 ToolRequest/Response（繁體中文註解）。
from dataclasses import dataclass
from typing import Optional, Dict, Any
import datetime as dt
from .runtime.tool_runner import ToolRunner
from ...contracts.messages.sre_messages import ToolRequest, MetricQuery, TimeRange, LogQuery

@dataclass
class IncidentInput:
    service: str
    namespace: str = "default"
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None
    symptom: Optional[str] = None  # e.g., 5xx surge

class SREAssistant:
    def __init__(self) -> None:
        self.runner = ToolRunner()

    def investigate(self, inc: IncidentInput) -> Dict[str, Any]:
        end_ms = inc.end_ms or int(dt.datetime.utcnow().timestamp()*1000)
        start_ms = inc.start_ms or int((dt.datetime.utcnow() - dt.timedelta(minutes=30)).timestamp()*1000)
        tr = TimeRange(start_ms=start_ms, end_ms=end_ms)

        # 1) 指標檢查（ToolRunner → Prometheus）
        promql = f'rate(http_requests_total{{service="{inc.service}",status=~"5.."}}[5m])'
        prom_req = ToolRequest(name="prom.query_range", metric=MetricQuery(promql=promql, range=tr), params={"step":"30s"})
        prom_resp = self.runner.invoke("prom.query_range", prom_req)

        # 2) 日誌比對（ToolRunner → Loki）
        logql = f'{{service="{inc.service}",namespace="{inc.namespace}"}} |= "error"'
        log_req = ToolRequest(name="loki.query_range", log=LogQuery(logql=logql, range=tr, limit=200, direction="backward"))
        log_resp = self.runner.invoke("loki.query_range", log_req)

        # 3) 叢集事件（ToolRunner → K8s）
        k8s_req = ToolRequest(name="k8s.get_events", params={}, k8s=None)
        k8s_resp = self.runner.invoke("k8s.get_events", k8s_req)

        # 4) 匯總輸出
        return {
            "service": inc.service,
            "metrics_query": promql,
            "logs_query": logql,
            "metrics_raw": prom_resp.data,
            "logs_raw": log_resp.data,
            "k8s_events": k8s_resp.data,
        }
