
from __future__ import annotations
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ExpertConf(BaseModel):
    model: Optional[str] = None
    tools_allowlist: Optional[List[str]] = None
    prompt: Optional[str] = None
    slo: Optional[Dict[str, float]] = None

class AgentConf(BaseModel):
    model: str = Field(...)
    tools_allowlist: Optional[List[str]] = None
    tools_require_approval: Optional[List[str]] = None

class RunnerConf(BaseModel):
    max_iterations: int = Field(ge=1, default=10)

class Config(BaseModel):
    agent: AgentConf
    runner: RunnerConf = RunnerConf()
    experts: Dict[str, ExpertConf] = {}

def main()->int:
    data = yaml.safe_load(Path("adk.yaml").read_text(encoding="utf-8")) or {}
    try:
        Config(**data); print("adk.yaml schema OK"); return 0
    except Exception as e:
        print("schema invalid:", e); return 2

if __name__ == "__main__": import sys; sys.exit(main())
