
# -*- coding: utf-8 -*-
# 用虛擬事件型別驗證嚴格解析與 DecisionRecord 生成
from sre_assistant.core.adk_events import extract_decision, AGENT_FINISHED, TOOL_CALL_FINISHED

class AgentFinished:
    def __init__(self):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.agent = {"name":"DiagnosticExpert"}
        self.output = {"summary":"ok"}
        self.latency_ms = 123

class ToolCallFinished:
    def __init__(self):
        """
        自動產生註解時間：2025-08-22 03:37:34Z
        函式用途：`__init__` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        self.agent = {"name":"DiagnosticExpert"}
        self.tool = {"name":"PromQLQueryTool"}
        self.args = {"query":"up"}
        self.result = {"series":[]}
        self.latency_ms = 45

def test_agent_finished_to_decision():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_agent_finished_to_decision` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    rec = extract_decision(AgentFinished())
    assert rec is not None and rec.agent_name == "DiagnosticExpert" and rec.decision_type == AGENT_FINISHED

def test_tool_finished_to_decision():
    """
    自動產生註解時間：2025-08-22 03:37:34Z
    函式用途：`test_tool_finished_to_decision` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    rec = extract_decision(ToolCallFinished())
    assert rec is not None and rec.decision_type == TOOL_CALL_FINISHED