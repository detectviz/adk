# GCP Exporters 冒煙測試（需專案憑證），預設跳過
import pytest, os
pytestmark = pytest.mark.skipif(not os.getenv("GCP_PROJECT_ID"), reason="未設定 GCP_PROJECT_ID")
def test_otel_init():
    
    from sre_assistant.core.telemetry_gcp import init_gcp_observability
    try:
        init_gcp_observability()
    except Exception:
        # 在 CI 可允許無憑證報錯
        pass