
"""
OpenTelemetry 初始化模組（繁中註解）
功能：
- 讀取環境變數與 adk.yaml，設定 Resource 屬性（service.name、cloud.provider=gcp 等）。
- 建立 OTLP gRPC 匯出器，將 Traces/Metrics 送往 OTLP 端點。
- 可透過環境 `OTEL_ENABLED=false` 關閉初始化。
"""
from __future__ import annotations
import os, yaml
from typing import Dict, Any

def _load_adk()->Dict[str, Any]:
    """讀取 adk.yaml，失敗時回傳空字典。"""
    try:
        with open("adk.yaml","r",encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def init_otel()->None:
    """
    初始化 OTel：僅在 `OTEL_ENABLED` 非 false/0 時執行。
    - 服務名稱：`SERVICE_NAME`（若無則 adk.yaml.agent.name，否則 fallback 'sre-assistant'）
    - OTLP 端點：`OTEL_EXPORTER_OTLP_ENDPOINT`（Cloud Build 已注入時可直接使用）
    - Resource：`service.name`、`cloud.provider=gcp`、`gcp.project_id`、`gcp.region`
    """
    if os.getenv("OTEL_ENABLED","true").lower() in ("0","false","no"):  # 可由環境關閉
        return
    try:
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry import trace
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except Exception:
        return  # 未安裝 OTel 套件時安靜略過

    cfg = _load_adk()
    agent_name = ((cfg.get("agent") or {}).get("name")) or "sre-assistant"
    service_name = os.getenv("SERVICE_NAME", agent_name)
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    region = os.getenv("CLOUD_RUN_REGION", os.getenv("_REGION", ""))

    resource = Resource.create({
        "service.name": service_name,
        "cloud.provider": "gcp",
        "gcp.project_id": project_id,
        "gcp.region": region,
    })

    provider = TracerProvider(resource=resource)
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://127.0.0.1:4317")
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=otlp_endpoint.startswith("http://"))
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    # 若 FastAPI 已載入，啟用自動攔截（由 app 初始化處呼叫）
    try:
        import sre_assistant.server.app as appmod  # type: ignore
        if hasattr(appmod, "app"):
            FastAPIInstrumentor().instrument_app(appmod.app)
    except Exception:
        pass
