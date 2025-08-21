
# -*- coding: utf-8 -*-
# 遙測初始化：若安裝 OTel SDK，並設定 OTLP 端點，則安裝 BatchSpanProcessor 導出追蹤
from __future__ import annotations
import os

def init_tracing():
    try:
        import opentelemetry.sdk.resources as resources
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry import trace
        res = resources.Resource.create({
            "service.name": os.getenv("OTEL_SERVICE_NAME","sre-assistant"),
            "service.version": os.getenv("OTEL_SERVICE_VERSION","v12"),
        })
        provider = TracerProvider(resource=res)
        endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT","http://localhost:4318/v1/traces")
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
    except Exception:
        # 未安裝或配置不完整，忽略
        pass
