
# E2E 測試：針對真連接的 Prometheus/K8s/Grafana 進行最小驗證
# - 透過環境變數控制是否執行：未設置對應變數時自動跳過
import os, pytest, time, uuid

from sre_assistant.tools.promql import promql_query_tool
from sre_assistant.tools.k8s import k8s_rollout_restart_tool
from sre_assistant.tools.grafana import grafana_create_dashboard_tool

pytestmark = pytest.mark.e2e

def test_prometheus_query_range():
    
    if not os.getenv("PROM_URL"):
        pytest.skip("PROM_URL 未設定，跳過")
    res = promql_query_tool("up", "instant@1699999999")
    assert "series" in res
    # 允許空結果，但不應回傳錯誤碼
    assert "error" not in (res.get("stats") or {})

def test_k8s_rollout_restart():
    
    if not os.getenv("KUBECONFIG") and os.getenv("K8S_IN_CLUSTER","").lower() not in {"1","true","yes"}:
        pytest.skip("未配置 K8s 環境，跳過")
    out = k8s_rollout_restart_tool(namespace=os.getenv("K8S_NS","default"), deployment_name=os.getenv("K8S_DEPLOY","nonexistent"), reason="e2e-test")
    # 允許因不存在而失敗，但函式需可執行並回傳字典
    assert isinstance(out, dict)

def test_grafana_create_dashboard():
    
    if not os.getenv("GRAFANA_URL") or not os.getenv("GRAFANA_TOKEN"):
        pytest.skip("Grafana 未配置，跳過")
    r = grafana_create_dashboard_tool(service_type="web")
    assert "success" in r and "elapsed_ms" in r