
# 合約測試：驗證 YAML 規格存在關鍵欄位且可註冊
import os, yaml
from adk_runtime.main import build_registry

def test_yaml_contracts_present():
    """
    2025-08-22 03:37:34Z
    函式用途：`test_yaml_contracts_present` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    base = os.path.join(os.path.dirname(__file__), "..", "sre_assistant", "tools", "specs")
    names = ["PromQLQueryTool.yaml","K8sRolloutRestartTool.yaml","GrafanaDashboardTool.yaml"]
    for n in names:
        p = os.path.join(base, n)
        assert os.path.exists(p), f"{n} 缺失"
        spec = yaml.safe_load(open(p, "r", encoding="utf-8"))
        for k in ["schema_version","name","description","args_schema","returns_schema","timeout_seconds"]:
            assert k in spec, f"{n} 缺少 {k}"
        assert "risk_level" in spec, f"{n} 應包含風險等級"
    reg = build_registry()
    assert "PromQLQueryTool" in reg.list_tools()