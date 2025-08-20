# 說明：SRE 主助理（簡化），以工具呼叫為核心並加入繁體中文註解。

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from .tools import prometheus_tool as prom
from .tools import loki_tool as loki
from .tools import k8s_tool as k8s
from .tools import alertmanager_tool as am
from .tools import grafana_tool as graf

@dataclass
class IncidentInput:
    service: str
    namespace: str = "default"
    cluster: str = "cluster-1"
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None
    symptom: Optional[str] = None  # e.g., 5xx surge

class SREAssistant:
    """簡化版 SRE Agent。以工具呼叫為核心，不依賴外部 ADK。"""

    def investigate(self, inc: IncidentInput) -> Dict[str, Any]:
        # 1) 指標檢查
        q = f'rate(http_requests_total{{service="{inc.service}",status=~"5.."}}[5m])'
        import datetime as _dt
        end = _dt.datetime.utcfromtimestamp((inc.end_ms or 0)/1000.0) if inc.end_ms else _dt.datetime.utcnow()
        start = _dt.datetime.utcfromtimestamp((inc.start_ms or 0)/1000.0) if inc.start_ms else end - _dt.timedelta(minutes=30)
        m = prom.query_range(q, start=start, end=end, step="30s")

        # 2) 日誌比對
        lq = f'{ {{"service": "{inc.service}", "namespace": "{inc.namespace}"}} } |= "error"'
        logs = loki.query_range(str(lq), start=start, end=end, limit=200, direction="backward")

        # 3) 叢集事件
        events = k8s.get_events(namespace=inc.namespace)

        # 4) 匯總
        summary = {
            "service": inc.service,
            "metrics_query": q,
            "logs_filter": lq,
            "metrics_raw": m,
            "logs_raw": logs,
            "k8s_events": events,
        }
        return summary

    def annotate(self, text: str, dashboard_uid: Optional[str] = None, panel_id: Optional[int] = None) -> Dict[str, Any]:
        return graf.annotate(text=text, dashboard_uid=dashboard_uid, panel_id=panel_id, tags=["sre-assistant"])

    def list_alerts(self, selector: str = "") -> List[Dict[str, Any]]:
        return am.list_alerts(selector)
