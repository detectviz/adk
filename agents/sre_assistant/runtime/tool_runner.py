
# -*- coding: utf-8 -*-
# 工具執行分派器，含允許清單與橋接（繁體中文註解）。
import os, time
from typing import Set
from .structured_logger import info, warn, error
from .bridge_client import BridgeClient
from contracts.messages.sre_messages import ToolRequest, ToolResponse

_DEFAULT_ALLOW = {"bridge.exec"}

class ToolRunner:
    def __init__(self, allowed: Set[str] | None = None) -> None:
        self.bridge = BridgeClient()
        env_allow = os.getenv("ALLOW_TOOLS","").strip()
        self.allowed = set(_DEFAULT_ALLOW) if not env_allow else {t.strip() for t in env_allow.split(",") if t.strip()}
        if allowed is not None: self.allowed |= set(allowed)
    def _check_allowed(self, tool_name: str) -> None:
        if tool_name not in self.allowed:
            raise ValueError(f"工具未允許：{tool_name}")
    async def invoke(self, tool_name: str, req: ToolRequest) -> ToolResponse:
        self._check_allowed(tool_name)
        started = time.monotonic()
        try:
            if tool_name == "bridge.exec":
                cat = req.params.get("category"); name = req.params.get("name"); args = req.params.get("args", [])
                if not isinstance(args, list): args = [str(args)]
                result = await self.bridge.exec(str(cat), str(name), *[str(a) for a in args])
                return ToolResponse(True, result.get("status","ok"), result.get("message",""), result.get("data"))
            raise ValueError(f"未知工具：{tool_name}")
        finally:
            dur = int((time.monotonic()-started)*1000)
            info("tool_invoke", tool=tool_name, duration_ms=dur)
