
# -*- coding: utf-8 -*-
# A2A gRPC Server（最小骨架）；需先以 protoc 產生 *_pb2.py 與 *_pb2_grpc.py 後方可啟動
from __future__ import annotations
import os, json, grpc
from concurrent import futures

# 產物：由 protoc 生成（此處僅示意匯入）
try:
    from sre_assistant.adk_app.proto import a2a_pb2, a2a_pb2_grpc
except Exception as e:
    a2a_pb2 = None; a2a_pb2_grpc = None

class AgentBridgeServicer(a2a_pb2_grpc.AgentBridgeServicer):
    """最小實作：僅回顯請求，實務中應調用本地 ADK Runner 或工具。"""
    def Relay(self, request, context):
        # 這裡可以呼叫本地 RUNNER 或 ToolRegistry 進行處理
        return a2a_pb2.RelayResponse(
            status="OK",
            message="accepted",
            output_json=json.dumps({"echo": request.payload_json}, ensure_ascii=False)
        )

def serve(host="0.0.0.0", port=50051):
    if a2a_pb2_grpc is None:
        raise RuntimeError("尚未以 protoc 產生 gRPC 代碼。請先執行 make a2a-proto")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    a2a_pb2_grpc.add_AgentBridgeServicer_to_server(AgentBridgeServicer(), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
