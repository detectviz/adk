# src/sre_assistant/__init__.py
"""
SRE Assistant - ADK 代理套件。

此檔案暴露主要的代理工作流程及其工廠函數，
使其可被應用程式的其他部分（例如測試或伺服器入口點）匯入。
"""

from .workflow import SREWorkflowFactory, run_demo

__all__ = ["SREWorkflowFactory", "run_demo"]
