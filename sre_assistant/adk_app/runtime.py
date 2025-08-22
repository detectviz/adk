
# -*- coding: utf-8 -*-
# ADK 模式主入口：構建 ToolRegistry -> Coordinator(LoopAgent+BuiltInPlanner) -> 暴露 RUNNER
from __future__ import annotations
from pathlib import Path
from adk.registry import ToolRegistry
from .coordinator import build_coordinator

def get_runner():
    reg = ToolRegistry()
    if Path('tools/tools.yaml').exists():
        reg.register_from_yaml('tools/tools.yaml')
    from sre_assistant.tools.k8s_long_running import k8s_rollout_restart_long_running_tool
    from sre_assistant.tools.knowledge_ingestion import ingest_text
    from sre_assistant.tools.rag_retrieve import rag_search
    # 額外確保核心工具註冊
    reg.register('K8sRolloutRestartLongRunningTool', k8s_rollout_restart_long_running_tool)
    reg.register('ingest_text', ingest_text)
    reg.register('rag_search', rag_search)
    return build_coordinator(reg)

# 供 WSGI/ASGI 啟動時引用
RUNNER = get_runner()
