
# -*- coding: utf-8 -*-
# 工具執行統一入口：加入允許清單、輸入驗證與結構化日誌（繁體中文註解）。
import os, time
from typing import Any, Dict, Set
from ..tools import prometheus_tool as prom
from ..tools import loki_tool as loki
from ..tools import k8s_tool as k8s
from ..tools import alertmanager_tool as am
from ..tools import grafana_tool as graf
from .structured_logger import info, warn, error
from ....contracts.messages.sre_messages import ToolRequest, ToolResponse

_DEFAULT_ALLOW = {
    "prom.query", "prom.query_range",
    "loki.query_range",
    "k8s.list_pods", "k8s.get_events", "k8s.get_pod_logs",
    "graf.annotate",
    "am.list_alerts",
}

class ToolRunner:
    def __init__(self, allowed: Set[str] | None = None) -> None:
        # 允許清單可由環境變數覆寫，格式：以逗號分隔
        env_allow = os.getenv("ALLOW_TOOLS", "")
        if env_allow.strip():
            self.allowed: Set[str] = {t.strip() for t in env_allow.split(",") if t.strip()}
        else:
            self.allowed = set(_DEFAULT_ALLOW) if allowed is None else set(allowed)

    def _check_allowed(self, tool_name: str) -> None:
        if tool_name not in self.allowed:
            raise ValueError(f"工具未允許：{tool_name}（請調整 ALLOW_TOOLS 或程式設定）")

    def invoke(self, tool_name: str, req: ToolRequest) -> ToolResponse:
        self._check_allowed(tool_name)
        started = time.monotonic()
        outcome = "ok"
        try:
            # 依 tool_name 分派
            if tool_name == "prom.query":
                q = (req.metric.promql if req.metric else req.params.get("promql"))
                r = prom.query(q)
                return ToolResponse(True, "ok", "prometheus query", r)

            if tool_name == "prom.query_range":
                m = req.metric
                r = prom.query_range(m.promql,
                                     start=_ms_to_dt(m.range.start_ms),
                                     end=_ms_to_dt(m.range.end_ms),
                                     step=req.params.get("step","30s"))
                return ToolResponse(True, "ok", "prometheus range", r)

            if tool_name == "loki.query_range":
                l = req.log
                r = loki.query_range(l.logql,
                                     start=_ms_to_dt(l.range.start_ms),
                                     end=_ms_to_dt(l.range.end_ms),
                                     limit=l.limit,
                                     direction=l.direction)
                return ToolResponse(True, "ok", "loki range", r)

            if tool_name == "k8s.list_pods":
                ns = req.k8s.namespace if req.k8s else "default"
                r = k8s.list_pods(namespace=ns, label_selector=req.params.get("label_selector"))
                return ToolResponse(True, "ok", "k8s pods", r)

            if tool_name == "k8s.get_events":
                ns = req.k8s.namespace if req.k8s else "default"
                r = k8s.get_events(namespace=ns)
                return ToolResponse(True, "ok", "k8s events", r)

            if tool_name == "k8s.get_pod_logs":
                ns = req.k8s.namespace if req.k8s else "default"
                r = k8s.get_pod_logs(name=req.params["name"], namespace=ns, tail_lines=int(req.params.get("tail_lines",200)))
                return ToolResponse(True, "ok", "k8s logs", r)

            if tool_name == "graf.annotate":
                r = graf.annotate(text=req.params["text"],
                                  dashboard_uid=req.params.get("dashboard_uid"),
                                  panel_id=req.params.get("panel_id"),
                                  tags=req.params.get("tags",["sre-assistant"]))
                return ToolResponse(True, "ok", "grafana annotate", r)

            if tool_name == "am.list_alerts":
                r = am.list_alerts(req.params.get("filter",""))
                return ToolResponse(True, "ok", "alertmanager alerts", r)

            raise ValueError(f"未知工具：{tool_name}")

        except Exception as exc:
            outcome = "error"
            error("tool_invoke_error", tool=tool_name, message=str(exc))
            raise
        finally:
            duration_ms = int((time.monotonic() - started) * 1000)
            info("tool_invoke", tool=tool_name, outcome=outcome, duration_ms=duration_ms)

def _ms_to_dt(ms: int):
    import datetime as dt
    return dt.datetime.utcfromtimestamp(ms/1000.0)
