
# -*- coding: utf-8 -*-
# SRE 主助理：透過 bridge.exec 呼叫外部工具（繁體中文註解）。
from dataclasses import dataclass
from typing import Optional, Dict, Any
from .runtime.tool_runner import ToolRunner
from contracts.messages.sre_messages import ToolRequest

@dataclass
class IncidentInput:
    service: str
    namespace: str = "default"
    threshold: int = 80

class SREAssistant:
    def __init__(self) -> None:
        self.runner = ToolRunner(allowed={"bridge.exec"})
    def check_health(self, threshold: int = 80) -> Dict[str, Any]:
        disk = self.runner.invoke("bridge.exec", ToolRequest(name="bridge.exec", params={"category":"diagnostic","name":"check_disk","args":[threshold]}))
        mem  = self.runner.invoke("bridge.exec", ToolRequest(name="bridge.exec", params={"category":"diagnostic","name":"check_memory","args":[threshold]}))
        return {"disk": disk.__dict__, "memory": mem.__dict__}
