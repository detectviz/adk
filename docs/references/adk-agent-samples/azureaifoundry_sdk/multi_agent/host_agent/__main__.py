"""
具有 Azure AI Agents 整合的多代理 (multi-agent) 路由應用程式。

此應用程式提供一個 Gradio 介面，用於與路由代理 (routing agent) 互動，
該代理 (Agent) 使用 Azure AI Agents 實現核心功能，並將任務委派給遠端代理 (remote agents)。
"""

import asyncio
import os
import traceback
from collections.abc import AsyncIterator
from pprint import pformat

import gradio as gr

from routing_agent import RoutingAgent

APP_NAME = "azure_routing_app"
USER_ID = "default_user"
SESSION_ID = "default_session"

# Global routing agent instance
ROUTING_AGENT: RoutingAgent = None


async def get_response_from_agent(
    message: str,
    history: list[gr.ChatMessage],
) -> AsyncIterator[gr.ChatMessage]:
    """透過 A2A 和 Semantic Kernel 從 Azure AI Foundry Agent 路由取得回應。"""
    global ROUTING_AGENT
    
    if not ROUTING_AGENT:
        yield gr.ChatMessage(
            role="assistant",
            content="❌ **錯誤**：路由代理 (Routing agent) 未初始化。請重新啟動應用程式。",
        )
        return
    
    try:
        # 顯示我們正在處理請求
        yield gr.ChatMessage(
            role="assistant",
            content="🤔 **正在處理您的請求...**",
        )
        
        # 透過 Azure AI Agent 處理訊息
        response = await ROUTING_AGENT.process_user_message(message)
        
        # 產生最終回應
        if response:
            yield gr.ChatMessage(
                role="assistant", 
                content=response
            )
        else:
            yield gr.ChatMessage(
                role="assistant",
                content="❌ **錯誤**：未收到來自代理 (Agent) 的回應。",
            )
            
    except Exception as e:
        print(f"在 get_response_from_agent 中發生錯誤 (類型：{type(e)})：{e}")
        traceback.print_exc()
        yield gr.ChatMessage(
            role="assistant",
            content=f"❌ **發生錯誤**：{str(e)}\n\n請查看伺服器日誌以了解詳細資訊。",
        )


async def initialize_routing_agent():
    """初始化 Azure AI 路由代理 (Agent)。"""
    global ROUTING_AGENT
    
    try:
        print("正在初始化 Azure AI 路由代理 (Agent)...")
        
        # 建立具有遠端代理 (Agent) 位址的路由代理 (Agent)
        ROUTING_AGENT = await RoutingAgent.create(
            remote_agent_addresses=[
                os.getenv('PLAYWRIGHT_AGENT_URL', 'http://localhost:10001'),
                os.getenv('TOOL_AGENT_URL', 'http://localhost:10002'),
            ]
        )
        
        # 建立 Azure AI 代理 (Agent)
        azure_agent = ROUTING_AGENT.create_agent()
        print(f"Azure AI 路由代理 (Agent) 已成功初始化，ID 為：{azure_agent.id}")
        
    except Exception as e:
        print(f"初始化路由代理 (Agent) 失敗：{e}")
        traceback.print_exc()
        raise


async def cleanup_routing_agent():
    """清理路由代理 (Agent) 資源。"""
    global ROUTING_AGENT
    
    if ROUTING_AGENT:
        try:
            ROUTING_AGENT.cleanup()
            print("路由代理 (Agent) 已成功清理。")
        except Exception as e:
            print(f"清理期間發生錯誤：{e}")
        finally:
            ROUTING_AGENT = None


async def main():
    """具有 Azure AI Agents 整合的主要 gradio 應用程式。"""
    
    # 檢查必要的環境變數
    required_env_vars = [
        "AZURE_AI_AGENT_ENDPOINT",
        "AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ 缺少必要的環境變數：{', '.join(missing_vars)}")
        print("請在執行應用程式前設定這些環境變數。")
        return
    
    # 初始化路由代理 (Agent)
    await initialize_routing_agent()

    try:
        with gr.Blocks(theme=gr.themes.Ocean(), title="Azure AI 路由代理 (Agent)") as demo:
            # 標頭部分
            gr.Markdown("""
            # 🤖 Azure AI 路由代理 (Agent)
            
            此助理使用 Azure AI Agents 來協助您使用 playwright 和一些開發工具。
            該代理 (Agent) 會智慧地將您的請求路由到專門的遠端代理 (Agent) 以獲得最佳協助。
            """)
            
            # 顯示代理 (Agent) 狀態
            if ROUTING_AGENT and ROUTING_AGENT.azure_agent:
                gr.Markdown(f"""
                ### 📊 代理 (Agent) 狀態
                - **Azure AI 代理 (Agent) ID**：`{ROUTING_AGENT.azure_agent.id}`
                - **執行緒 ID**：`{ROUTING_AGENT.current_thread.id if ROUTING_AGENT.current_thread else '未建立'}`
                - **可用遠端代理 (Agent)**：{len(ROUTING_AGENT.remote_agent_connections)}
                """)
            
            # 聊天介面
            gr.ChatInterface(
                get_response_from_agent,
                title="💬 與 Azure AI 路由代理 (Agent) 聊天",
                description="給我一則訊息，我將協助您瀏覽網頁、複製儲存庫，或使用 VSCode 和 VSCode Insiders 開啟它",
                examples=[
                    "複製儲存庫 https://github.com/kinfey/mcpdemo1",
                    "前往 github.com/kinfey",
                    "使用 VSCode 或 VSCode Insiders 開啟 {path}",
                ]
            )
            
            # 頁尾
            gr.Markdown("""
            ---
            **技術提供**：Azure AI Agents | **A2A 框架**：具有 Semantic Kernel 和 A2A 的多代理 (Multi-Agent) 路由系統
            """)

        print("正在啟動 Gradio 介面...")
        demo.queue().launch(
            server_name="0.0.0.0",
            server_port=8083,
        )
        
    except Exception as e:
        print(f"主應用程式發生錯誤：{e}")
        traceback.print_exc()
    finally:
        print("正在關閉應用程式...")
        await cleanup_routing_agent()
        print("Gradio 應用程式已關閉。")

if __name__ == "__main__":
    asyncio.run(main())
