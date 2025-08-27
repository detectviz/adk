# eval/evaluation.py
"""
一個為 SRE Assistant 設計的、可執行的基礎評估框架。

此腳本提供了一個基礎但可運作的範例，展示如何以程式化的方式，
根據一組預先定義的測試案例來評估 SREWorkflow 的表現。
它取代了先前基於模擬 (mock) 的「願景」文件，提供了一個務實的起點。
"""
import asyncio
from typing import Dict, Any, List

from google.adk.agents import InvocationContext
from src.sre_assistant.workflow import SREWorkflow

# --- 黃金標準測試案例 (Golden Test Cases) ---
# 這是一個測試案例列表，每個案例代表一個事件或情境。
# 在真實世界中，這些案例應從外部檔案（如 JSONL）載入，以方便管理。
#
# 每個測試案例的結構：
# - test_id: 唯一的測試案例標識符。
# - description: 對此案例的自然語言描述。
# - initial_context: 模擬啟動工作流程時的初始上下文狀態。
#   - state: 包含傳遞給工作流程的初始數據，例如憑證、資源、以及模擬的診斷結果，
#            用以引導分診器 (Dispatcher) 的決策。
# - expected_outcome: 定義了此案例的「成功」標準。
#   - state_key: 我們期望在執行結束後，於 `ctx.state` 中檢查的鍵。
#   - expected_value: 對應 `state_key` 的期望值。
# - expected_expert: (可選) 更細緻的檢查，驗證分診器是否選擇了預期的專家代理。

TEST_CASES: List[Dict[str, Any]] = [
    {
        "test_id": "case_001_db_high_latency",
        "description": "主資料庫延遲過高，應觸發擴展修復。",
        "initial_context": {
            "state": {
                # 工作流程的輸入參數
                "credentials": {"auth_method": "local"},
                "resource": "database",
                "action": "diagnose",
                # 模擬的診斷結果，用以引導分診器
                "metrics_analysis": {"error_rate": 0.01, "latency_ms": 1500},
                "logs_analysis": {"critical_errors": 5, "pattern": "timeout"},
            }
        },
        "expected_outcome": {
            "state_key": "remediation_status",
            "expected_value": "dispatcher_executed",
        },
        "expected_expert": "scaling_fix",
    },
    {
        "test_id": "case_002_auth_service_500_errors",
        "description": "認證服務返回 500 錯誤，應觸發回滾。",
        "initial_context": {
            "state": {
                "credentials": {"auth_method": "local"},
                "resource": "auth-service",
                "action": "diagnose",
                "metrics_analysis": {"error_rate": 0.6, "latency_ms": 200},
                "logs_analysis": {"critical_errors": 250, "pattern": "NullPointerException"},
            }
        },
        "expected_outcome": {
            "state_key": "dispatcher_decision",
            "expected_value": "rollback_fix", # 我們期望 LLM 能做出此決策
        },
        "expected_expert": "rollback_fix",
    },
]


async def run_single_test_case(workflow: SREWorkflow, test_case: Dict[str, Any]) -> Dict[str, Any]:
    """
    針對 SREWorkflow 執行單一評估測試案例。

    Args:
        workflow (SREWorkflow): 要評估的 SREWorkflow 實例。
        test_case (Dict[str, Any]): 包含初始狀態和預期結果的測試案例字典。

    Returns:
        Dict[str, Any]: 一個包含測試結果（如是否成功）和最終上下文狀態的字典。
    """
    print(f"--- 正在執行測試: {test_case['test_id']} ---")

    # 步驟 1. 設定 (Setup): 為這次執行創建一個全新的、乾淨的 InvocationContext。
    initial_state = test_case.get("initial_context", {}).get("state", {})
    ctx = InvocationContext(state=initial_state)

    # 步驟 2. 執行 (Act): 異步運行工作流程。
    await workflow.run_async(ctx)

    # 步驟 3. 評估 (Evaluate): 檢查最終的上下文狀態是否符合預期。
    outcome_check = test_case["expected_outcome"]
    actual_value = ctx.state.get(outcome_check["state_key"])

    success = (actual_value == outcome_check["expected_value"])

    # 進行更詳細的檢查，驗證是否選擇了正確的專家
    if "expected_expert" in test_case:
        # 這裡是一個簡化版的檢查。一個更完整的評估器會去檢查工具調用的歷史紀錄。
        decision = ctx.state.get("dispatcher_decision", "")
        if test_case["expected_expert"] not in decision:
            success = False

    print(f"  - 描述: {test_case['description']}")
    print(f"  - 期望: {outcome_check['state_key']} == '{outcome_check['expected_value']}'")
    print(f"  - 實際:   {outcome_check['state_key']} == '{actual_value}'")
    print(f"  - 結果: {'通過 (PASS)' if success else '失敗 (FAIL)'}")

    return {
        "test_id": test_case["test_id"],
        "success": success,
        "final_context_state": ctx.state
    }


async def main():
    """
    評估腳本的主入口點。
    """
    print("=============================================")
    print("=   SRE Assistant 評估框架 v0.1              =")
    print("=============================================")

    # 只需實例化一次工作流程，以提高效率
    sre_workflow = SREWorkflow()

    results = []
    for case in TEST_CASES:
        result = await run_single_test_case(sre_workflow, case)
        results.append(result)
        print("-" * 40)

    # --- 最終報告 ---
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    pass_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print("\n================= 摘要報告 =================")
    print(f"  總測試數量: {total_tests}")
    print(f"  通過:        {passed_tests}")
    print(f"  失敗:        {total_tests - passed_tests}")
    print(f"  通過率:      {pass_rate:.2f}%")
    print("=============================================")


if __name__ == "__main__":
    asyncio.run(main())
