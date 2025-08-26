# src/sre_assistant/tests/test_contracts.py
# 說明：此檔案包含對 Pydantic 資料契約的屬性測試。
# 使用 Hypothesis 函式庫自動生成各種有效的輸入資料，
# 以確保模型的穩健性和邊界條件的正確性。
# 參考 ARCHITECTURE.md 第 16.1 節的測試策略。

import pytest
from hypothesis import given, strategies as st
import sys
import os
import importlib.util

# --- 動態導入 contracts 模組 ---
# 說明：與 test_agent.py 相同，我們需要動態載入模組
# 以處理 'sre_assistant' 目錄名稱中的連字號。
SRERequest = None
SeverityLevel = None
import_error = None

try:
    # 設置路徑以允許從 sre_assistant 導入
    current_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    sys.path.insert(0, os.path.abspath(os.path.join(project_root, '..')))

    contracts_module_path = os.path.join(project_root, "contracts.py")
    spec = importlib.util.spec_from_file_location("sre_assistant.contracts", contracts_module_path)
    contracts_module = importlib.util.module_from_spec(spec)

    # 模擬套件結構
    if 'sre_assistant' not in sys.modules:
        sys.modules["sre_assistant"] = importlib.util.module_from_spec(
            importlib.util.spec_from_file_location('sre_assistant', os.path.join(project_root, '__init__.py'))
        )
    sys.modules["sre_assistant.contracts"] = contracts_module

    spec.loader.exec_module(contracts_module)

    # 從已載入的模組中獲取我們需要的類別
    SRERequest = contracts_module.SRERequest
    SeverityLevel = contracts_module.SeverityLevel

except Exception as e:
    import_error = e

# --- Hypothesis 策略定義 ---

# 為 SeverityLevel Enum 定義一個策略
severity_strategy = st.sampled_from(SeverityLevel)

# 為 SRERequest 模型定義一個策略
sre_request_strategy = st.builds(
    SRERequest,
    incident_id=st.uuids().map(str),
    severity=severity_strategy,
    input=st.text(min_size=1, max_size=1000),
    affected_services=st.lists(st.text(min_size=3, max_size=50), max_size=10), # 限制列表大小以加快測試
    context=st.dictionaries(st.text(max_size=20), st.text(max_size=100), max_size=10),
    session_id=st.one_of(st.none(), st.uuids().map(str)),
    trace_id=st.one_of(st.none(), st.uuids().map(str))
)

# --- 測試案例 ---

@pytest.mark.skipif(SRERequest is None, reason=f"Failed to import SRERequest: {import_error if 'import_error' in locals() else 'Unknown error'}")
@given(request_data=sre_request_strategy)
def test_sre_request_contract_validation(request_data: SRERequest):
    """
    測試：SRERequest 模型是否能成功處理由 Hypothesis 生成的各種有效資料。

    目的：
    - 驗證 Pydantic 模型的類型註解和驗證器是否穩健。
    - 確保模型在處理各種邊界情況（如空列表、特殊字符等）時不會崩潰。
    - 確認模型的預設值和可選欄位行為符合預期。
    """
    assert isinstance(request_data, SRERequest), "Instance should be of type SRERequest"
    assert request_data.incident_id is not None, "incident_id should always be present"
    assert request_data.severity in SeverityLevel, "severity must be a valid SeverityLevel"
    print(f"Successfully validated SRERequest with incident_id: {request_data.incident_id}")

def test_placeholder_for_other_contracts():
    """
    預留位置測試：提醒我們為其他契約模型（如 SREResponse, AgentState）添加測試。
    """
    # TODO: 使用 Hypothesis 為 SREResponse 添加測試
    # TODO: 使用 Hypothesis 為 AgentState 添加測試
    # TODO: 使用 Hypothesis 為 SLOStatus 和 ErrorBudgetStatus 添加測試
    pass
