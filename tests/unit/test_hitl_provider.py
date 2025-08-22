# 檔案：tests/unit/test_hitl_provider.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

from sre_assistant.core.hitl_provider import load_providers, get_provider
def test_load_and_get_provider():
    """
    2025-08-22 03:37:34Z
    函式用途：`test_load_and_get_provider` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    data = load_providers()
    assert isinstance(data.get("providers"), list)
    _ = get_provider("hitl-approval")