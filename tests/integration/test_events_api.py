# 檔案：tests/integration/test_events_api.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

import sre_assistant.server.app as appmod
from sre_assistant.core.persistence import DB, init_schema
def test_events_api_sqlite(monkeypatch):
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_events_api_sqlite` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `monkeypatch`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    monkeypatch.delenv("PG_DSN", raising=False)
    init_schema()
    DB.write_event("sessX","user","Dummy",{"a":1})
    DB.write_decision("sessX","agent","DecisionType",{"q":"x"},{"a":"y"},0.5,10)
    ev = appmod.get_session_events.__wrapped__("sessX", limit=10, _=None)
    dc = appmod.get_session_decisions.__wrapped__("sessX", limit=10, offset=0, _=None)
    assert "events" in ev and "decisions" in dc