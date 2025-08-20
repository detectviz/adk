# 說明：gRPC 橋接的 Python 假實作（stub），後續可替換為實際 proto 生成客戶端。

from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class TimeRange:
    start_ms: int
    end_ms: int

@dataclass
class ResourceSelector:
    cluster: str = ""
    namespace: str = ""
    workload: str = ""
    labels: Dict[str,str] = None

@dataclass
class MetricQuery:
    promql: str
    range: Optional[TimeRange] = None

@dataclass
class LogQuery:
    logql: str
    range: Optional[TimeRange] = None

@dataclass
class SreToolRequest:
    metric: Optional[MetricQuery] = None
    log: Optional[LogQuery] = None
    k8s: Optional[ResourceSelector] = None

@dataclass
class SreToolResponse:
    summary: str
    data_json: bytes

class AgentBridgeClient:
    def __init__(self, addr: str):
        self.addr = addr  # stub only

    def execute_tool(self, req: SreToolRequest) -> SreToolResponse:
        # Stub implementation. Integrate with actual gRPC in platform.
        return SreToolResponse(summary="stub", data_json=b"{}")
