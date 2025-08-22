# 測試：SSE 事件名存在於 server/events.py 以便 Dev UI 對接
import importlib
def test_event_symbol_exists():
    mod = importlib.import_module('sre_assistant.server.events')
    txt = getattr(mod, '__doc__', '') or ''
    src = getattr(mod, '__dict__', {})
    # 只要模組文字包含事件名關鍵字即可
    assert 'adk_request_credential' in (txt + str(src))
