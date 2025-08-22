# 標準化工具集 (Toolset) 實作
from __future__ import annotations
from typing import List, TYPE_CHECKING

# 官方 ADK 核心元件
from google.adk.tools import BaseTool, BaseToolset, FunctionTool, LongRunningFunctionTool

# 匯入工具函式的實作
from .k8s_long_running import _start_restart, _poll_restart
from .knowledge_ingestion import ingest_text
from .rag_retrieve import rag_search

if TYPE_CHECKING:
    from google.adk.context import ReadonlyContext


class SREAssistantToolset(BaseToolset):
    """一個集合了所有 SRE Assistant 自訂工具的標準 Toolset。
    
    這個類別遵循 ADK 的 Toolset 設計模式，用於集中管理和提供工具，
    使得主執行階段 (runtime) 的邏輯更清晰，並為未來動態提供工具打下基礎。
    """

    async def get_tools(self, readonly_context: "ReadonlyContext" = None) -> List[BaseTool]:
        """回傳此工具集所管理的所有工具實例。

        ADK 框架會自動呼叫此方法來探索代理可用的工具。
        `readonly_context` 參數未來可用於根據使用者角色或 Session 狀態動態回傳不同工具。
        """
        return [
            LongRunningFunctionTool(
                name="K8sRolloutRestartLongRunningTool",
                start_func=_start_restart,
                poll_func=_poll_restart,
                description="對指定的 Kubernetes Deployment 執行滾動重啟。此為長時任務。"
            ),
            FunctionTool(
                name="ingest_text", 
                func=ingest_text, 
                description="將提供的文字內容提取、處理並儲存到 RAG 知識庫中。"
            ),
            FunctionTool(
                name="rag_search", 
                func=rag_search, 
                description="根據使用者查詢，從 RAG 知識庫中檢索最相關的資訊片段。"
            )
        ]

    async def close(self) -> None:
        """在應用程式關閉時，執行必要的清理工作。"""
        # 目前沒有需要清理的資源，但保留此方法以備未來擴充。
        pass
