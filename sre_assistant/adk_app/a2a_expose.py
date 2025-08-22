
# -*- coding: utf-8 -*-
# 以 ADK A2A 暴露本地專家代理（示例：DiagnosticExpert）
from __future__ import annotations
import os
try:
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
except Exception as e:
    raise RuntimeError("缺少 google-adk[a2a] 依賴，請先安裝：pip install 'google-adk[a2a]'") from e

# 載入既有本地代理（假設專案內有 DiagnosticExpert 實作為 LlmAgent 實例）
from sre_assistant.adk_app.coordinator import diagnostic_expert

# 產生 A2A ASGI 應用（自動提供 /.well-known/agent.json）
a2a_app = to_a2a(diagnostic_expert, port=int(os.getenv("A2A_PORT","8001")))
