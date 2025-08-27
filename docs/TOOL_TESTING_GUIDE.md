# 工具測試指南

本文件概述了在 SRE Assistant 專案中測試工具的最佳實踐。遵守這些指南對於確保我們代理生態系統的可靠性、可預測性和可維護性至關重要。

## 核心理念：獨立測試工具

根據 Google ADK 的官方指南，**工具必須在本地進行隔離測試**。工具是一個獨立的業務邏輯單元，其正確性不應依賴於大型語言模型 (LLM) 或完整的代理工作流程。

工具的單元測試應專注於單一職責：
- 工具是否能正確處理其輸入？
- 在成功的情況下，它是否能產生預期的輸出？
- 它是否能優雅地處理錯誤和邊界情況？
- 它是否如預期般與外部依賴（如 API 或資料庫）互動？（這些依賴應該被**模擬**）。

## 如何撰寫工具測試

我們使用 `pytest` 作為我們的測試框架，並使用 `pytest-asyncio` 來處理異步程式碼。所有的工具測試都應放置在 `tests/` 目錄下，並鏡像 `src/` 目錄的結構。例如，`src/sre_assistant/auth/tools.py` 中工具的測試應位於 `tests/test_auth_tools.py`。

### 範例：測試 `authenticate` 工具

讓我們看看 `tests/test_tools.py` 中對我們 `authenticate` 工具的測試。這可作為未來所有工具測試的模板。

```python
# tests/test_tools.py

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from google.adk.agents.invocation_context import InvocationContext
from src.sre_assistant.auth.tools import authenticate

# 將此檔案中的所有測試標記為異步
pytestmark = pytest.mark.asyncio


@patch('src.sre_assistant.auth.tools.AuthFactory')
@patch('src.sre_assistant.auth.tools.config_manager')
async def test_authenticate_success_and_cache(mock_config_manager, mock_auth_factory):
    """
    測試 authenticate 工具是否能成功驗證使用者、
    返回正確的使用者資訊，並將結果快取到上下文中。
    """
    # 1. 準備 (Arrange): 設定所有模擬物件和測試資料
    # 模擬外部依賴以隔離工具。
    mock_auth_config = MagicMock()
    mock_config_manager.get_auth_config.return_value = mock_auth_config

    mock_provider = AsyncMock()
    mock_provider.authenticate.return_value = (True, {'user_id': 'test-user'})
    mock_auth_factory.create.return_value = mock_provider

    # 為測試創建一個乾淨的 InvocationContext。
    ctx = InvocationContext()
    credentials = {'token': 'valid-token'}

    # 2. 執行 (Act): 使用測試資料呼叫工具函式。
    success, user_info = await authenticate(ctx, credentials)

    # 3. 斷言 (Assert): 驗證結果。
    # 檢查工具的直接輸出。
    assert success is True
    assert user_info == {'user_id': 'test-user'}

    # 檢查模擬的依賴是否被如期呼叫。
    mock_provider.authenticate.assert_called_once_with(credentials)

    # 檢查副作用（例如，對上下文狀態的更改）。
    assert "user_info" in ctx.state
    assert any(key.startswith('user:auth_cache_') for key in ctx.state.keys())

    # 您甚至可以測試更複雜的行為，例如快取。
    # 再次執行並斷言模擬的依賴沒有被再次呼叫。
    await authenticate(ctx, credentials)
    assert mock_provider.authenticate.call_count == 1
```

### 關鍵原則說明

1.  **使用 `@patch` 裝飾器**：`unittest.mock` 中的 `@patch` 裝飾器用於將外部依賴（`AuthFactory`、`config_manager`）替換為模擬物件。這是隔離您的工具最重要的一步。
2.  **準備、執行、斷言 (Arrange, Act, Assert)**：使用此模式清晰地組織您的測試。這使得測試的目的易於理解。
3.  **一次只測試一件事**：每個測試函式都應該有一個單一、明確的目的。在範例中，我們測試了成功和快取路徑。應為身份驗證失敗編寫一個單獨的測試。
4.  **異步模擬**：在模擬異步函式或方法時，請使用 `AsyncMock`。
5.  **檢查輸入、輸出和副作用**：一個好的測試會驗證三件事：
    - **輸出**：返回值是否正確？
    - **依賴呼叫**：模擬的依賴是否被用正確的參數呼叫？（`.assert_called_once_with(...)`）
    - **副作用**：工具是否如預期般修改了 `InvocationContext` 的狀態？

遵循此模板，我們可以為我們的工具建立一個強健的測試套件，這是一個可靠的 SRE Assistant 的基礎。
