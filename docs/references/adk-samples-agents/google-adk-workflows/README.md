# 多代理旅程規劃系統

一個使用 Google 代理開發套件 (ADK) 建置的精密多代理工作流程，展示了專業化 AI 代理協同解決複雜旅程規劃任務的能力。

## 🏗️ 架構

這個系統並非建置一個龐大的「超級代理」，而是採用一個由專業化 AI 代理組成的團隊，每個代理都是其領域的專家：

### 核心代理

所有基礎代理都整合在 `subagent.py` 中：

1.  **FlightAgent (航班代理)** - 航班預訂專家
    -   處理航班搜尋與預訂
    -   以結構化的 JSON 格式回傳航班詳細資訊
    -   在缺少細節時做出合理的假設

2.  **HotelAgent (飯店代理)** - 飯店預訂專家
    -   管理飯店搜尋與預訂
    -   以 JSON 格式提供住宿詳細資訊
    -   處理各種房型與預訂偏好

3.  **SightseeingAgent (景點代理)** - 旅遊專家
    -   為每個目的地推薦前 2 名的景點
    -   提供時間安排與相關細節
    -   專注於必看景點

4.  **TripSummaryAgent (旅程摘要代理)** - 摘要編譯專家
    -   將旅程詳細資訊彙編成全面的行程
    -   建立結構化的旅遊摘要
    -   將資訊格式化以便於閱讀

### 協調代理

每個協調代理都有自己的資料夾和專屬的 `agent.py`：

5.  **SimpleAgent (簡單代理)** (`simple/`) - 基本旅程協調員
    -   簡單的子代理協調模式
    -   直接管理航班、飯店和景點代理
    -   適合直接了當的旅程規劃

6.  **DispatcherAgent (分派代理)** (`dispatcher/`) - 智慧型請求路由器
    -   分析請求並將其路由至適當的專家
    -   使用代理工具進行靈活的協調
    -   處理從簡單到複雜的多步驟請求

7.  **ParallelAgent (並行代理)** (`parallel/`) - 效率最佳化工具
    -   並行執行航班和飯店代理以提高速度
    -   循序執行：景點 → 並行(航班+飯店) → 摘要
    -   最大化獨立航班和飯店任務的效率

8.  **SelfCriticAgent (自我批判代理)** (`self_critic/`) - 品質保證專家
    -   與並行代理相同的執行方式 (航班+飯店並行)
    -   增加品質控制：旅程摘要審查員與驗證員
    -   確保輸出在交付前符合品質標準

### 工作流程模式

-   **並行執行**：航班和飯店預訂同時進行以提高效率
-   **循序協調**：相依的任務按邏輯順序執行
-   **回饋循環**：內建的品質保證與驗證
-   **狀態管理**：代理透過共享的會話狀態進行溝通

## 🚀 快速入門

### 先決條件

-   Python 3.8+
-   用於 Gemini 模型的 Google API 金鑰

### 安裝

1.  **複製並導覽至專案**：
    ```bash
    git clone <repository-url>
    cd adk_workflows
    ```

2.  **建立並啟用虛擬環境**：
    ```bash
    # 建立虛擬環境
    python -m venv venv

    # 啟用虛擬環境
    # 在 macOS/Linux 上：
    source venv/bin/activate

    # 在 Windows 上：
    # venv\Scripts\activate
    ```

3.  **安裝依賴項**：
    ```bash
    pip install -r requirements.txt
    ```

4.  **設定環境**：
    ```bash
    # 複製環境範本
    cp env.example .env

    # 編輯 .env 並新增您的 Google API 金鑰
    # 從以下網址取得您的金鑰：https://aistudio.google.com/app/apikey
    ```

5.  **啟動網頁介面**：
    ```bash
    adk web
    ```
    這將會開啟一個網頁介面，您可以在其中選擇並測試任何可用的代理。

## 📋 設定

### 環境變數 (.env)

```env
# 必要
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-2.0-flash

# 可選
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## 🏃‍♂️ 使用方式

完成安裝步驟後，只需執行：

```bash
adk web
```

這會開啟一個網頁介面，您可以在其中：
-   選擇 4 個協調代理中的任何一個 (簡單、分派、並行、自我批判)
-   測試不同類型的旅程規劃請求
-   觀察每個代理如何處理各種情境

### 您可以測試的範例請求

-   **簡單**：「幫我找一班去巴黎的班機」
-   **複雜**：「預訂一班去巴黎的班機，並在艾菲爾鐵塔附近找一間飯店」
-   **全面**：「規劃一個為期三天的東京之旅，包含航班、住宿和觀光景點」

## 🎯 代理詳細資訊

### FlightAgent (航班代理)
-   **目的**：專門處理航班預訂與資訊
-   **輸入**：航班偏好、日期、目的地
-   **輸出**：包含航班詳細資訊、價格、預訂狀態的 JSON
-   **特色**：對缺少的細節進行智慧假設

### HotelAgent (飯店代理)
-   **目的**：飯店預訂與住宿管理
-   **輸入**：地點、日期、房型偏好
-   **輸出**：包含飯店詳細資訊、價格、空房情況的 JSON
-   **特色**：房型最佳化、基於地點的建議

### SightseeingAgent (景點代理)
-   **目的**：旅遊推薦與行程規劃
-   **輸入**：目的地、興趣、停留時間
-   **輸出**：包含前 2 名景點、時間、詳細資訊的 JSON
-   **特色**：精選推薦、實用的時間資訊

### TripSummaryAgent (旅程摘要代理)
-   **目的**：品質保證與旅程彙編
-   **元件**：
    -   **TripSummaryAgent**：彙編全面的行程
    -   **TripSummaryReviewer**：品質檢查與驗證
    -   **ValidateTripSummary**：最終核准與回饋
-   **輸出**：經過驗證的完整旅遊行程

## 🔄 工作流程選項

### 簡單工作流程
```
TripPlanner (root_agent) → 協調 FlightAgent + HotelAgent + SightseeingAgent
```

### 分派工作流程
```
DispatcherAgent → 分析請求 → 路由至適當的工具 → 彙編回應
```

### 並行工作流程
```
SightseeingAgent → FlightAgent + HotelAgent (並行) → TripSummaryAgent
```

### 自我批判工作流程
```
SightseeingAgent → FlightAgent + HotelAgent (並行) → TripSummaryAgent → Reviewer → Validator
```

## 🧪 開發

### 專案結構

```
adk_workflows/
├── subagent.py            # 所有核心代理 (航班、飯店、景點、旅程摘要)
├── simple/
│   └── agent.py           # 基本旅程協調員
├── dispatcher/
│   └── agent.py           # 智慧型請求路由器
├── parallel/
│   └── agent.py           # 並行執行最佳化工具
├── self_critic/
│   └── agent.py           # 品質保證工作流程
├── requirements.txt       # 依賴項
├── env.example           # 環境範本
├── README.md             # 文件
└── SETUP_INSTRUCTIONS.md # 設定指南
```

### 新增代理

**核心代理：**
1.  將您的新核心代理新增至 `subagent.py`
2.  視需要在協調代理中匯入並使用

**協調代理：**
1.  建立一個新資料夾：`new_orchestrator/`
2.  新增包含您的協調邏輯的 `agent.py`
3.  從 `subagent.py` 匯入核心代理

## 🎯 多代理架構的優點

1.  **專業化**：每個代理都在其特定領域表現出色
2.  **可擴展性**：易於新增或修改現有代理
3.  **可維護性**：明確的關注點分離
4.  **效率**：對獨立任務進行並行執行
5.  **品質**：內建的審查與驗證流程
6.  **靈活性**：模組化設計便於客製化

## 🤝 貢獻

1.  Fork 儲存庫
2.  建立一個功能分支
3.  新增您的專業代理或增強功能
4.  更新文件
5.  提交拉取請求

## 📜 授權

[在此處新增您的授權資訊]

## 🆘 支援

若有問題與疑問：
-   在儲存庫中開啟一個 issue
-   查看 [Google ADK 文件](https://ai.google.dev/adk)
-   檢閱代理實作範例

---

**使用 Google 代理開發套件 (ADK) 建置** - 透過 Gemini 賦能智慧型多代理工作流程。