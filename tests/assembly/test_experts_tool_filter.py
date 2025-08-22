import os, yaml
from sre_assistant.adk_app.runtime import RUNNER

def test_allowlist_from_experts(tmp_path, monkeypatch):
    os.makedirs('experts', exist_ok=True)
    yaml.safe_dump({'tools_allowlist':['rag_search','K8sRolloutRestartLongRunningTool']},
                   open('experts/diagnostic.yaml','w',encoding='utf-8'))
    RUNNER.register_tools({'rag_search':object(),'promql_query':object(),'K8sRolloutRestartLongRunningTool':object()})
    mounted = RUNNER.assemble()
    assert set(mounted.keys())=={'rag_search','K8sRolloutRestartLongRunningTool'}
