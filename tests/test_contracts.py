# tests/test_contracts.py
"""
此檔案包含對 Pydantic 資料契約的屬性測試。

使用 Hypothesis 函式庫自動生成各種有效的輸入資料，
以確保模型的穩健性和邊界條件的正確性。
"""

import pytest
from hypothesis import given, strategies as st

from sre_assistant.contracts import SRERequest, SeverityLevel

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
