
# -*- coding: utf-8 -*-
# 工具執行器：讀取 YAML 規格、驗證輸入/輸出、執行函式、重試與逾時、Prometheus 指標與 OTel 追蹤。
from __future__ import annotations
import json, time
from typing import Any, Dict, Callable
from jsonschema import validate, ValidationError
from ..core.observability import TOOL_TOTAL, TOOL_LATENCY
from ..core.tracing import start_span

class ExecutionError(Exception):
    """
    標準化工具錯誤。
    code: 字串錯誤碼（E_TIMEOUT/E_BACKEND/E_BAD_QUERY/E_POLICY/E_SCHEMA/...）
    """
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code

class ToolExecutor:
    """
    以 YAML 規格為契約執行工具函式。
    - 輸入與回傳都以 JSON Schema 驗證
    - 以 retry 設定執行重試
    - 以 Prometheus 指標與 OTel 追蹤標記耗時與錯誤
    """
    def __init__(self, registry):
        self.registry = registry

    def _validate(self, schema: Dict[str, Any], obj: Dict[str, Any], is_input: bool):
        try:
            validate(instance=obj, schema=schema)
        except ValidationError as e:
            raise ExecutionError("E_SCHEMA", f"{'輸入' if is_input else '輸出'}不符合 Schema: {e.message}")

    def invoke(self, tool_name: str, spec: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        func: Callable[..., Dict[str, Any]] = self.registry.get_func(tool_name)
        if func is None:
            raise ExecutionError("E_NOT_FOUND", f"工具 {tool_name} 未註冊")
        args_schema = spec.get("args_schema") or {"type":"object"}
        ret_schema  = spec.get("returns_schema") or {"type":"object"}
        retry_cfg = spec.get("retry", {}) or {}
        max_retries = int(retry_cfg.get("max_retries", 0))

        # 參數驗證
        self._validate(args_schema, kwargs, True)

        attempt = 0
        last_err: ExecutionError | None = None
        with TOOL_LATENCY.labels(tool=tool_name).time():
            with start_span(f"tool.{tool_name}", {"args": {k:str(v) for k,v in kwargs.items()}}):
                while attempt <= max_retries:
                    try:
                        t0 = time.time()
                        data = func(**kwargs)  # 呼叫工具函式
                        dt = int((time.time()-t0)*1000)
                        TOOL_TOTAL.labels(tool=tool_name, status="ok").inc()
                        # 回傳驗證
                        if isinstance(data, dict):
                            self._validate(ret_schema, data, False)
                        return data
                    except ExecutionError as e:
                        last_err = e
                        attempt += 1
                        if attempt > max_retries:
                            TOOL_TOTAL.labels(tool=tool_name, status="error").inc()
                            raise
                    except Exception as e:
                        last_err = ExecutionError("E_UNKNOWN", str(e))
                        attempt += 1
                        if attempt > max_retries:
                            TOOL_TOTAL.labels(tool=tool_name, status="error").inc()
                            raise last_err
        # 不應到達這裡，保險回傳
        if last_err:
            raise last_err
        raise ExecutionError("E_UNKNOWN", "未明錯誤")
