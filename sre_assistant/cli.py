
# -*- coding: utf-8 -*-
from __future__ import annotations
import asyncio, sys, json
from .core.assistant import SREAssistant
from ..adk_runtime.main import build_registry

async def main():
    registry = build_registry()
    assistant = SREAssistant(registry)
    message = " ".join(sys.argv[1:]) or "diagnose orders latency"
    res = await assistant.chat(message)
    print(json.dumps(res, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
