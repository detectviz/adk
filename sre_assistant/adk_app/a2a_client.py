
# -*- coding: utf-8 -*-
# A2A gRPC Client（最小示例）
from __future__ import annotations
import grpc, json
try:
    from sre_assistant.adk_app.proto import a2a_pb2, a2a_pb2_grpc
except Exception:
    a2a_pb2=None; a2a_pb2_grpc=None

def relay(addr: str, session_id: str, agent: str, intent: str, payload: dict) -> dict:
    if not a2a_pb2 or not a2a_pb2_grpc:
        raise RuntimeError("尚未以 protoc 產生 gRPC 代碼。請先執行 make a2a-proto")
    with grpc.insecure_channel(addr) as ch:
        stub = a2a_pb2_grpc.AgentBridgeStub(ch)
        resp = stub.Relay(a2a_pb2.RelayRequest(
            session_id=session_id, agent=agent, intent=intent, payload_json=json.dumps(payload, ensure_ascii=False)
        ))
        return {"status": resp.status, "message": resp.message, "output": json.loads(resp.output_json or "{}")}
