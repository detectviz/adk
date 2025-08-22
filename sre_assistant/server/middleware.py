
# FastAPI 中介層：為每個請求建立 trace span 並記錄狀態碼與延遲
from __future__ import annotations
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace

class OTelMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        tracer = trace.get_tracer(__name__)
        start = time.time()
        with tracer.start_as_current_span(f"HTTP {request.method} {request.url.path}") as span:
            resp = await call_next(request)
            span.set_attribute("http.status_code", resp.status_code)
            span.set_attribute("http.route", request.url.path)
            span.set_attribute("http.method", request.method)
            span.set_attribute("net.peer.ip", request.client.host if request.client else "")
        resp.headers["x-latency-ms"] = str(int((time.time()-start)*1000))
        return resp