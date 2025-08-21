
# -*- coding: utf-8 -*-
# 工具執行器：包裝 ToolRegistry 的呼叫，加入輸入/輸出驗證、超時與重試，並映射錯誤碼。
from __future__ import annotations
import time, threading, queue
from typing import Any, Dict
from .registry import ToolRegistry, ToolSpecError
from ..core.observability import TOOL_EXEC_TOTAL, TOOL_EXEC_LATENCY, log_event
try:
    import jsonschema
except Exception:
    jsonschema = None  # 若未安裝，則僅做必要欄位檢查

class ExecutionError(Exception):
    # 執行時錯誤：攜帶標準化錯誤碼以便 StepResult 呈現
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)

class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def _validate(self, schema: Dict[str, Any], data: Dict[str, Any], role: str, tool: str):
        if jsonschema and schema:
            try:
                jsonschema.validate(instance=data, schema=schema)
            except Exception as e:
                raise ExecutionError("E_SCHEMA", f"{role} 驗證失敗: {tool}: {e}")

    def _run_with_timeout(self, fn, kwargs: Dict[str, Any], timeout: int):
        q: "queue.Queue[Any]" = queue.Queue()

        def _target():
            try:
                q.put((True, fn(**kwargs)))
            except Exception as e:
                q.put((False, e))

        t = threading.Thread(target=_target, daemon=True)
        t.start()
        try:
            ok, val = q.get(timeout=timeout)
            if ok:
                return val
            if isinstance(val, ExecutionError):
                raise val
            raise ExecutionError("E_BACKEND", f"工具內部例外: {val}")
        except queue.Empty:
            raise ExecutionError("E_TIMEOUT", f"工具執行逾時（{timeout}s）")

    def invoke(self, name: str, spec: Dict[str, Any], **kwargs):
        # 輸入驗證
        self._validate(spec.get("args_schema", {}), kwargs, "輸入", name)

        timeout = int(spec.get("timeout_seconds", 30))
        retry = spec.get("retry", {"max_retries": 0})
        max_retries = int(retry.get("max_retries", 0))

        attempt = 0
        while True:
            attempt += 1
            TOOL_EXEC_TOTAL.labels(tool=name, status="attempt").inc()
            t0 = time.time()
            try:
                entry = self.registry.require(name)
                fn = entry["func"]
                out = self._run_with_timeout(fn, kwargs, timeout=timeout)
                if isinstance(out, dict):
                    self._validate(spec.get("returns_schema", {}), out, "輸出", name)
                TOOL_EXEC_TOTAL.labels(tool=name, status="ok").inc()
                TOOL_EXEC_LATENCY.labels(tool=name).observe(time.time() - t0)
                log_event("tool.invoke.ok", {"tool": name})
                return out
            except ExecutionError as e:
                TOOL_EXEC_TOTAL.labels(tool=name, status=e.code).inc()
                TOOL_EXEC_LATENCY.labels(tool=name).observe(time.time() - t0)
                log_event("tool.invoke.error", {"tool": name, "error": e.code, "message": str(e), "attempt": attempt})
                if attempt > max_retries:
                    raise
            except Exception as e:
                TOOL_EXEC_TOTAL.labels(tool=name, status="error").inc()
                TOOL_EXEC_LATENCY.labels(tool=name).observe(time.time() - t0)
                log_event("tool.invoke.error", {"tool": name, "error": "E_UNKNOWN", "message": str(e), "attempt": attempt})
                if attempt > max_retries:
                    raise ExecutionError("E_UNKNOWN", str(e))
