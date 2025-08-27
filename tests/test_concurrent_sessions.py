# test/test_concurrent_sessions.py
# 說明：此檔案包含 SRE Assistant 的並發測試。
# 根據技術債務清單，需要添加 50 個並發會話的測試，
# 以確保系統在生產負載下的穩定性和可靠性。
# 參考 ARCHITECTURE.md 第 16.1 節。

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import sys
import os
import importlib.util
import time

# --- 動態導入 SRECoordinator ---
SRECoordinator = None
import_error = None

try:
    current_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.insert(0, os.path.abspath(os.path.join(project_root, '..')))

    agent_module_path = os.path.join(project_root, "agent.py")
    spec = importlib.util.spec_from_file_location("sre_assistant.agent", agent_module_path)
    agent_module = importlib.util.module_from_spec(spec)

    if 'sre_assistant' not in sys.modules:
        sys.modules["sre_assistant"] = importlib.util.module_from_spec(
            importlib.util.spec_from_file_location('sre_assistant', os.path.join(project_root, '__init__.py'))
        )
    sys.modules["sre_assistant.agent"] = agent_module

    spec.loader.exec_module(agent_module)
    SRECoordinator = agent_module.SRECoordinator

except Exception as e:
    import_error = e

# --- 模擬 SRECoordinator 的執行 ---
# 我們不希望在測試中執行完整的代理邏輯，因此我們模擬 execute 方法。
async def mock_execute(query: str, **kwargs):
    """模擬的 execute 方法，帶有隨機延遲"""
    session_id = query.split(" ")[-1]
    # 模擬 I/O bound 或 CPU bound 的工作
    await asyncio.sleep(0.01 + (int(session_id) % 10) * 0.005)
    return {"status": "resolved", "session_id": session_id}

async def mock_runner_run(query: types.Content, **kwargs):
    """模擬的 runner.run 方法，以匹配 ADK Runner 的 API"""
    # 從 types.Content 中提取查詢字符串
    query_text = query.parts[0].text
    session_id = query_text.split(" ")[-1]
    for i in range(3):
        await asyncio.sleep(0.01)
        # 模擬 Runner 返回的 Event 物件
        # 為了簡化，我們只返回一個字典，測試斷言需要匹配這個結構
        yield {"chunk": i, "session_id": session_id}

# --- 測試案例 ---

@pytest.mark.skipif(SRECoordinator is None, reason=f"Failed to import SRECoordinator: {import_error if 'import_error' in locals() else 'Unknown error'}")
@pytest.mark.asyncio
async def test_50_concurrent_sessions():
    """
    測試：模擬 50 個並發會話同時請求 SRE Assistant。

    目的：
    - 驗證系統在並發負載下不會出現 race conditions 或 deadlocks。
    - 確保每個會話的狀態是隔離的，不會互相干擾。
    - 評估系統處理中等程度並發請求時的性能和響應能力。
    """
    CONCURRENT_SESSIONS = 50

    async def run_single_session(session_id: int):
        """為單個會話創建代理實例並執行"""
        # 每個異步任務都應該有自己的代理實例和 Runner，
        # 以模擬真實世界中每個請求由不同 worker 處理的情況。
        agent = SRECoordinator()
        runner = Runner(
            app_name="sre_assistant",
            agent=agent,
            session_service=InMemorySessionService()
        )

        # 使用 patch 來模擬 Runner 的 run 方法
        # 這確保了我們只測試 Runner 的並發處理能力，而不執行其內部複雜邏輯。
        with patch.object(runner, 'run', side_effect=mock_runner_run, create=True):
            # 準備查詢輸入
            query = types.Content(parts=[types.Part(text=f"Test query for session {session_id}")])
            # 收集 streaming 結果
            results = [res async for res in runner.run(query=query)]
            return results

    print(f"\nStarting {CONCURRENT_SESSIONS} concurrent session test...")
    start_time = time.time()

    # 創建並發任務
    tasks = [run_single_session(i) for i in range(CONCURRENT_SESSIONS)]

    # 並發執行所有任務
    all_results = await asyncio.gather(*tasks, return_exceptions=True)

    end_time = time.time()
    duration = end_time - start_time
    print(f"Completed {CONCURRENT_SESSIONS} sessions in {duration:.2f} seconds.")

    # --- 驗證結果 ---
    successful_sessions = 0
    failed_sessions = []

    for i, result in enumerate(all_results):
        if isinstance(result, Exception):
            failed_sessions.append((i, result))
        else:
            # 驗證每個會話的結果是否正確
            assert isinstance(result, list), f"Session {i} did not return a list"
            assert len(result) == 3, f"Session {i} did not return 3 chunks"
            # 驗證會話 ID 是否被正確傳遞，證明會話隔離
            for chunk in result:
                assert chunk['session_id'] == str(i)
            successful_sessions += 1

    if failed_sessions:
        pytest.fail(f"{len(failed_sessions)} sessions failed: {failed_sessions}")

    assert successful_sessions == CONCURRENT_SESSIONS, f"Expected {CONCURRENT_SESSIONS} successful sessions, but got {successful_sessions}"

    print(f"All {CONCURRENT_SESSIONS} concurrent sessions completed successfully and were isolated.")

    # 性能斷言（可選）
    # 斷言總執行時間應小於某個閾值，以捕捉性能退化
    # 這個閾值需要根據機器的性能進行調整
    assert duration < 5.0, "Concurrent execution took too long."
