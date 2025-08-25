# A2A 猜數字遊戲示範 (Python)

這個儲存庫展示了三個輕量級的 A2A 代理，它們合作玩一個經典的「猜數字」遊戲。

為了讓它成為一個易於理解的 A2A 和 Python SDK 的實用入門介紹，我們刻意讓這個應用程式保持極簡：

- 沒有 LLM、API 金鑰等
- 不需要遠端伺服器（所有 3 個代理都在本地執行）
- 易於安裝和嘗試
- 最少的外部依賴
- 展示 A2A 一些核心概念的最小功能集。

| 代理 | 角色 |
|-------|------|
| **愛麗絲代理 (AgentAlice)** | 挑選一個秘密整數 (1-100) 並對傳入的猜測進行評分。 |
| **鮑伯代理 (AgentBob)**   | CLI 前端 – 轉送玩家的猜測，顯示愛麗絲的提示，並與卡蘿協商。 |
| **卡蘿代理 (AgentCarol)** | 產生猜測歷史的文字視覺化，並應要求將其洗牌，直到鮑伯滿意為止。 |

## 需求

- Python **3.10+**
- `pip`

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```

執行時的依賴極少：官方的 `a2a-sdk` 套件和用於 HTTP 伺服器的 `uvicorn`。

## 執行示範

1. 複製儲存庫並 `cd` 進入該目錄。
2. 開啟**三個終端機**（或窗格）。在每一個終端機中，首先啟動虛擬環境：

   ```bash
   source .venv/bin/activate   # (Windows: .venv\\Scripts\\activate)
   ```

   然後啟動代理：

   ```bash
   # 終端機 1 – 愛麗絲（評估者）
   python agent_Alice.py

   # 終端機 2 – 卡蘿（視覺化/洗牌者）
   python agent_Carol.py

   # 終端機 3 – 鮑伯（CLI 前端）
   python agent_Bob.py
   ```

3. 開始玩吧！鮑伯會提示您輸入數字，直到愛麗絲回覆 `correct! attempts: N`。

在遊戲過程中，鮑伯會重複要求卡蘿重新洗牌歷史記錄，直到它被排序為止——這練習了代理之間的多輪、參考任務的訊息。

## 目錄結構（節略）

```text
number_guessing_game/
├── agent_Alice.py                  # 評估者代理
├── agent_Bob.py                    # CLI 前端代理
├── agent_Carol.py                  # 視覺化/洗牌者代理
├── utils/
│   ├── game_logic.py               # 純遊戲機制（與傳輸無關）
│   ├── helpers.py                  # 小型的通用輔助工具（JSON 解析等）
│   ├── protocol_wrappers.py        # A2A SDK 的便利包裝器
│   ├── server.py                   # 啟動 Starlette + SDK 處理器的輔助工具
│   └── __init__.py                 # 重新匯出
├── config.py                       # 集中式埠口設定
├── requirements.txt                # 執行時依賴
└── README.md                       # ← 您在這裡
```

## A2A 功能涵蓋範圍 (SDK 0.3.x)

大部分繁重的工作（驗證、錯誤對應、任務聚合等）都由 SDK 處理。因此，此示範專注於**代理邏輯**——而不是協定細節。

| 領域 | 狀態 |
|------|--------|
| `message/send` | 透過 SDK 輔助工具實作。 |
| 任務聚合 | 由 `ClientTaskManager` 處理。 |
| 串流與訂閱 | **未實作** – SDK 回傳 `Unsupported operation`。 |
| 推播通知設定 | 未實作（功能旗標為 `false`）。 |
| 傳輸 | 透過 Starlette/Uvicorn 的 JSON-RPC（gRPC 留作練習）。 |
| TLS 與認證 | 僅在 `localhost` 上使用純 HTTP。 |

## 授權

釋出於公共領域。
