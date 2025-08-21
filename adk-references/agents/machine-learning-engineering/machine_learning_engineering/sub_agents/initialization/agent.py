"""機器學習工程的初始化代理。"""

from typing import Optional
import dataclasses
import os
import shutil
import time
import ast

from google.adk import agents
from google.adk.agents import callback_context as callback_context_module
from google.adk.models import llm_response as llm_response_module
from google.adk.models import llm_request as llm_request_module
from google.genai import types
from google.adk.tools.google_search_tool import google_search

from machine_learning_engineering.sub_agents.initialization import prompt
from machine_learning_engineering.shared_libraries import debug_util
from machine_learning_engineering.shared_libraries import common_util
from machine_learning_engineering.shared_libraries import config


def get_model_candidates(
    callback_context: callback_context_module.CallbackContext,
    llm_response: llm_response_module.LlmResponse,
) -> Optional[llm_response_module.LlmResponse]:
    """
    從大型語言模型 (LLM) 的回應中解析模型候選者。

    此函式會處理來自 LLM 的回應，預期其為包含模型資訊的 JSON 陣列。
    它會提取模型名稱和範例程式碼，將它們儲存到狀態 (state) 中，
    並將每個模型的描述寫入工作區的單獨檔案中。
    """
    task_id = callback_context.agent_name.split("_")[-1]
    workspace_dir = callback_context.state.get("workspace_dir", "")
    task_name = callback_context.state.get("task_name", "")
    num_model_candidates = callback_context.state.get("num_model_candidates", 2) 
    run_cwd = os.path.join(workspace_dir, task_name, task_id)
    try:
        # 從 LLM 回應中提取純文字
        response_text = common_util.get_text_from_response(llm_response)
        # 解析包含模型資訊的 JSON 陣列
        start_idx, end_idx = response_text.find("["), response_text.rfind("]")+1
        result = response_text[start_idx:end_idx]
        models = ast.literal_eval(result)[:num_model_candidates]
        for j, model in enumerate(models):
            # 為每個模型建立描述
            model_description = ""
            model_description += f"## 模型名稱\n"
            model_description += model["model_name"]
            model_description += "\n\n"
            model_description += f"## 範例 Python 程式碼\n"
            model_description += model["example_code"]
            # 將模型資訊儲存到狀態中
            callback_context.state[f"init_{task_id}_model_{j+1}"] = {
                "model_name": model["model_name"],
                "example_code": model["example_code"],
                "model_description": model_description,
            }
            # 將模型描述寫入檔案
            with open(os.path.join(run_cwd, "model_candidates", f"model_{j+1}.txt"), "w") as f:
                f.write(model_description)
        # 標記模型檢索完成
        callback_context.state[f"init_{task_id}_model_finish"] = True
    except:
        # 如果解析失敗則不執行任何操作
        return None
    return None


def get_task_summary(
    callback_context: callback_context_module.CallbackContext,
    llm_response: llm_response_module.LlmResponse,
) -> Optional[llm_response_module.LlmResponse]:
    """獲取任務摘要。"""
    response_text = common_util.get_text_from_response(llm_response)
    task_type = callback_context.state.get("task_type", "未知任務")
    task_summary = f"任務：{task_type}\n{response_text}"
    callback_context.state["task_summary"] = task_summary
    return None


def check_model_finish(
    callback_context: callback_context_module.CallbackContext,
    llm_request: llm_request_module.LlmRequest,
) -> Optional[llm_response_module.LlmResponse]:
    """檢查模型檢索是否完成。"""
    task_id = callback_context.agent_name.split("_")[-1]
    if callback_context.state.get(f"init_{task_id}_model_finish", False):
        return llm_response_module.LlmResponse()
    return None


def check_model_eval_finish(
    callback_context: callback_context_module.CallbackContext,
    llm_request: llm_request_module.LlmRequest,
) -> Optional[llm_response_module.LlmResponse]:
    """檢查模型評估是否完成。"""
    model_id = callback_context.agent_name.split("_")[-1]
    task_id = callback_context.agent_name.split("_")[-2]
    model_description = callback_context.state.get(
        f"init_{task_id}_model_{model_id}",
        {},
    ).get("model_description", "")
    callback_context.state[f"model_eval_skip_data_leakage_check_{task_id}_{model_id}"] = True
    if not model_description:
        return llm_response_module.LlmResponse()
    result_dict = callback_context.state.get(f"init_code_exec_result_{task_id}_{model_id}", {})
    if result_dict:
        return llm_response_module.LlmResponse()
    callback_context.state[f"model_eval_skip_data_leakage_check_{task_id}_{model_id}"] = False
    return None


def check_merger_finish(
    callback_context: callback_context_module.CallbackContext,
    llm_request: llm_request_module.LlmRequest,
) -> Optional[llm_response_module.LlmResponse]:
    """檢查程式碼整合是否完成。"""
    reference_idx = callback_context.agent_name.split("_")[-1]
    task_id = callback_context.agent_name.split("_")[-2]
    result_dict = callback_context.state.get(f"merger_code_exec_result_{task_id}_{reference_idx}", {})
    callback_context.state[f"merger_skip_data_leakage_check_{task_id}_{reference_idx}"] = True
    if result_dict:
        return llm_response_module.LlmResponse()
    callback_context.state[f"merger_skip_data_leakage_check_{task_id}_{reference_idx}"] = False
    return None


def skip_data_use_check(
    callback_context: callback_context_module.CallbackContext,
    llm_request: llm_request_module.LlmRequest,
) -> Optional[llm_response_module.LlmResponse]:
    """如果程式碼未更改，則跳過資料使用檢查。"""
    task_id = callback_context.agent_name.split("_")[-1]
    check_data_use_finish = callback_context.state.get(f"check_data_use_finish_{task_id}", False)
    if check_data_use_finish:
        return llm_response_module.LlmResponse()
    result_dict = callback_context.state.get(f"train_code_exec_result_0_{task_id}", {})
    callback_context.state[f"check_data_use_skip_data_leakage_check_{task_id}"] = True
    if result_dict:
        return llm_response_module.LlmResponse()
    callback_context.state[f"check_data_use_skip_data_leakage_check_{task_id}"] = False
    return None


def rank_candidate_solutions(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """
    根據執行結果的分數對候選解決方案進行排名。

    此函式收集所有模型候選者的執行結果，並根據評估指標
    （`lower` 為 True 時升序，否則降序）對它們進行排序。
    排名最高的解決方案被選為「基礎解決方案」，並儲存其相關資訊
    （分數、程式碼、索引）以供後續步驟使用。
    """
    workspace_dir = callback_context.state.get("workspace_dir", "")
    task_name = callback_context.state.get("task_name", "")
    task_id = callback_context.agent_name.split("_")[-1]
    run_cwd = os.path.join(workspace_dir, task_name, task_id)
    num_model_candidates = callback_context.state.get("num_model_candidates", 2)
    performance_results = []
    # 收集所有候選者的性能結果
    for k in range(num_model_candidates):
        model_id = k + 1
        init_code = callback_context.state.get(f"init_code_{task_id}_{model_id}", "")
        init_code_exec_result = callback_context.state.get(
            f"init_code_exec_result_{task_id}_{model_id}", {}
        )
        if init_code_exec_result:
            performance_results.append(
                (init_code_exec_result.get("score", 0.0), init_code, init_code_exec_result)
            )
    # 根據指標對結果進行排序（值越低越好或越高越好）
    if callback_context.state.get("lower", True):
        performance_results.sort(key=lambda x: x[0])
    else:
        performance_results.sort(key=lambda x: x[0], reverse=True)
    # 將最佳解決方案設為基礎解決方案
    best_score = performance_results[0][0]
    base_solution = performance_results[0][1].replace("```python", "").replace("```", "")
    callback_context.state[f"performance_results_{task_id}"] = performance_results
    callback_context.state[f"best_score_{task_id}"] = best_score
    callback_context.state[f"base_solution_{task_id}"] = base_solution
    callback_context.state[f"best_idx_{task_id}"] = 0
    # 將最佳解決方案寫入檔案
    with open(f"{run_cwd}/train0_0.py", "w", encoding="utf-8") as f:
        f.write(base_solution)
    # 儲存合併器代理的初始狀態
    callback_context.state[f"merger_code_{task_id}_0"] = performance_results[0][1]
    callback_context.state[f"merger_code_exec_result_{task_id}_0"] = performance_results[0][2]
    return None


def select_best_solution(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """選擇最佳解決方案。"""
    workspace_dir = callback_context.state.get("workspace_dir", "")
    task_name = callback_context.state.get("task_name", "")
    task_id = callback_context.agent_name.split("_")[-1]
    run_cwd = os.path.join(workspace_dir, task_name, task_id)
    best_idx = callback_context.state.get(f"best_idx_{task_id}", 0)
    response = callback_context.state.get(f"merger_code_{task_id}_{best_idx}", "")
    result_dict = callback_context.state.get(
        f"merger_code_exec_result_{task_id}_{best_idx}", {}
    )
    code_text = response.replace("```python", "").replace("```", "")
    output_filepath = os.path.join(run_cwd, "train0.py")
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(code_text)
    callback_context.state[f"train_code_0_{task_id}"] = code_text
    callback_context.state[f"train_code_exec_result_0_{task_id}"] = result_dict
    return None


def update_merger_states(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """
    在合併操作後更新狀態。

    此函式比較合併後程式碼的分數與目前的最佳分數。
    如果合併後的程式碼產生了更好的分數（根據 `lower` is better 原則），
    則更新「基礎解決方案」為這個新的、更優的程式碼。
    """
    lower = callback_context.state.get("lower", True)
    reference_idx = callback_context.agent_name.split("_")[-1]
    task_id = callback_context.agent_name.split("_")[-2]
    best_score = callback_context.state.get(f"best_score_{task_id}", 0)
    base_solution = callback_context.state.get(f"base_solution_{task_id}", "")
    best_idx = callback_context.state.get(f"best_idx_{task_id}", 0)
    merged_code = callback_context.state.get(
        f"merger_code_{task_id}_{reference_idx}", ""
    )
    result_dict = callback_context.state.get(
        f"merger_code_exec_result_{task_id}_{reference_idx}", {}
    )
    score = result_dict["score"]
    # 根據指標（越低越好或越高越好）來判斷是否更新最佳解
    if lower:
        if score <= best_score:
            best_score = score
            base_solution = merged_code.replace("```python", "").replace("```", "")
            best_idx = int(reference_idx)
    else:
        if score >= best_score:
            best_score = score
            base_solution = merged_code.replace("```python", "").replace("```", "")
            best_idx = int(reference_idx)
    # 更新狀態中的最佳分數、解決方案和索引
    callback_context.state[f"best_score_{task_id}"] = best_score
    callback_context.state[f"base_solution_{task_id}"] = base_solution
    callback_context.state[f"best_idx_{task_id}"] = best_idx
    return None


def prepare_task(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """
    為任務執行做準備。

    此回呼函式在初始化代理開始時執行。它會：
    1. 從 `config` 載入預設設定並存入狀態。
    2. 設定隨機種子以確保實驗的可重現性。
    3. 從檔案讀取任務描述並存入狀態。
    """
    config_dict = dataclasses.asdict(config.CONFIG)
    for key in config_dict:
        callback_context.state[key] = config_dict[key]
    callback_context.state["start_time"] = time.time()
    # 固定隨機性以確保結果一致
    common_util.set_random_seed(callback_context.state["seed"])
    task_name = callback_context.state.get("task_name", "")
    data_dir = callback_context.state.get("data_dir", "")
    # 載入任務描述
    task_description = open(
        os.path.join(data_dir, task_name, "task_description.txt"),
        "r",
    ).read()
    callback_context.state["task_description"] = task_description
    return None


def create_workspace(
    callback_context: callback_context_module.CallbackContext
) -> Optional[types.Content]:
    """
    為特定的任務執行建立一個乾淨的工作區。

    此函式會為目前的任務 ID 建立一個新的目錄結構。
    如果目錄已存在，會先刪除舊的目錄以確保環境乾淨。
    接著，它會複製所有必要的輸入資料到新建立的 `input` 子目錄中。
    """
    data_dir = callback_context.state.get("data_dir", "")
    workspace_dir = callback_context.state.get("workspace_dir", "")
    task_name = callback_context.state.get("task_name", "")
    task_id = callback_context.agent_name.split("_")[-1]
    run_cwd = os.path.join(workspace_dir, task_name, task_id)
    # 如果工作目錄已存在，則刪除以確保乾淨的開始
    if os.path.exists(run_cwd):
      shutil.rmtree(run_cwd)
    # 建立執行所需的核心目錄
    os.makedirs(os.path.join(workspace_dir, task_name, task_id), exist_ok=True)
    os.makedirs(os.path.join(workspace_dir, task_name, task_id, "input"), exist_ok=True)
    os.makedirs(os.path.join(workspace_dir, task_name, task_id, "model_candidates"), exist_ok=True)
    # 將所有相關的任務檔案複製到工作區的 'input' 資料夾
    files = os.listdir(os.path.join(data_dir, task_name))
    for file in files:
        if os.path.isdir(os.path.join(data_dir, task_name, file)):
            shutil.copytree(
                os.path.join(data_dir, task_name, file),
                os.path.join(workspace_dir, task_name, task_id, "input", file),
            )
        else:
            # 排除答案檔案
            if "answer" not in file:
                common_util.copy_file(
                    os.path.join(data_dir, task_name, file),
                    os.path.join(workspace_dir, task_name, task_id, "input"),
                )
    return None


def get_model_eval_agent_instruction(
    context: callback_context_module.ReadonlyContext,
) -> str:
    """獲取模型評估代理的指令。"""
    task_description = context.state.get("task_description", "")
    model_id = context.agent_name.split("_")[-1]
    task_id = context.agent_name.split("_")[-2]
    model_description = context.state.get(
        f"init_{task_id}_model_{model_id}",
        {},
    ).get("model_description", "")
    return prompt.MODEL_EVAL_INSTR.format(
        task_description=task_description,
        model_description=model_description,
    )


def get_model_retriever_agent_instruction(
    context: callback_context_module.ReadonlyContext,
) -> str:
    """獲取模型檢索器代理的指令。"""
    task_summary = context.state.get("task_summary", "")
    num_model_candidates = context.state.get("num_model_candidates", 2)
    return prompt.MODEL_RETRIEVAL_INSTR.format(
        task_summary=task_summary,
        num_model_candidates=num_model_candidates,
    )


def get_merger_agent_instruction(
    context: callback_context_module.ReadonlyContext,
) -> str:
    """獲取整合代理的指令。"""
    reference_idx = int(context.agent_name.split("_")[-1])
    task_id = context.agent_name.split("_")[-2]
    performance_results = context.state.get(f"performance_results_{task_id}", [])
    base_solution = context.state.get(f"base_solution_{task_id}", "")
    if reference_idx < len(performance_results):
        reference_solution = performance_results[reference_idx][1].replace(
            "```python", ""
        ).replace("```", "")
    else:
        reference_solution = ""
    return prompt.CODE_INTEGRATION_INSTR.format(
        base_code=base_solution,
        reference_code=reference_solution,
    )


def get_check_data_use_instruction(
    context: callback_context_module.ReadonlyContext,
) -> str:
    """獲取檢查資料使用代理的指令。"""
    task_id = context.agent_name.split("_")[-1]
    task_description = context.state.get("task_description", "")
    code = context.state.get(f"train_code_0_{task_id}", "")
    return prompt.CHECK_DATA_USE_INSTR.format(
        code=code,
        task_description=task_description,
    )


task_summarization_agent = agents.Agent(
    model=config.CONFIG.agent_model,
    name="task_summarization_agent",
    description="總結任務描述。",
    instruction=prompt.SUMMARIZATION_AGENT_INSTR,
    after_model_callback=get_task_summary,
    generate_content_config=types.GenerateContentConfig(
        temperature=0.0,
    ),
    include_contents="none",
)
init_parallel_sub_agents = []
for k in range(config.CONFIG.num_solutions):
    model_retriever_agent = agents.Agent(
        model=config.CONFIG.agent_model,
        name=f"model_retriever_agent_{k+1}",
        description="檢索用於解決給定任務的有效模型。",
        instruction=get_model_retriever_agent_instruction,
        tools=[google_search],
        before_model_callback=check_model_finish,
        after_model_callback=get_model_candidates,
        generate_content_config=types.GenerateContentConfig(
            temperature=1.0,
        ),
        include_contents="none",
    )
    model_retriever_loop_agent = agents.LoopAgent(
        name=f"model_retriever_loop_agent_{k+1}",
        description="檢索有效模型，直到成功為止。",
        sub_agents=[model_retriever_agent],
        max_iterations=config.CONFIG.max_retry,
    )
    init_solution_gen_sub_agents = [
        model_retriever_loop_agent,
    ]
    for l in range(config.CONFIG.num_model_candidates):
        model_eval_and_debug_loop_agent = debug_util.get_run_and_debug_agent(
            prefix="model_eval",
            suffix=f"{k+1}_{l+1}",
            agent_description="使用給定模型生成程式碼",
            instruction_func=get_model_eval_agent_instruction,
            before_model_callback=check_model_eval_finish,
        )
        init_solution_gen_sub_agents.append(model_eval_and_debug_loop_agent)
    rank_agent = agents.SequentialAgent(
        name=f"rank_agent_{k+1}",
        description="根據分數對解決方案進行排名。",
        before_agent_callback=rank_candidate_solutions,
    )
    init_solution_gen_sub_agents.append(rank_agent)
    for l in range(1, config.CONFIG.num_model_candidates):
        merge_and_debug_loop_agent = debug_util.get_run_and_debug_agent(
            prefix="merger",
            suffix=f"{k+1}_{l}",
            agent_description="將兩個解決方案整合為一個解決方案",
            instruction_func=get_merger_agent_instruction,
            before_model_callback=check_merger_finish,
        )
        merger_states_update_agent = agents.SequentialAgent(
            name=f"merger_states_update_agent_{k+1}_{l}",
            description="合併後更新狀態。",
            before_agent_callback=update_merger_states,
        )
        init_solution_gen_sub_agents.extend(
            [
                merge_and_debug_loop_agent,
                merger_states_update_agent,
            ]
        )
    selection_agent = agents.SequentialAgent(
        name=f"selection_agent_{k+1}",
        description="選擇最佳解決方案。",
        before_agent_callback=select_best_solution,
    )
    init_solution_gen_sub_agents.append(selection_agent)
    if config.CONFIG.use_data_usage_checker:
        check_data_use_and_debug_loop_agent = debug_util.get_run_and_debug_agent(
            prefix="check_data_use",
            suffix=f"{k+1}",
            agent_description="檢查是否使用了所有提供的資訊",
            instruction_func=get_check_data_use_instruction,
            before_model_callback=skip_data_use_check,
        )
        init_solution_gen_sub_agents.append(check_data_use_and_debug_loop_agent)
    init_solution_gen_agent = agents.SequentialAgent(
        name=f"init_solution_gen_agent_{k+1}",
        description="為給定任務生成初始解決方案。",
        sub_agents=init_solution_gen_sub_agents,
        before_agent_callback=create_workspace,
    )
    init_parallel_sub_agents.append(init_solution_gen_agent)
init_parallel_agent = agents.ParallelAgent(
    name="init_parallel_agent",
    description="並行生成給定任務的多個初始解決方案。",
    sub_agents=init_parallel_sub_agents,
)
initialization_agent = agents.SequentialAgent(
    name="initialization_agent",
    description="初始化狀態並生成初始解決方案。",
    sub_agents=[
        task_summarization_agent,
        init_parallel_agent,
    ],
    before_agent_callback=prepare_task,
)
