
# -*- coding: utf-8 -*-
# 追蹤工具：no-op 兼容 + 取得目前 trace/span id
from __future__ import annotations
from contextlib import contextmanager
from typing import Dict, Tuple

try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    _TRACER = trace.get_tracer("sre-assistant")
except Exception:
    trace = None
    _TRACER = None

@contextmanager
def start_span(name: str, attrs: Dict[str, str] | None = None):
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`start_span` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `name`：參數用途請描述。
    - `attrs`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    if _TRACER is None:
        yield None
        return
    span = _TRACER.start_span(name=name)
    if attrs:
        for k, v in list(attrs.items())[:20]:
            try:
                span.set_attribute(k, str(v)[:256])
            except Exception:
                pass
    try:
        yield span
        span.set_status(Status(StatusCode.OK))
    except Exception as e:
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.record_exception(e)
        raise
    finally:
        span.end()

def current_trace_ids() -> Tuple[str|None, str|None]:
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`current_trace_ids` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    if trace is None:
        return None, None
    try:
        span = trace.get_current_span()
        ctx = span.get_span_context()
        tid = format(ctx.trace_id, '032x') if ctx and ctx.trace_id else None
        sid = format(ctx.span_id, '016x') if ctx and ctx.span_id else None
        return tid, sid
    except Exception:
        return None, None