# 測試目標：驗證 HITL 觸發條件依 adk.yaml 與高風險命名空間運作
import os, yaml, types, importlib

def _mk_ctx():
    # 建立簡易的 ToolContext 模擬物件
    called = {}
    class Ctx:
        def __init__(self): self.session = types.SimpleNamespace(state={})
        def request_credential(self, **kw):
            called['args']=kw
    return Ctx(), called

def test_hitl_by_agent_require(tmp_path, monkeypatch):
    # 建立 adk.yaml，指定工具需審批
    yaml.safe_dump({'agent': {'tools_require_approval': ['K8sRolloutRestartLongRunningTool']}}, open('adk.yaml','w',encoding='utf-8'))
    mod = importlib.import_module('sre_assistant.tools.k8s_long_running')
    ctx, called = _mk_ctx()
    # 呼叫私有啟動函式（若為公開 API，應改呼叫公開入口）
    if hasattr(mod, '_need_hitl'):
        assert mod._need_hitl('K8sRolloutRestartLongRunningTool','dev') is True
    # 清理
    os.remove('adk.yaml')

def test_hitl_by_high_risk_namespace(monkeypatch):
    import importlib
    mod = importlib.import_module('sre_assistant.tools.k8s_long_running')
    assert mod._need_hitl('K8sRolloutRestartLongRunningTool','prod') is True
