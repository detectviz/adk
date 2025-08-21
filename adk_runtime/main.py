
# -*- coding: utf-8 -*-
from __future__ import annotations
from sre_assistant.adk_compat.registry import ToolRegistry
from sre_assistant.tools.promql import promql_query_tool
from sre_assistant.tools.k8s import k8s_rollout_restart_tool
from sre_assistant.tools.grafana import grafana_create_dashboard_tool
from sre_assistant.tools.runbook import runbook_lookup_tool
from sre_assistant.core.rag import knowledge_ingestion_tool, rag_retrieve_tool
import os

def build_registry() -> ToolRegistry:
    base = os.path.join(os.path.dirname(__file__), "..", "sre_assistant", "tools", "specs")
    reg = ToolRegistry()
    reg.register_from_yaml(os.path.join(base, "PromQLQueryTool.yaml"), func=promql_query_tool)
    reg.register_from_yaml(os.path.join(base, "K8sRolloutRestartTool.yaml"), func=k8s_rollout_restart_tool)
    reg.register_from_yaml(os.path.join(base, "GrafanaDashboardTool.yaml"), func=grafana_create_dashboard_tool)
    reg.register_from_yaml(os.path.join(base, "RunbookLookupTool.yaml"), func=runbook_lookup_tool)
    reg.register_from_yaml(os.path.join(base, "KnowledgeIngestionTool.yaml"), func=knowledge_ingestion_tool)
    reg.register_from_yaml(os.path.join(base, "RAGRetrieveTool.yaml"), func=rag_retrieve_tool)
    return reg
