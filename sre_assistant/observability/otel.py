
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider, PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from google.auth.transport.requests import Request as GAuthRequest
import google.auth
import google.auth.credentials

def init_telemetry(service_name: str = "sre-assistant") -> None:
    """
    自動產生註解時間：{ts}
    函式用途：初始化 OpenTelemetry Tracing/Metrics，支援 OTLP/gRPC；若對 Google Telemetry API 則自動附加 Bearer。
    參數說明：
    - `service_name`：資源屬性的 `service.name`。
    回傳：無。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or os.getenv("GOOGLE_PROJECT_ID","")
    res = Resource.create({ResourceAttributes.SERVICE_NAME: service_name, "gcp.project_id": project_id or "unknown", "cloud.provider":"gcp"})
    tp = TracerProvider(resource=res)
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    headers = None
    if os.getenv('GOOGLE_OTLP_AUTH','true').lower() in ('1','true','yes') and ('otel.googleapis.com' in endpoint or endpoint.startswith('https://')):
        try:
            creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
            creds.refresh(GAuthRequest())
            headers = (('authorization', f'Bearer {creds.token}'),)
        except Exception:
            headers = None
    span_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=endpoint.startswith('http://'), headers=headers)
    tp.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tp)

    metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=endpoint.startswith('http://'), headers=headers)
    reader = PeriodicExportingMetricReader(metric_exporter)
    mp = MeterProvider(resource=res, metric_readers=[reader])
    metrics.set_meter_provider(mp)

def get_tracer(name: str = "sre_assistant"):
    """
    自動產生註解時間：{ts}
    函式用途：取得 Tracer。
    參數說明：
    - `name`：Tracer 名稱。
    回傳：Tracer 實例。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    return trace.get_tracer(name)
