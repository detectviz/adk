
# -*- coding: utf-8 -*-
import grpc
from concurrent import futures
try:
    from sre_assistant.a2a import agent_pb2, agent_pb2_grpc
except Exception:
    agent_pb2 = None; agent_pb2_grpc=None

class AgentGatewayServicer:
    def __init__(self, runner): self.runner=runner
    def Execute(self, request, context):
        text = request.input
        out = f"SREAssistant 回覆（echo）：{text}"
        return agent_pb2.ExecuteResponse(output=out, trace_id="placeholder")

def serve(runner, host="0.0.0.0", port=50051):
    if agent_pb2_grpc is None:
        raise RuntimeError("請先執行 make a2a-gen 生成 pb2")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    agent_pb2_grpc.add_AgentGatewayServicer_to_server(AgentGatewayServicer(runner), server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    return server
