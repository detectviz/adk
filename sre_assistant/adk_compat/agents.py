
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: str

class Agent:
    name: str
    instruction: str
    tools: List[str]

    def __init__(self, name: str, instruction: str = "", tools: Optional[List[str]] = None):
        self.name = name
        self.instruction = instruction or ""
        self.tools = tools or []

    async def run(self, message: str, **kwargs) -> Dict[str, Any]:
        return {"role": "assistant", "content": f"{self.name} 收到: {message}"}

class LlmAgent(Agent):
    pass

class SequentialAgent(Agent):
    def __init__(self, steps: List[Callable[..., Any]], name: str = "SequentialAgent"):
        super().__init__(name=name)
        self.steps = steps

    async def run(self, message: str, **kwargs) -> Dict[str, Any]:
        outputs = []
        for step in self.steps:
            outputs.append(step(message))
        return {"role": "assistant", "content": str(outputs)}

class LoopAgent(Agent):
    def __init__(self, agents: List[Agent], max_iterations: int = 5, name: str = "LoopAgent"):
        super().__init__(name=name)
        self.agents = agents
        self.max_iterations = max_iterations

    async def run(self, message: str, **kwargs) -> Dict[str, Any]:
        return {"role": "assistant", "content": f"LoopAgent 執行: {message}"}
