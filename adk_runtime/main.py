
# -*- coding: utf-8 -*-
# ADK Runtime：建立 ToolRegistry，按「YAML + 函式」模式顯式註冊工具。
from __future__ import annotations
import os
from sre_assistant.adk_compat.registry import ToolRegistry
from sre_assistant.tools.promql import promql_query_tool
from sre_assistant.tools.k8s import k8s_rollout_restart_tool
from sre_assistant.tools.grafana import grafana_create_dashboard_tool
from sre_assistant.tools.knowledge_ingestion import knowledge_ingestion_tool
from sre_assistant.tools.rag_retrieve import rag_retrieve_vector_tool

def build_registry() -> ToolRegistry:
    base = os.path.join(os.path.dirname(__file__), "..", "sre_assistant", "tools", "specs")
    reg = ToolRegistry()
    reg.register_from_yaml(os.path.join(base, "PromQLQueryTool.yaml"), func=promql_query_tool)
    reg.register_from_yaml(os.path.join(base, "K8sRolloutRestartTool.yaml"), func=k8s_rollout_restart_tool)
    reg.register_from_yaml(os.path.join(base, "GrafanaDashboardTool.yaml"), func=grafana_create_dashboard_tool)
    # 已存在的 YAML：KnowledgeIngestionTool.yaml 與 RAGRetrieveTool.yaml
    reg.register_from_yaml(os.path.join(base, "KnowledgeIngestionTool.yaml"), func=knowledge_ingestion_tool)
    reg.register_from_yaml(os.path.join(base, "RAGRetrieveTool.yaml"), func=rag_retrieve_vector_tool)
    return reg
