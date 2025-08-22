
# OpenTelemetry Logs 初始化模組（Python 端）
# 目的：將 Python logging 事件以 OTLP 輸出，便於 Alloy 收集後轉送到 Loki
from __future__ import annotations
import os, logging

from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry._logs import set_logger_provider

_LOGGER_CONFIGURED = False

def init_otel_logging() -> None:
    """
    2025-08-22 03:37:34Z
    函式用途：`init_otel_logging` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    global _LOGGER_CONFIGURED
    if _LOGGER_CONFIGURED:
        return
    # 讀取 OTLP 端點；預設 http/protobuf → Alloy 4318
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    lp = LoggerProvider()
    set_logger_provider(lp)
    exporter = OTLPLogExporter(endpoint=f"{endpoint}/v1/logs")
    lp.add_log_record_processor(BatchLogRecordProcessor(exporter))
    # 將標準 logging 綁定 OTel Handler（可同時輸出至 console）
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    _LOGGER_CONFIGURED = True