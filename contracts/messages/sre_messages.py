
# -*- coding: utf-8 -*-
# 簡化的訊息模型，對齊 adk-references/mapping/agent_messages_software_bug.proto 的核心概念。
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class TimeRange:
    start_ms: int
    end_ms: int

@dataclass
class MetricQuery:
    promql: str
    range: Optional[TimeRange] = None

@dataclass
class LogQuery:
    logql: str
    range: Optional[TimeRange] = None
    limit: int = 200
    direction: str = "backward"

@dataclass
class ResourceSelector:
    cluster: str = ""
    namespace: str = ""
    workload: str = ""
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class ToolRequest:
    name: str
    params: Dict[str, Any] = field(default_factory=dict)
    metric: Optional[MetricQuery] = None
    log: Optional[LogQuery] = None
    k8s: Optional[ResourceSelector] = None

@dataclass
class ToolResponse:
    success: bool
    status: str
    message: str
    data: Any
