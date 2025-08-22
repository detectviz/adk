# 專家代理 (Expert Agents) 的標準化實作
from __future__ import annotations
from typing import TYPE_CHECKING, List

# 官方 ADK 核心元件
from google.adk.agents import Agent, LlmAgent, AgentConfig
from google.adk.tools import Tool
from google.adk.tools.agent_tool import AgentTool

if TYPE_CHECKING:
    from google.adk.tools import ToolRegistry


class DiagnosticAgent(Agent):
    """診斷專家：負責問題分類、根因假設與資料蒐集。"""
    def __init__(self, config: AgentConfig, registry: "ToolRegistry"):
        super().__init__(config)
        # 每個專家內部可以包含一個或多個 LlmAgent 來執行具體任務。
        self._llm = LlmAgent(
            name="_DiagnosticLLM", 
            model=config.model,
            instruction="你是診斷專家，專注於問題分類、根因假設與資料蒐集。請使用 RAG 工具查詢知識庫以獲得線索。",
            tools=[registry.get("rag_search")]
        )
    async def process(self, request): 
        # 將收到的請求直接委派給內部的 LlmAgent 處理。
        return await self._llm.process(request)


class RemediationAgent(Agent):
    """修復專家：根據診斷結果，制定並執行修復計畫。"""
    def __init__(self, config: AgentConfig, registry: "ToolRegistry"):
        super().__init__(config)
        self._llm = LlmAgent(
            name="_RemediationLLM", 
            model=config.model,
            instruction="你是修復專家，根據診斷結果制定並執行修復計畫。高風險操作將觸發人工審批。",
            tools=[registry.get("K8sRolloutRestartLongRunningTool")]
        )
    async def process(self, request): 
        return await self._llm.process(request)


class PostmortemAgent(Agent):
    """覆盤專家：負責事件總結、根因分析與提出改進建議。"""
    def __init__(self, config: AgentConfig, registry: "ToolRegistry"):
        super().__init__(config)
        self._llm = LlmAgent(
            name="_PostmortemLLM", 
            model=config.model,
            instruction="你是覆盤專家，負責事件總結、根因分析、提出改進建議並將結論歸檔至知識庫。",
            tools=[registry.get("rag_search")] # 覆盤也可能需要查詢歷史資料
        )
    async def process(self, request): 
        return await self._llm.process(request)


class ConfigAgent(Agent):
    """配置專家：負責監控儀表板與告警策略的生成與調整。"""
    def __init__(self, config: AgentConfig, registry: "ToolRegistry"):
        super().__init__(config)
        self._llm = LlmAgent(
            name="_ConfigLLM", 
            model=config.model,
            instruction="你是配置專家，負責根據使用者需求，生成或調整監控儀表板與告警策略。",
            tools=[registry.get("ingest_text")] # 可能需要將新設定寫入文件
        )
    async def process(self, request): 
        return await self._llm.process(request)


def list_expert_tools(config: AgentConfig, registry: "ToolRegistry") -> List[AgentTool]:
    """工廠函式：根據主代理設定，初始化所有專家代理並將它們包裝成 AgentTool。

    Args:
        config: 主代理的 AgentConfig，用於派生子代理的設定。
        registry: 工具註冊表，用於向專家代理注入所需工具。

    Returns:
        一個包含所有專家 AgentTool 的列表，可供主代理使用。
    """
    experts = [
        DiagnosticAgent(config.get_sub_agent_config("Diagnostic"), registry),
        RemediationAgent(config.get_sub_agent_config("Remediation"), registry),
        PostmortemAgent(config.get_sub_agent_config("Postmortem"), registry),
        ConfigAgent(config.get_sub_agent_config("Config"), registry),
    ]
    # 將每個 Agent 實例包裝成 AgentTool，使其能被其他 Agent 當作工具來呼叫。
    return [AgentTool(name=f"{agent.config.name}Tool", agent=agent) for agent in experts]
