from __future__ import annotations
import os, glob, yaml
from typing import Dict

# 移除未使用的導入

# ADK 執行階段建構器：讀取 adk.yaml，建立工具（FunctionTool/LongRunningFunctionTool）、專家代理（AgentTool），主代理（LlmAgent），最後組裝 LoopAgent
from __future__ import annotations
from typing import Any, Dict, List
import os
from pathlib import Path

try:
    from google.adk.agents import LlmAgent, LoopAgent
    from google.adk.planners import BuiltInPlanner
    from google.adk.runner import Runner
    from google.adk.sessions import SessionService, InMemorySessionService
    from google.adk.tools import ToolRegistry
    from google.adk.tools.agent_tool import AgentTool
    from google.adk.tools.function_tool import FunctionTool
    from google.adk.tools.long_running_tool import LongRunningFunctionTool
except Exception as e:
    LlmAgent = None
    LoopAgent = None
    BuiltInPlanner = None
    Runner = None
    SessionService = None
    InMemorySessionService = None
    ToolRegistry = None
    AgentTool = None
    FunctionTool = None
    LongRunningFunctionTool = None

from ..core.config import load_combined_config

# 匯入實際工具實作（函式）
from sre_assistant.tools.k8s_long_running import k8s_rollout_restart_long_running_tool
from sre_assistant.tools.knowledge_ingestion import ingest_text
from sre_assistant.tools.rag_retrieve import rag_search
from sre_assistant.experts import diagnostic as diag_exp
from sre_assistant.experts import remediation as remed_exp
from sre_assistant.experts import postmortem as pm_exp
from sre_assistant.experts import config as cfg_exp

def _wrap_tool(name: str, fn) -> Any:
    """將 Python 函式工具包成 ADK Tool 物件；若無 ADK 套件則回傳原函式."""
    if FunctionTool is None:
        return fn
    if "long_running" in getattr(fn, "__name__", name).lower():
        if LongRunningFunctionTool is not None:
            return LongRunningFunctionTool(name=name, func=fn)
    return FunctionTool(name=name, func=fn)

def _select_tools_by_names(tool_objs: Dict[str, Any], names: List[str] | None) -> List[Any]:
    
    if not names:
        return list(tool_objs.values())
    out = []
    for n in names:
        if n in tool_objs:
            out.append(tool_objs[n])
    return out

def build_runner_from_config(cfg: dict) -> "Runner":
    
    if LlmAgent is None or LoopAgent is None or BuiltInPlanner is None or Runner is None:
        raise RuntimeError("缺少 google-adk 套件，無法建立 Runner")

    # 1) 使用官方 Tool Registry 註冊工具
    registry = ToolRegistry() if ToolRegistry is not None else None
    
    if registry is not None:
        # 註冊工具到官方 ToolRegistry
        if LongRunningFunctionTool is not None:
            registry.register(LongRunningFunctionTool(
                name="K8sRolloutRestartLongRunningTool",
                func=k8s_rollout_restart_long_running_tool
            ))
        
        if FunctionTool is not None:
            registry.register(FunctionTool(name="ingest_text", func=ingest_text))
            registry.register(FunctionTool(name="rag_search", func=rag_search))
    
    # Fallback to legacy tool mapping if ToolRegistry unavailable
    tool_map = {
        "K8sRolloutRestartLongRunningTool": k8s_rollout_restart_long_running_tool,
        "ingest_text": ingest_text,
        "rag_search": rag_search,
    }
    tool_objs = {name: _wrap_tool(name, fn) for name, fn in tool_map.items()}

    # 2) 讀取主代理工具 allowlist
    agent_cfg = (cfg.get("agent") or {})
    main_tool_allow = agent_cfg.get("tools_allowlist") or list(tool_objs.keys())
    
    # 使用 registry 獲取工具或回退到 legacy 方式
    if registry is not None:
        main_tools = []
        for tool_name in main_tool_allow:
            tool = registry.get(tool_name)
            if tool is not None:
                main_tools.append(tool)
    else:
        main_tools = _select_tools_by_names(tool_objs, main_tool_allow)

    # 3) 專家代理：依 experts.*.tools_allowlist 分配工具
    exp_cfg = (cfg.get("experts") or {})
    diag_tools = _select_tools_by_names(tool_objs, (exp_cfg.get("diagnostic") or {}).get("tools_allowlist", ["rag_search"])) 
    remed_tools = _select_tools_by_names(tool_objs, (exp_cfg.get("remediation") or {}).get("tools_allowlist", ["K8sRolloutRestartLongRunningTool"])) 
    pm_tools = _select_tools_by_names(tool_objs, (exp_cfg.get("postmortem") or {}).get("tools_allowlist", ["rag_search"])) 
    cfg_tools = _select_tools_by_names(tool_objs, (exp_cfg.get("config") or {}).get("tools_allowlist", ["ingest_text"])) 

    diagnostic_expert = diag_exp.build_agent(tool_objs)
    remediation_expert = remed_exp.build_agent(tool_objs)
    postmortem_expert = pm_exp.build_agent(tool_objs)
    config_expert = cfg_exp.build_agent(tool_objs)

    expert_tools = []
    if AgentTool is not None:
        expert_tools = [
            AgentTool(name="DiagnosticExpertTool", agent=diagnostic_expert),
            AgentTool(name="RemediationExpertTool", agent=remediation_expert),
            AgentTool(name="PostmortemExpertTool", agent=postmortem_expert),
            AgentTool(name="ConfigExpertTool", agent=config_expert),
        ]

    # 4) 主代理
    instruction = "你是 SREAssistant 主協調器。先規劃再執行，所有輸出需附依據與後續建議。高風險操作由工具內部觸發 HITL。"
    main_llm = LlmAgent(
        name="SREMainAgent",
        model=agent_cfg.get("model", os.getenv("ADK_MODEL","gemini-2.0-flash")),
        instruction=instruction,
        tools=(main_tools + expert_tools),
    )

    planner = BuiltInPlanner()
    max_iter = int((cfg.get("runner") or {}).get("max_iterations") or os.getenv("ADK_MAX_ITER","10"))
    
    # 5) 建立 LoopAgent 並用 Runner 包裝
    loop_agent = LoopAgent(agents=[main_llm], planner=planner, max_iterations=max_iter)
    
    # 6) 建立 SessionService
    session_service = InMemorySessionService() if InMemorySessionService is not None else None
    
    # 7) 用標準 Runner 包裝 LoopAgent
    return Runner(agent=loop_agent, session_service=session_service)

def get_runner():
    # 讀取 adk.yaml 並合併 experts/*.yaml 覆蓋
    
    cfg = load_combined_config("adk.yaml")
    return build_runner_from_config(cfg)

RUNNER = get_runner()

# 移除未使用的函數

import yaml, glob, os

def get_effective_models()->dict:
    """
    讀取 experts/*.yaml 的 model 欄位，回傳 {expert_name: model_name}。
    無設定者略過。
    """
    out={}
    for yp in glob.glob(os.path.join('experts','*.yaml')):
        name=os.path.splitext(os.path.basename(yp))[0]
        try:
            data=yaml.safe_load(open(yp,'r',encoding='utf-8')) or {}
            model=data.get('model')
            if isinstance(model,str) and model.strip():
                out[name]=model.strip()
        except Exception:
            continue
    return out

def get_slo_targets()->dict:
    """
    讀取 experts/*.yaml 的 slo 欄位，回傳 {expert_name: slo_dict}。
    """
    out={}
    for yp in glob.glob(os.path.join('experts','*.yaml')):
        name=os.path.splitext(os.path.basename(yp))[0]
        try:
            data=yaml.safe_load(open(yp,'r',encoding='utf-8')) or {}
            slo=data.get('slo') or {}
            if isinstance(slo, dict) and slo:
                out[name]=slo
        except Exception:
            continue
    return out
