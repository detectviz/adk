from sre_assistant.adk_app.assembly import gather_subagent_tool_allowlist

# ADK 執行階段建構器：讀取 adk.yaml，建立工具（FunctionTool/LongRunningFunctionTool）、專家代理（AgentTool），主代理（LlmAgent），最後組裝 LoopAgent
from __future__ import annotations
from typing import Any, Dict, List
import os
from pathlib import Path

try:
    from google.adk.agents import LlmAgent, LoopAgent
    from google.adk.planners import BuiltInPlanner
    from google.adk.tools.agent_tool import AgentTool
    from google.adk.tools.function_tool import FunctionTool
    from google.adk.tools.long_running_tool import LongRunningFunctionTool
except Exception as e:
    LlmAgent = None
    LoopAgent = None
    BuiltInPlanner = None
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
    """
    2025-08-22 03:37:34Z
    函式用途：`_select_tools_by_names` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `tool_objs`：參數用途請描述。
    - `names`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    if not names:
        return list(tool_objs.values())
    out = []
    for n in names:
        if n in tool_objs:
            out.append(tool_objs[n])
    return out

def build_runner_from_config(cfg: dict) -> "LoopAgent":
    """
    2025-08-22 03:37:34Z
    函式用途：`build_runner_from_config` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `cfg`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    if LlmAgent is None or LoopAgent is None or BuiltInPlanner is None:
        raise RuntimeError("缺少 google-adk 套件，無法建立 Runner")

    # 1) 建立所有工具物件
    tool_map = {
        "K8sRolloutRestartLongRunningTool": k8s_rollout_restart_long_running_tool,
        "ingest_text": ingest_text,
        "rag_search": rag_search,
    }
    tool_objs = {name: _wrap_tool(name, fn) for name, fn in tool_map.items()}

    # 2) 讀取主代理工具 allowlist
    agent_cfg = (cfg.get("agent") or {})
    main_tool_allow = agent_cfg.get("tools_allowlist") or list(tool_objs.keys())
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
    return LoopAgent(agents=[main_llm], planner=planner, max_iterations=max_iter)

def get_runner():
    # 讀取 adk.yaml 並合併 experts/*.yaml 覆蓋
    """
    2025-08-22 03:37:34Z
    函式用途：`get_runner` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：此函式無參數或皆使用外部環境。
    回傳：請描述回傳資料結構與語義。
    """
    cfg = load_combined_config("adk.yaml")
    return build_runner_from_config(cfg)

RUNNER = get_runner()

def _filter_tools_by_subagents(registry: dict) -> dict:
    """{ts}
函式用途：依 sub_agents 工具白名單過濾註冊表。""".format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    allow = gather_subagent_tool_allowlist()
    return {k:v for k,v in registry.items() if k in allow}
