"""使用 Agent Development Kit (ADK) 示範機器學習工程代理"""

import os
import json
from typing import Optional
from google.genai import types
from google.adk.agents import callback_context as callback_context_module

from google.adk import agents
from machine_learning_engineering.sub_agents.initialization import agent as initialization_agent_module
from machine_learning_engineering.sub_agents.refinement import agent as refinement_agent_module
from machine_learning_engineering.sub_agents.ensemble import agent as ensemble_agent_module
from machine_learning_engineering.sub_agents.submission import agent as submission_agent_module

from machine_learning_engineering import prompt


def save_state(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """印出回呼上下文 (callback context) 的目前狀態。"""
    workspace_dir = callback_context.state.get("workspace_dir", "")
    task_name = callback_context.state.get("task_name", "")
    run_cwd = os.path.join(workspace_dir, task_name)
    with open(os.path.join(run_cwd, "final_state.json"), "w") as f:
        json.dump(callback_context.state.to_dict(), f, indent=2)
    return None


# 定義一個循序代理，它將按順序執行一系列子代理來解決機器學習工程任務。
# 這個管線代表了從初始化到最終提交的完整工作流程。
mle_pipeline_agent = agents.SequentialAgent(
    name="mle_pipeline_agent",
    sub_agents=[
        initialization_agent_module.initialization_agent, # 步驟 1: 初始化解決方案
        refinement_agent_module.refinement_agent,       # 步驟 2: 優化解決方案
        ensemble_agent_module.ensemble_agent,           # 步驟 3: 集成多個解決方案
        submission_agent_module.submission_agent,       # 步驟 4: 產生最終的提交檔案
    ],
    description="為了解決 MLE 任務，執行一系列的子代理。",
    after_agent_callback=save_state,
)

# 為了與 ADK 工具相容，根代理必須命名為 `root_agent`
root_agent = agents.Agent(
    model=os.getenv("ROOT_AGENT_MODEL"),
    name="mle_frontdoor_agent",
    instruction=prompt.FRONTDOOR_INSTRUCTION,
    global_instruction=prompt.SYSTEM_INSTRUCTION,
    sub_agents=[mle_pipeline_agent],
    generate_content_config=types.GenerateContentConfig(temperature=0.01),
)
