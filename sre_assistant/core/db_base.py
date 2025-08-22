
# DB 介面抽象：便於在 SQLite 與 PostgreSQL 間切換。
from __future__ import annotations
from typing import Any, Dict, List, Optional, Protocol

class DatabaseInterface(Protocol):
        """
        2025-08-22 03:37:34Z
        函式用途：`insert_decision` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `session_id`：參數用途請描述。
        - `agent_name`：參數用途請描述。
        - `decision_type`：參數用途請描述。
        - `input`：參數用途請描述。
        - `output`：參數用途請描述。
        - `confidence`：參數用途請描述。
        - `execution_time_ms`：參數用途請描述。
        - `trace_id`：參數用途請描述。
        - `span_id`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
    def insert_decision(self, session_id: str, agent_name: str, decision_type: str, input: str, output: str, confidence: float | None, execution_time_ms: int, trace_id: str | None = None, span_id: str | None = None) -> int: ...
        """
        2025-08-22 03:37:34Z
        函式用途：`update_decision_output` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `decision_id`：參數用途請描述。
        - `output`：參數用途請描述。
        - `execution_time_ms`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
    def update_decision_output(self, decision_id: int, output: str, execution_time_ms: int | None = None): ...
        """
        2025-08-22 03:37:34Z
        函式用途：`insert_tool_execution` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `decision_id`：參數用途請描述。
        - `tool_name`：參數用途請描述。
        - `parameters`：參數用途請描述。
        - `result`：參數用途請描述。
        - `status`：參數用途請描述。
        - `error_message`：參數用途請描述。
        - `duration_ms`：參數用途請描述。
        - `trace_id`：參數用途請描述。
        - `span_id`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
    def insert_tool_execution(self, decision_id: int | None, tool_name: str, parameters: str, result: str, status: str, error_message: str | None, duration_ms: int, trace_id: str | None = None, span_id: str | None = None) -> int: ...
        """
        2025-08-22 03:37:34Z
        函式用途：`list_decisions` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `limit`：參數用途請描述。
        - `offset`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
    def list_decisions(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]: ...
        """
        2025-08-22 03:37:34Z
        函式用途：`list_tool_execs` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `limit`：參數用途請描述。
        - `offset`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
    def list_tool_execs(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]: ...