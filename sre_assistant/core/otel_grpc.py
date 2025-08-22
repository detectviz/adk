# 注意：此模組僅用於 OpenTelemetry 追蹤傳遞（Trace Propagation），
# 與 ADK 的 Agent-to-Agent 通訊（A2A）無關，請勿混淆。
# 注意：此檔僅用於 OpenTelemetry 的 Trace 傳遞（gRPC 攔截器）\n
# -*- coding: utf-8 -*-
# gRPC OTel 攔截器：自動注入/抽取 traceparent（簡化版）
from __future__ import annotations
import grpc
from opentelemetry import trace
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator

class ClientInterceptor(grpc.UnaryUnaryClientInterceptor):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
    def __init__(self): self._prop=TraceContextTextMapPropagator()
    def intercept_unary_unary(self, continuation, client_call_details, request):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`intercept_unary_unary` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `continuation`：參數用途請描述。
        - `client_call_details`：參數用途請描述。
        - `request`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        metadata = []
        if client_call_details.metadata: metadata = list(client_call_details.metadata)
        carrier = {}
        self._prop.inject(carrier)
        for k,v in carrier.items():
            metadata.append((k, v))
        new_details = grpc.ClientCallDetails(client_call_details.method, client_call_details.timeout, metadata, client_call_details.credentials, client_call_details.wait_for_ready, client_call_details.compression)
        return continuation(new_details, request)

class ServerInterceptor(grpc.UnaryUnaryServerInterceptor):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
    def __init__(self): self._prop=TraceContextTextMapPropagator()
    def intercept_service(self, continuation, handler_call_details):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`intercept_service` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `continuation`：參數用途請描述。
        - `handler_call_details`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        return continuation(handler_call_details)