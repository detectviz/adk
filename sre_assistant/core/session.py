# ADK 標準 Session Service 工廠函式
from __future__ import annotations
import os
from typing import TYPE_CHECKING

# 官方 ADK Session 管理元件
from google.adk.sessions import SessionService, InMemorySessionStore

if TYPE_CHECKING:
    from google.adk.sessions import SessionStore

def get_session_service() -> SessionService:
    """工廠函式：根據環境變數，選擇並初始化符合 ADK 標準的 SessionStore，並建立 SessionService。

    支援的後端 (透過環境變數 `SESSION_BACKEND` 設定):
    - `database`: 使用 `DatabaseSessionStore`，將 Session 狀態持久化至資料庫。
        - 需要設定 `DATABASE_URL` 環境變數。
        - 需要安裝 `google-adk[database]` 額外相依性。
    - `memory` (預設): 使用 `InMemorySessionStore`，Session 狀態儲存於記憶體中。

    Returns:
        一個配置好的 `SessionService` 實例。

    Raises:
        RuntimeError: 當設定為 `database` 後端但缺少對應的 URL 或相依性時拋出。
    """
    store: SessionStore
    backend = os.getenv("SESSION_BACKEND", "memory").lower()

    if backend in ("db", "database"):
        try:
            # 延遲導入 (lazy import) 以避免對非資料庫使用者造成不必要的相依性問題。
            from google.adk.sessions import DatabaseSessionStore
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                raise ValueError("環境變數 `SESSION_BACKEND` 設定為 'database'，但未提供 `DATABASE_URL`。")
            store = DatabaseSessionStore(url=database_url)
        except ImportError:
            # 若使用者選擇資料庫後端但未安裝所需套件，應提供明確的錯誤指引。
            raise RuntimeError(
                "若要使用 DatabaseSessionStore，請確保已安裝資料庫相關的額外相依性，例如：`pip install google-adk[database]`。"
            )
        except ValueError as e:
            raise RuntimeError(str(e))
    else:
        # 預設使用記憶體儲存，適用於開發、測試或無狀態的執行環境。
        store = InMemorySessionStore()

    # 使用選擇的儲存後端來建立並回傳標準的 SessionService。
    return SessionService(store=store)
