import os
from beeai_framework.adapters.a2a import A2AServer, A2AServerConfig
from beeai_framework.agents.experimental import RequirementAgent
from beeai_framework.backend import ChatModel
from beeai_framework.memory import UnconstrainedMemory
from beeai_framework.serve.utils import LRUMemoryManager
from beeai_framework.tools.search.duckduckgo import DuckDuckGoSearchTool
from beeai_framework.tools.search.wikipedia import WikipediaTool
from beeai_framework.tools.think import ThinkTool
from beeai_framework.tools.weather import OpenMeteoTool


def main() -> None:
    llm = ChatModel.from_name(os.environ.get("BEEAI_MODEL", "ollama:granite3.3:8b"))
    agent = RequirementAgent(
        llm=llm,
        tools=[ThinkTool(), DuckDuckGoSearchTool(), OpenMeteoTool(), WikipediaTool()],
        memory=UnconstrainedMemory(),
    )

    # 向 A2A 伺服器註冊代理 (Agent) 並執行 HTTP 伺服器
    # 對於 ToolCallingAgent，我們不需要指定 ACPAgent 工廠方法
    # 因為它已經在 A2AServer 中註冊
    # 我們使用 LRU 記憶體管理器來在記憶體中保留有限數量的會話
    A2AServer(config=A2AServerConfig(port=int(os.environ.get("A2A_PORT", 9999))), memory_manager=LRUMemoryManager(maxsize=100)).register(agent).serve()


if __name__ == "__main__":
    main()
