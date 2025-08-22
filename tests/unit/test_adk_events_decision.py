
# -*- coding: utf-8 -*-
# 用虛擬事件型別驗證嚴格解析與 DecisionRecord 生成
from sre_assistant.core.adk_events import extract_decision, AGENT_FINISHED, TOOL_CALL_FINISHED

class AgentFinished:
    def __init__(self):
        self.agent = {"name":"DiagnosticExpert"}
        self.output = {"summary":"ok"}
        self.latency_ms = 123

class ToolCallFinished:
    def __init__(self):
        self.agent = {"name":"DiagnosticExpert"}
        self.tool = {"name":"PromQLQueryTool"}
        self.args = {"query":"up"}
        self.result = {"series":[]}
        self.latency_ms = 45

def test_agent_finished_to_decision():
    rec = extract_decision(AgentFinished())
    assert rec is not None and rec.agent_name == "DiagnosticExpert" and rec.decision_type == AGENT_FINISHED

def test_tool_finished_to_decision():
    rec = extract_decision(ToolCallFinished())
    assert rec is not None and rec.decision_type == TOOL_CALL_FINISHED
