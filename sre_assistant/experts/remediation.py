
# 專家代理模組（單檔）：導出 build_agent(tool_objs) 以建立 LlmAgent 實例
from __future__ import annotations
from typing import Dict, Any, List
import os
from ..core.config import load_adk_config

try:
    from google.adk.agents import LlmAgent
except Exception:
    LlmAgent = None

def _select_tools(tool_objs: Dict[str, Any], default_names: List[str], section: str) -> List[Any]:
    """根據 adk.yaml 的 experts.<section>.tools_allowlist 選擇工具；若未配置則採用 default_names。"""
    cfg = load_adk_config()
    allow = (((cfg.get("experts", {}) or {}).get(section, {}) or {}).get("tools_allowlist")) or default_names
    out = []
    for n in allow:
        if n in tool_objs:
            out.append(tool_objs[n])
    return out

def build_agent(tool_objs: Dict[str, Any]) -> "LlmAgent":
    """建立 RemediationExpert 實例。
    - 模型選擇：experts.remediation.model > agent.model > ADK_MODEL。
    - 工具清單：experts.remediation.tools_allowlist 或預設 ['K8sRolloutRestartLongRunningTool']。
    """
    if LlmAgent is None:
        raise RuntimeError("缺少 google-adk 套件，無法建立 RemediationExpert")
    cfg = load_adk_config()
    agent_cfg = (cfg.get("agent") or {})
    exp_cfg = ((cfg.get("experts") or {}).get("remediation") or {})
    model = exp_cfg.get('model') or agent_cfg.get('model') or os.getenv('ADK_MODEL', 'gemini-2.0-flash')
    tools = _select_tools(tool_objs, ["K8sRolloutRestartLongRunningTool"], "remediation")
    return LlmAgent(
        name="RemediationExpert",
        model=model,
        prompt = exp_cfg.get("prompt")
    instruction=prompt or '你是修復專家，將診斷結果轉為安全的修復計畫；高風險操作需 request_credential。' ,
        tools=tools,
    )
