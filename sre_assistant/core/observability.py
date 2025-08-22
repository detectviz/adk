
# 觀測性模組：統一暴露 Prometheus 指標、結構化日誌，並預留追蹤掛鉤。
# - 指標採用 prometheus_client（使用者在 make dev 會安裝）
# - 追蹤預留 OpenTelemetry 掛鉤（可選）
import time
import json
import logging
from typing import Any, Dict

try:
    from prometheus_client import Counter, Histogram, Gauge
except Exception:
    class _Noop:
            """
            2025-08-22 03:37:34Z
            函式用途：`labels` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
            參數說明：
            - `self`：參數用途請描述。
            - `*a`：參數用途請描述。
            - `**k`：參數用途請描述。
            回傳：請描述回傳資料結構與語義。
            """
        def labels(self, *a, **k): return self
            """
            2025-08-22 03:37:34Z
            函式用途：`inc` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
            參數說明：
            - `self`：參數用途請描述。
            - `*a`：參數用途請描述。
            - `**k`：參數用途請描述。
            回傳：請描述回傳資料結構與語義。
            """
        def inc(self, *a, **k): pass
            """
            2025-08-22 03:37:34Z
            函式用途：`observe` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
            參數說明：
            - `self`：參數用途請描述。
            - `*a`：參數用途請描述。
            - `**k`：參數用途請描述。
            回傳：請描述回傳資料結構與語義。
            """
        def observe(self, *a, **k): pass
            """
            2025-08-22 03:37:34Z
            函式用途：`set` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
            參數說明：
            - `self`：參數用途請描述。
            - `*a`：參數用途請描述。
            - `**k`：參數用途請描述。
            回傳：請描述回傳資料結構與語義。
            """
        def set(self, *a, **k): pass
    Counter = Histogram = Gauge = lambda *a, **k: _Noop()

REQUEST_TOTAL = Counter("agent_requests_total", "Agent 請求總數", ["agent", "status"])
REQUEST_LATENCY = Histogram("agent_request_duration_seconds", "Agent 請求延遲（秒）", ["agent"])
TOOL_EXEC_TOTAL = Counter("tool_executions_total", "工具執行次數", ["tool", "status"])
TOOL_EXEC_LATENCY = Histogram("tool_execution_duration_seconds", "工具執行延遲（秒）", ["tool"])

logger = logging.getLogger("sre_assistant")
_handler = logging.StreamHandler()
_formatter = logging.Formatter('%(message)s')
_handler.setFormatter(_formatter)
if not logger.handlers:
    logger.addHandler(_handler)
logger.setLevel(logging.INFO)

def log_event(event: str, payload: Dict[str, Any]) -> None:
    # 以 JSON 格式輸出事件日誌，便於搜尋與分析
    
    record = {"ts": time.time(), "event": event}
    record.update(payload or {})
    logger.info(json.dumps(record, ensure_ascii=False))