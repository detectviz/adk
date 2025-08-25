# Marvin 聯絡人提取代理 (A2A 範例)

此範例展示了一個使用 [Marvin](https://github.com/prefecthq/marvin) 框架從文字中提取結構化聯絡資訊的代理，並與代理對代理 (A2A) 協定整合。

## 總覽

該代理接收文字，並嘗試使用 Marvin 將聯絡人詳細資訊（姓名、電子郵件、電話等）提取為結構化格式。它透過多輪對話管理對話狀態，以在確認提取的資料之前收集必要的資訊（姓名、電子郵件）。代理的回應透過 A2A 同時包含文字摘要/問題和結構化資料。

## 主要元件

- **Marvin `ExtractorAgent` (`agent.py`)**：使用 `marvin` 進行提取並透過字典管理多輪狀態的核心邏輯。
- **A2A `AgentTaskManager` (`task_manager.py`)**：將代理與 A2A 協定整合，管理任務狀態（包括透過 SSE 串流）和回應格式。
- **A2A 伺服器 (`__main__.py`)**：託管代理和任務管理器。

## 先決條件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- `OPENAI_API_KEY`（或 pydantic-ai 支援的其他 LLM 供應商憑證）

## 設定與執行

1. 導覽至 Python 範例目錄：

    ```bash
    cd samples/python/agents/marvin
    ```

2. 設定 LLM 供應商 API 金鑰：

    ```bash
    export OPENAI_API_KEY=your_api_key_here
    ```

3. 設定 Python 環境：

    ```bash
    uv venv
    source .venv/bin/activate
    uv sync
    ```

4. 執行 Marvin 代理伺服器：

    ```bash
    # 預設主機/埠 (localhost:10030)
    MARVIN_DATABASE_URL=sqlite+aiosqlite:///test.db MARVIN_LOG_LEVEL=DEBUG uv run .

    # 自訂主機/埠
    # uv run . --host 0.0.0.0 --port 8080
    ```

    若未設定 `MARVIN_DATABASE_URL`，對話歷史將不會依會話 ID 持久化。

5. 在另一個終端機中，執行 A2A 客戶端（例如，範例 CLI）：

    ```bash
    # 確保環境已啟動 (source .venv/bin/activate)
    cd samples/python/hosts/cli
    uv run . --agent http://localhost:10030 # 使用正確的代理 URL/埠
    ```

## 提取的資料結構

在 `DataPart` 中返回的結構化資料定義如下：

```python
class ContactInfo(BaseModel):
    name: str = Field(description="個人的名字和姓氏")
    email: EmailStr
    phone: str = Field(description="標準化電話號碼")
    organization: str | None = Field(None, description="如果提及，則為組織")
    role: str | None = Field(None, description="如果提及，則為職稱或角色")
```

如果您想讓內容呈現得更好，或者可能序列化一些奇怪的東西，可以使用驗證器。

## 了解更多

- [Marvin 文件](https://www.askmarvin.ai/)
- [Marvin GitHub 儲存庫](https://github.com/prefecthq/marvin)
