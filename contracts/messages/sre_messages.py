
# -*- coding: utf-8 -*-
# 簡化契約（繁體中文註解）。
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class ToolRequest:
    name: str
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolResponse:
    success: bool
    status: str
    message: str
    data: Any
