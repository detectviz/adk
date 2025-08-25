import asyncio
import logging
import os
import time
from collections.abc import AsyncIterable
from typing import Any

from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder
from dotenv import load_dotenv
from pydantic import BaseModel
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.mcp import MCPSsePlugin, MCPStdioPlugin
# from semantic_kernel.contents import ChatMessageContent

logger = logging.getLogger(__name__)

load_dotenv()

# region Response Format


class ResponseFormat(BaseModel):
    """一個用於指示模型應如何回應的回應格式模型。"""

    status: str = 'input_required'
    message: str


# endregion

# region 具有 MCP 的 Azure AI Agent


class SemanticKernelMCPAgent:
    """包裝具有 MCP 外掛程式的 Azure AI Agent 以處理各種任務。"""

    def __init__(self):
        self.agent = None
        self.thread = None
        self.client = None
        self.credential = None
        self.plugin = None

    async def initialize_playwright(self):
        """使用 Playwright MCP 外掛程式初始化代理 (Agent)（遵循筆記本模式）。"""
        try:
            # 建立 Azure 憑證
            self.credential = DefaultAzureCredential()
            
            # 建立 Azure AI 用戶端（使用筆記本中的非同步內容管理員模式）
            self.client = await AzureAIAgent.create_client(credential=self.credential).__aenter__()
            
            # 建立 Playwright MCP STDIO 外掛程式（遵循筆記本模式）
            self.plugin = MCPStdioPlugin(
                name="Playwright",
                command="npx",
                args=["@playwright/mcp@latest"],
            )
            
            # 使用非同步內容管理員初始化外掛程式
            await self.plugin.__aenter__()
            
            # 建立代理 (Agent) 定義（遵循筆記本模式）
            agent_definition = await self.client.agents.create_agent(
                model=AzureAIAgentSettings().model_deployment_name,
                name="PlayWrightAgent",  # 使用與筆記本相同的名稱
                instructions="回答使用者的問題。",  # 使用與筆記本相同的指令
            )

            # 使用 MCP 外掛程式建立代理 (Agent)
            self.agent = AzureAIAgent(
                client=self.client,
                definition=agent_definition,
                plugins=[self.plugin],
            )
            
            logger.info("已成功使用 Playwright 外掛程式初始化 MCP 代理 (Agent)")
            
        except Exception as e:
            logger.error(f"使用 Playwright 初始化 MCP 代理 (Agent) 失敗：{e}")
            await self.cleanup()
            raise

    async def initialize_with_stdio(self, name: str, command: str, args: list[str] = None):
        """使用 Azure 憑證和 MCP STDIO 外掛程式初始化代理 (Agent)。
        
        Args:
            name: MCP 外掛程式的名稱
            command: 啟動 MCP 伺服器的指令（例如："python"、"npx"）
            args: 指令的參數（例如：["server.py"] 或 ["@playwright/mcp@latest"]）
        """
        try:
            # 建立 Azure 憑證
            self.credential = DefaultAzureCredential()
            
            # 建立 Azure AI 用戶端（使用筆記本中的非同步內容管理員模式）
            self.client = await AzureAIAgent.create_client(credential=self.credential).__aenter__()
            
            # 建立 MCP STDIO 外掛程式
            if args:
                self.plugin = MCPStdioPlugin(
                    name=name,
                    command=command,
                    args=args,
                )
            else:
                self.plugin = MCPStdioPlugin(
                    name=name,
                    command=command,
                )
            
            # 使用非同步內容管理員初始化外掛程式
            await self.plugin.__aenter__()
            
            # 建立代理 (Agent) 定義（遵循筆記本模式）
            agent_definition = await self.client.agents.create_agent(
                model=AzureAIAgentSettings().model_deployment_name,
                name="SKAssistant",  # 使用與筆記本相同的名稱
                instructions="回答使用者的問題。",  # 使用與筆記本相同的指令
            )

            # 使用 MCP 外掛程式建立代理 (Agent)
            self.agent = AzureAIAgent(
                client=self.client,
                definition=agent_definition,
                plugins=[self.plugin],
            )
            
            logger.info(f"已成功使用 STDIO 外掛程式 '{name}' 初始化 MCP 代理 (Agent)")
            
        except Exception as e:
            logger.error(f"使用 STDIO '{name}' 初始化 MCP 代理 (Agent) 失敗：{e}")
            await self.cleanup()
            raise

    async def invoke(self, user_input: str, session_id: str = None) -> dict[str, Any]:
        """使用 Azure AI Agent 和 MCP 外掛程式處理任務。

        Args:
            user_input (str): 使用者輸入訊息。
            session_id (str): 工作階段的唯一識別碼（可選）。

        Returns:
            dict: 一個包含內容和任務完成狀態的字典。
        """
        if not self.agent:
            return {
                'is_task_complete': False,
                'require_user_input': True,
                'content': '代理 (Agent) 未初始化。請先呼叫 initialize()。',
            }

        try:
            responses = []
            # 遵循筆記本模式並進行適當的回應處理
            async for response in self.agent.invoke(
                messages=user_input,
                thread=self.thread,
            ):
                # 如同在筆記本中一樣列印回應（用於偵錯）
                print(f"# {response.name}: {response}")
                responses.append(str(response))
                self.thread = response.thread

            content = "\n".join(responses) if responses else "未收到回應。"
            print("已完成處理使用者輸入。")  # 遵循筆記本模式
            
            return {
                'is_task_complete': True,
                'require_user_input': False,
                'content': content,
            }
        except Exception as e:
            return {
                'is_task_complete': False,
                'require_user_input': True,
                'content': f'處理請求時發生錯誤：{str(e)}',
            }

    async def stream(
        self,
        user_input: str,
        session_id: str = None,
    ) -> AsyncIterable[dict[str, Any]]:
        """從具有 MCP 外掛程式的 Azure AI Agent 串流回應。

        Args:
            user_input (str): 使用者輸入訊息。
            session_id (str): 工作階段的唯一識別碼（可選）。

        Yields:
            dict: 一個包含內容和任務完成狀態的字典。
        """
        if not self.agent:
            yield {
                'is_task_complete': False,
                'require_user_input': True,
                'content': '代理 (Agent) 未初始化。請先呼叫 initialize()。',
            }
            return

        try:
            async for response in self.agent.invoke(
                messages=user_input,
                thread=self.thread,
            ):
                # 如同在筆記本模式中一樣列印回應名稱
                print(f"# {response.name}: {response}")
                self.thread = response.thread
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': str(response),
                }
            
            # 最終完成訊息
            print("已完成處理使用者輸入。")  # 遵循筆記本模式
            yield {
                'is_task_complete': True,
                'require_user_input': False,
                'content': '任務已成功完成。',
            }
        except Exception as e:
            yield {
                'is_task_complete': False,
                'require_user_input': True,
                'content': f'處理請求時發生錯誤：{str(e)}',
            }

    async def cleanup(self):
        """清理資源。"""
        try:
            if self.thread:
                await self.thread.delete()
                self.thread = None
                logger.info("執行緒已成功刪除")
        except Exception as e:
            logger.error(f"刪除執行緒時發生錯誤：{e}")
        
        try:
            if self.agent and self.client:
                await self.client.agents.delete_agent(self.agent.id)
                logger.info("代理 (Agent) 已成功刪除")
        except Exception as e:
            logger.error(f"刪除代理 (Agent) 時發生錯誤：{e}")
        
        try:
            if self.plugin:
                await self.plugin.__aexit__(None, None, None)
                self.plugin = None
                logger.info("MCP 外掛程式已成功清理")
        except Exception as e:
            logger.error(f"清理 MCP 外掛程式時發生錯誤：{e}")
        
        try:
            if self.client:
                await self.client.close()
                self.client = None
                logger.info("用戶端已成功關閉")
        except Exception as e:
            logger.error(f"關閉用戶端時發生錯誤：{e}")
        
        try:
            if self.credential:
                await self.credential.close()
                self.credential = None
                logger.info("憑證已成功關閉")
        except Exception as e:
            logger.error(f"關閉憑證時發生錯誤：{e}")
        
        self.agent = None

# endregion

# region 用於筆記本風格用法的便利函式

async def run_playwright_agent_example(user_input: str = "請導覽至 github.com/kinfey"):
    """執行與更新後的筆記本實作類似的 Playwright MCP 代理 (Agent) 範例。
    
    Args:
        user_input: 要處理的使用者輸入
    """
    agent = SemanticKernelMCPAgent()
    
    try:
        # 使用 Playwright 外掛程式初始化代理 (Agent)
        await agent.initialize_playwright()
        
        # 處理使用者輸入
        print(f"正在處理使用者輸入：{user_input}")
        result = await agent.invoke(user_input)
        
        print("\n結果：")
        print(result['content'])
        
        return result
        
    except Exception as e:
        print(f"錯誤：{e}")
        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': f'錯誤：{str(e)}',
        }
    finally:
        # 清理
        await agent.cleanup()


async def run_playwright_agent_stream_example(user_input: str = "請導覽至 github.com/kinfey"):
    """執行具有串流功能的 Playwright MCP 代理 (Agent)，類似於更新後的筆記本實作。
    
    Args:
        user_input: 要處理的使用者輸入
    """
    agent = SemanticKernelMCPAgent()
    
    try:
        # 使用 Playwright 外掛程式初始化代理 (Agent)
        await agent.initialize_playwright()
        
        # 使用串流處理使用者輸入
        print(f"正在處理使用者輸入（串流）：{user_input}")
        
        async for response in agent.stream(user_input):
            if not response['is_task_complete']:
                print(response['content'])
            else:
                print(f"\n最終結果：{response['content']}")
                break
        
    except Exception as e:
        print(f"錯誤：{e}")
    finally:
        # 清理
        await agent.cleanup()

# endregion
