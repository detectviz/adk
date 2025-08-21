"""機器學習工程的集成 (Ensemble) 代理。"""

from typing import Optional
import os
import shutil
import numpy as np

from google.adk import agents
from google.adk.agents import callback_context as callback_context_module
from google.adk.models import llm_response as llm_response_module
from google.adk.models import llm_request as llm_request_module
from google.genai import types

from machine_learning_engineering.sub_agents.ensemble import prompt
from machine_learning_engineering.shared_libraries import debug_util
from machine_learning_engineering.shared_libraries import common_util
from machine_learning_engineering.shared_libraries import config


def update_ensemble_loop_states(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """更新集成迴圈狀態。"""
    callback_context.state["ensemble_iter"] += 1
    return None


def init_ensemble_loop_states(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """初始化集成迴圈狀態。"""
    callback_context.state["ensemble_iter"] = 0
    return None


def get_init_ensemble_plan(
    callback_context: callback_context_module.CallbackContext,
    llm_response: llm_response_module.LlmResponse,
) -> Optional[llm_response_module.LlmResponse]:
    """
    從 LLM 回應中獲取並儲存初始的集成計畫。

    此函式作為 `init_ensemble_plan_agent` 的後續回呼 (after_model_callback) 使用。
    它會從 LLM 的回應中提取文字內容，並將其作為第一個集成計畫儲存到狀態的 `ensemble_plans` 列表中。
    """
    response_text = common_util.get_text_from_response(llm_response)
    callback_context.state["ensemble_plans"] = [response_text]
    return None


def check_ensemble_plan_implement_finish(
    callback_context: callback_context_module.CallbackContext,
    llm_request: llm_request_module.LlmRequest,
) -> Optional[llm_response_module.LlmResponse]:
    """檢查集成計畫實作是否完成。"""
    ensemble_iter = callback_context.state.get("ensemble_iter", 0)
    result_dict = callback_context.state.get(
        f"ensemble_code_exec_result_{ensemble_iter}", {}
    )
    callback_context.state[
        f"ensemble_plan_implement_skip_data_leakage_check_{ensemble_iter}"
    ] = True
    if result_dict:
        return llm_response_module.LlmResponse()
    callback_context.state[
        f"ensemble_plan_implement_skip_data_leakage_check_{ensemble_iter}"
    ] = False
    return None


def get_refined_ensemble_plan(
    callback_context: callback_context_module.CallbackContext,
    llm_response: llm_response_module.LlmResponse,
) -> Optional[llm_response_module.LlmResponse]:
    """從回應中獲取優化後的集成計畫。"""
    response_text = common_util.get_text_from_response(llm_response)
    callback_context.state["ensemble_plans"].append(response_text)
    return None


def get_init_ensemble_plan_agent_instruction(
    context: callback_context_module.ReadonlyContext,
) -> str:
    """獲取初始集成計畫代理的指令。"""
    num_solutions = context.state.get("num_solutions", 2)
    outer_loop_round = context.state.get("outer_loop_round", 2)
    python_solutions = []
    for task_id in range(1, num_solutions + 1):
        code = context.state.get(
            f"train_code_{outer_loop_round}_{task_id}", ""
        )
        formatted_str = f"# Python 解決方案 {task_id}\n```python\n{code}\n```\n"
        python_solutions.append(formatted_str)
    instruction = prompt.INIT_ENSEMBLE_PLAN_INSTR.format(
        num_solutions=num_solutions,
        python_solutions="\n".join(python_solutions),
    )
    return instruction


def get_ensemble_plan_refinement_instruction(
    context: callback_context_module.ReadonlyContext,
) -> str:
    """
    為集成計畫的優化代理建構提示指令。

    此函式收集先前所有集成計畫的執行結果，包括它們的分數。
    它會對這些計畫根據性能進行排序，並選出表現最好的幾個。
    然後，它將這些頂尖計畫的摘要、以及原始的 Python 解決方案，
    格式化成一個提示，傳遞給 LLM，以引導其產生一個更佳的集成策略。
    """
    num_solutions = context.state.get("num_solutions", 2)
    outer_loop_round = context.state.get("outer_loop_round", 2)
    num_top_plans = context.state.get("num_top_plans", 3)
    lower = context.state.get("lower", True)
    prev_plans = context.state.get("ensemble_plans", [])
    prev_scores = []
    # 收集先前計畫的分數
    for k in range(len(prev_plans)):
        exec_result = context.state.get(
            f"ensemble_code_exec_result_{k}", {}
        )
        prev_scores.append(exec_result["score"])
    # 根據分數對計畫進行排序
    sorted_idx = np.argsort(prev_scores)[::-1]
    if lower:
        sorted_idx = sorted_idx[-num_top_plans:]
        criteria = "更低"
    else:
        sorted_idx = sorted_idx[:num_top_plans]
        criteria = "更高"
    # 建立先前計畫及其性能的摘要
    prev_plans_and_scores = ""
    for k in sorted_idx:
        prev_plans_and_scores += f"## 計畫：{prev_plans[k]}\n"
        prev_plans_and_scores += f"## 分數：{prev_scores[k]:.5f}\n\n"
    # 收集原始的 Python 解決方案
    python_solutions = []
    for task_id in range(1, num_solutions + 1):
        code = context.state.get(
            f"train_code_{outer_loop_round}_{task_id}", ""
        )
        formatted_str = f"# Python 解決方案 {task_id}\n```python\n{code}\n```\n"
        python_solutions.append(formatted_str)
    # 格式化最終的提示指令
    return prompt.ENSEMBLE_PLAN_REFINE_INSTR.format(
        num_solutions=num_solutions,
        python_solutions="\n".join(python_solutions),
        prev_plans_and_scores=prev_plans_and_scores,
        criteria=criteria,
    )


def get_ensemble_plan_implement_agent_instruction(
    context: callback_context_module.ReadonlyContext,
) -> str:
    """獲取集成計畫實作代理的指令。"""
    num_solutions = context.state.get("num_solutions", 2)
    outer_loop_round = context.state.get("outer_loop_round", 2)
    python_solutions = []
    for task_id in range(1, num_solutions + 1):
        code = context.state.get(
            f"train_code_{outer_loop_round}_{task_id}", ""
        )
        formatted_str = f"# Python 解決方案 {task_id}\n```python\n{code}\n```\n"
        python_solutions.append(formatted_str)
    prev_plans = context.state.get(f"ensemble_plans", [""])
    return prompt.ENSEMBLE_PLAN_IMPLEMENT_INSTR.format(
        num_solutions=num_solutions,
        python_solutions="\n".join(python_solutions),
        plan=prev_plans[-1],
    )


def create_workspace(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """
    為集成任務建立一個乾淨的工作區。

    此函式確保集成代理在一個隔離且準備好的環境中執行。它會：
    1. 刪除任何先前存在的集成工作區，以避免舊檔案的干擾。
    2. 建立一個新的工作區目錄結構，包括 `input` 和 `final` 子目錄。
    3. 將原始任務資料從 `data_dir` 複製到新的 `input` 目錄中，
       同時排除答案檔案，以防資料洩漏。
    """
    data_dir = callback_context.state.get("data_dir", "")
    workspace_dir = callback_context.state.get("workspace_dir", "")
    task_name = callback_context.state.get("task_name", "")
    run_cwd = os.path.join(workspace_dir, task_name, "ensemble")
    if os.path.exists(run_cwd):
      shutil.rmtree(run_cwd)
    # 建立集成任務所需的目錄結構
    os.makedirs(os.path.join(workspace_dir, task_name, "ensemble"), exist_ok=True)
    os.makedirs(os.path.join(workspace_dir, task_name, "ensemble", "input"), exist_ok=True)
    os.makedirs(os.path.join(workspace_dir, task_name, "ensemble", "final"), exist_ok=True)
    # 將所有相關的任務檔案複製到工作區的 'input' 資料夾
    files = os.listdir(os.path.join(data_dir, task_name))
    for file in files:
        if os.path.isdir(os.path.join(data_dir, task_name, file)):
            shutil.copytree(
                os.path.join(data_dir, task_name, file),
                os.path.join(workspace_dir, task_name, "ensemble", "input", file),
            )
        else:
            # 排除答案檔案，防止資料洩漏
            if "answer" not in file:
                common_util.copy_file(
                    os.path.join(data_dir, task_name, file),
                    os.path.join(workspace_dir, task_name, "ensemble", "input"),
                )
    return None


init_ensemble_plan_agent = agents.Agent(
    model=config.CONFIG.agent_model,
    name="init_ensemble_plan_agent",
    description="產生一個初始計畫來集成解決方案。",
    instruction=get_init_ensemble_plan_agent_instruction,
    before_agent_callback=init_ensemble_loop_states,
    after_model_callback=get_init_ensemble_plan,
    generate_content_config=types.GenerateContentConfig(
        temperature=1.0,
    ),
    include_contents="none",
)
init_ensemble_plan_implement_agent = debug_util.get_run_and_debug_agent(
    prefix="ensemble_plan_implement_initial",
    suffix="",
    agent_description="實作初始計畫以集成解決方案。",
    instruction_func=get_ensemble_plan_implement_agent_instruction,
    before_model_callback=check_ensemble_plan_implement_finish,
)
ensemble_plan_refine_agent = agents.Agent(
    model=config.CONFIG.agent_model,
    name="ensemble_plan_refine_agent",
    description="優化集成計畫。",
    instruction=get_ensemble_plan_refinement_instruction,
    after_model_callback=get_refined_ensemble_plan,
    generate_content_config=types.GenerateContentConfig(
        temperature=1.0,
    ),
    include_contents="none",
)
ensemble_plan_implement_agent = debug_util.get_run_and_debug_agent(
    prefix="ensemble_plan_implement",
    suffix="",
    agent_description="實作計畫以集成解決方案。",
    instruction_func=get_ensemble_plan_implement_agent_instruction,
    before_model_callback=check_ensemble_plan_implement_finish,
)
ensemble_plan_refine_and_implement_agent = agents.SequentialAgent(
    name="ensemble_plan_refine_and_implement_agent",
    description="優化集成計畫然後實作它。",
    sub_agents=[
        ensemble_plan_refine_agent,
        ensemble_plan_implement_agent,
    ],
    after_agent_callback=update_ensemble_loop_states,
)
ensemble_plan_refine_and_implement_loop_agent = agents.LoopAgent(
    name="ensemble_plan_refine_and_implement_loop_agent",
    description="迭代地優化集成計畫並實作它。",
    sub_agents=[ensemble_plan_refine_and_implement_agent],
    before_agent_callback=update_ensemble_loop_states,
    max_iterations=config.CONFIG.ensemble_loop_round,
)
ensemble_agent = agents.SequentialAgent(
    name="ensemble_agent",
    description="集成多個解決方案。",
    sub_agents=[
        init_ensemble_plan_agent,
        init_ensemble_plan_implement_agent,
        ensemble_plan_refine_and_implement_loop_agent,
    ],
    before_agent_callback=create_workspace,
    after_agent_callback=None,
)
