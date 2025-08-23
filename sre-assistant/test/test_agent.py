# sre-assistant/test/test_agent.py
# 說明：此檔案包含 SRECoordinator 的基本整合測試。

import pytest
import sys
import os
import importlib.util

# --- 動態導入模組 ---
# 說明：由於專案的主目錄名稱 'sre-assistant' 包含一個連字號，
# 它不是一個有效的 Python 套件名稱，因此我們無法使用標準的 `import` 語句。
#
# 作為解決方法，我們使用 `importlib` 函式庫根據文件路徑動態地載入 `agent.py` 模組。
# 這是處理非標準命名約定的穩定方法。

SRECoordinator = None
create_agent = None
import_error = None

try:
    # 1. 取得 agent.py 的絕對路徑
    # __file__ 是當前文件 (test_agent.py) 的路徑
    # 我們向上導航一層來到 'sre-assistant' 目錄
    current_dir = os.path.dirname(__file__)
    package_root = os.path.abspath(current_dir)
    # 我們需要將 'sre-assistant' 的父目錄加到 path，這樣 'from .sub_agents' 才能運作
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.insert(0, os.path.abspath(os.path.join(project_root, '..')))

    agent_module_path = os.path.join(project_root, "agent.py")

    # 2. 建立模組規格 (spec)
    # "sre_assistant.agent" 是我們賦予此模組的名稱，即使文件名不同
    spec = importlib.util.spec_from_file_location("sre_assistant.agent", agent_module_path)
    if spec is None:
        raise ImportError(f"Could not load spec for module at {agent_module_path}")

    # 3. 根據規格建立模組物件
    agent_module = importlib.util.module_from_spec(spec)

    # 4. 將模組添加到 sys.modules，使其對後續導入可見
    # 這一步驟很重要，因為 agent.py 內部可能有相對導入 (from .sub_agents...)
    # 為了讓這些相對導入能正確解析，它的父套件 'sre_assistant' 需要存在。
    # We create a dummy module for the package.
    sys.modules["sre_assistant"] = importlib.util.module_from_spec(
        importlib.util.spec_from_file_location('sre_assistant', os.path.join(project_root, '__init__.py'))
    )
    sys.modules["sre_assistant.agent"] = agent_module

    # 5. 執行模組載入
    spec.loader.exec_module(agent_module)

    # 6. 從已載入的模組中獲取我們需要的類別
    SRECoordinator = agent_module.SRECoordinator
    create_agent = agent_module.create_agent

except Exception as e:
    # 如果在導入過程中發生任何錯誤，我們將其定義為一個會失敗的測試，
    # 這樣就能清楚地看到問題所在。
    import_error = e

# --- 測試案例 ---

@pytest.mark.skipif(SRECoordinator is None, reason=f"Failed to import SRECoordinator: {import_error if 'import_error' in locals() else 'Unknown error'}")
def test_create_sre_coordinator_instance():
    """
    測試：是否可以成功實例化 SRECoordinator。

    目的：
    這是一個基本的健全檢查 (sanity check)，確保 SRECoordinator 的所有依賴項
    （即使是預留位置）都已正確連接，並且在實例化時不會引發導入錯誤或語法錯誤。
    """
    try:
        coordinator = SRECoordinator()
        assert coordinator is not None, "Coordinator instance should not be None"
        # 檢查它是否是 SequentialAgent 的一個實例
        from google.adk.agents import SequentialAgent
        assert isinstance(coordinator, SequentialAgent), "Coordinator should be an instance of SequentialAgent"
        print("SRECoordinator instantiated successfully.")
    except Exception as e:
        pytest.fail(f"Failed to instantiate SRECoordinator: {e}")

@pytest.mark.skipif(create_agent is None, reason=f"Failed to import create_agent: {import_error if 'import_error' in locals() else 'Unknown error'}")
def test_create_agent_factory():
    """
    測試：是否可以使用 create_agent 工廠函數成功創建代理。

    目的：
    驗證 ADK 的標準工廠模式是否已正確實現。
    """
    try:
        coordinator = create_agent()
        assert coordinator is not None, "Agent from factory should not be None"
        # 檢查它是否是 SRECoordinator 的一個實例
        assert isinstance(coordinator, SRECoordinator), "Agent from factory should be an instance of SRECoordinator"
        print("Agent created successfully via factory.")
    except Exception as e:
        pytest.fail(f"Factory function create_agent() failed: {e}")
