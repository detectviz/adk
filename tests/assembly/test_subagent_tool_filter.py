
def test_filter_uses_subagent_tool_lists():
    from sre_assistant.adk_app.assembly import gather_subagent_tool_allowlist
    allow = gather_subagent_tool_allowlist()
    assert "rag_search" in allow and "K8sRolloutRestartLongRunningTool" in allow
