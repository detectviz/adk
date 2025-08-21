
# -*- coding: utf-8 -*-
# SRE 主助理：透過 bridge.exec 呼叫外部工具（繁體中文註解）。
import asyncio
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

    async def check_health(self, threshold: int = 80) -> Dict[str, Any]:
        disk_task = self.runner.invoke("bridge.exec", ToolRequest(name="bridge.exec", params={"category":"diagnostic","name":"check_disk","args":[threshold]}))
        mem_task  = self.runner.invoke("bridge.exec", ToolRequest(name="bridge.exec", params={"category":"diagnostic","name":"check_memory","args":[threshold]}))

        results = await asyncio.gather(disk_task, mem_task)
        disk_result, mem_result = results

        return {"disk": disk_result.__dict__, "memory": mem_result.__dict__}
