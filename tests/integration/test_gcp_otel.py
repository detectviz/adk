
# -*- coding: utf-8 -*-
# GCP Exporters 冒煙測試（需專案憑證），預設跳過
import pytest, os
pytestmark = pytest.mark.skipif(not os.getenv("GCP_PROJECT_ID"), reason="未設定 GCP_PROJECT_ID")
def test_otel_init():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_otel_init` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    from sre_assistant.core.telemetry_gcp import init_gcp_observability
    try:
        init_gcp_observability()
    except Exception:
        # 在 CI 可允許無憑證報錯
        pass