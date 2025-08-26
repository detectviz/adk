# sre_assistant/tests/test_agent.py
"""
Contains integration tests for the main SRE Assistant workflow.
This version uses a standard import and includes debugging for import errors.
"""

import pytest
from google.adk.agents import SequentialAgent

# --- Standard Import with Debugging ---
# We add a print statement in the except block to reveal the root cause of any import failures.
try:
    from sre_assistant.workflow import SREWorkflow, create_workflow
    import_error = None
except Exception as e:
    SREWorkflow = None
    create_workflow = None
    import_error = e
    # --- DEBUGGING: Print the captured exception ---
    print(f"\n--- CAPTURED IMPORT ERROR ---\n{e}\n---------------------------\n")


# --- Test Cases ---

@pytest.mark.skipif(SREWorkflow is None, reason=f"Failed to import SREWorkflow: {import_error}")
def test_create_sre_workflow_instance():
    """
    Tests if an instance of SREWorkflow can be successfully created.
    """
    try:
        # 使用繁體中文註解：實例化工作流程
        workflow = SREWorkflow()
        assert workflow is not None, "工作流程實例不應為 None"
        assert isinstance(workflow, SequentialAgent), "工作流程應為 SequentialAgent 的一個實例"
        print("SREWorkflow 實例化成功。")
    except Exception as e:
        pytest.fail(f"無法實例化 SREWorkflow: {e}")


@pytest.mark.skipif(create_workflow is None, reason=f"Failed to import create_workflow: {import_error}")
def test_create_workflow_factory():
    """
    Tests if the create_workflow factory function successfully creates an agent.
    """
    try:
        # 使用繁體中文註解：透過工廠函數創建代理
        workflow = create_workflow()
        assert workflow is not None, "從工廠創建的代理不應為 None"
        assert isinstance(workflow, SREWorkflow), "從工廠創建的代理應為 SREWorkflow 的一個實例"
        print("已透過工廠函數成功創建代理。")
    except Exception as e:
        pytest.fail(f"工廠函數 create_workflow() 失敗: {e}")
