
# -*- coding: utf-8 -*-
# 啟動時載入工具描述檔並註冊
from __future__ import annotations
from adk.registry import ToolRegistry
from sre_assistant.tools.k8s_long_running import k8s_rollout_restart_long_running_tool
from sre_assistant.tools.knowledge_ingestion import ingest_text
from sre_assistant.tools.rag_retrieve import rag_search

def bootstrap_registry() -> ToolRegistry:
    reg = ToolRegistry()
    reg.register_from_yaml('tools/tools.yaml', func=k8s_rollout_restart_long_running_tool)
    reg.register('ingest_text', ingest_text)
    reg.register('rag_search', rag_search)
    return reg

REGISTRY = bootstrap_registry()

if __name__ == "__main__":
    print("Registered tools:", REGISTRY.list())
