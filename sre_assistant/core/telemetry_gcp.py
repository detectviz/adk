
# -*- coding: utf-8 -*-
# 對接 Google Cloud Observability：Traces→Telemetry API(gRPC OTLP)、Logs→Cloud Logging、Metrics→Cloud Monitoring
from __future__ import annotations
import os, logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GrpcSpanExporter
from opentelemetry.exporter.gcp_logging import GCPLoggingHandler
from opentelemetry.exporter.cloud_monitoring import CloudMonitoringMetricsExporter

def init_gcp_observability() -> None:
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        raise RuntimeError("未設定 GCP_PROJECT_ID")
    service_name = os.getenv("OTEL_SERVICE_NAME","sre-assistant")
    service_ver = os.getenv("OTEL_SERVICE_VERSION","14.4")
    env = os.getenv("ENV","dev")

    res = Resource.create({
        "service.name": service_name,
        "service.version": service_ver,
        "deployment.environment": env,
        "gcp.project_id": project_id,
    })

    # Traces → Telemetry API（gRPC OTLP）
    tp = TracerProvider(resource=res)
    tp.add_span_processor(BatchSpanProcessor(GrpcSpanExporter(endpoint="https://telemetry.googleapis.com:443/v1/traces")))
    trace.set_tracer_provider(tp)

    # Metrics → Cloud Monitoring
    reader = PeriodicExportingMetricReader(CloudMonitoringMetricsExporter(project_id=project_id))
    mp = MeterProvider(resource=res, metric_readers=[reader])
    metrics.set_meter_provider(mp)

    # Logs → Cloud Logging
    handler = GCPLoggingHandler(project=project_id)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)

    # 自動化 Instrumentation（可用時啟用）
    try:
        from opentelemetry.instrumentation.vertexai import VertexAIInstrumentor
        VertexAIInstrumentor().instrument()
    except Exception:
        pass
    try:
        from opentelemetry.instrumentation.google_genai_sdk import GoogleGenAiSdkInstrumentor
        GoogleGenAiSdkInstrumentor().instrument()
    except Exception:
        pass
