
# -*- coding: utf-8 -*-
import grpc
try:
    from sre_assistant.a2a import agent_pb2, agent_pb2_grpc
except Exception:
    agent_pb2 = None; agent_pb2_grpc=None

def execute(endpoint: str, agent: str, text: str, session_id: str=""):
    if agent_pb2_grpc is None:
        raise RuntimeError("請先執行 make a2a-gen 生成 pb2")
    with grpc.insecure_channel(endpoint) as ch:
        stub = agent_pb2_grpc.AgentGatewayStub(ch)
        resp = stub.Execute(agent_pb2.ExecuteRequest(agent=agent, input=text, session_id=session_id))
        return {"output": resp.output, "trace_id": resp.trace_id}
