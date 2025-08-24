# A2A 根代理範例

此範例展示如何在代理開發套件 (Agent Development Kit, ADK) 中使用**遠端代理對代理 (Agent-to-Agent, A2A) 代理作為根代理**。這是一種簡化的方法，其中主要代理實際上是一個遠端 A2A 服務，同時也展示如何使用 uvicorn 命令執行遠端代理。

## 總覽

A2A 根代理範例包含：

- **根代理 (Root Agent)** (`agent.py`)：一個遠端 A2A 代理的代理 (proxy)，作為與在獨立伺服器上執行的遠端 a2a 代理通訊的根代理。
- **遠端 Hello World 代理 (Remote Hello World Agent)** (`remote_a2a/hello_world/agent.py`)：在遠端伺服器上執行的實際代理實作，負責處理擲骰子和質數檢查。

## 架構

```
┌─────────────────┐    ┌────────────────────┐
│   根代理        │───▶│   遠端 Hello       │
│ (RemoteA2aAgent)│    │   World 代理       │
│ (localhost:8000)│    │  (localhost:8001)  │
└─────────────────┘    └────────────────────┘
```

## 主要功能

### 1. **遠端 A2A 作為根代理**
- `root_agent` 是一個 `RemoteA2aAgent`，連接到遠端 A2A 服務。
- 展示如何使用遠端代理作為主要代理，而非本地代理。
- 顯示 A2A 架構在分散式代理部署中的靈活性。

### 2. **Uvicorn 伺服器部署**
- 遠端代理使用輕量級的 ASGI 伺服器 uvicorn 提供服務。
- 展示一種不使用 ADK CLI 部署 A2A 代理的簡單方法。
- 說明如何將 A2A 代理公開為獨立的 Web 服務。

### 3. **代理功能**
- **擲骰子**：可以擲可設定面數的骰子。
- **質數檢查**：可以檢查數字是否為質數。
- **狀態管理**：在工具上下文中維護擲骰歷史。
- **平行工具執行**：可以平行使用多個工具。

### 4. **簡單的部署模式**
- 使用 `to_a2a()` 工具將標準 ADK 代理轉換為 A2A 服務。
- 遠端代理部署所需的設定極少。

## 設定與使用

### 前提條件

1. **啟動遠端 A2A 代理伺服器**：
   ```bash
   # 使用 uvicorn 啟動遠端代理
   uvicorn contributing.samples.a2a_root.remote_a2a.hello_world.agent:a2a_app --host localhost --port 8001
   ```

2. **執行主要代理**：
   ```bash
   # 在另一個終端機中，執行 adk web 伺服器
   adk web contributing/samples/
   ```

### 互動範例

當兩個服務都執行後，您可以與根代理進行互動：

**簡單的擲骰子：**
```
User: 擲一個 6 面骰
Bot: 我為您擲出了一個 4。
```

**檢查質數：**
```
User: 7 是質數嗎？
Bot: 是的，7 是質數。
```

**組合操作：**
```
User: 擲一個 10 面骰並檢查它是否為質數
Bot: 我為您擲出了一個 8。
Bot: 8 不是質數。
```

**多次擲骰與質數檢查：**
```
User: 擲一個骰子 3 次並檢查哪些結果是質數
Bot: 我為您擲出了一個 3。
Bot: 我為您擲出了一個 7。
Bot: 我為您擲出了一個 4。
Bot: 3, 7 是質數。
```

## 程式碼結構

### 根代理 (`agent.py`)

- **`root_agent`**：一個 `RemoteA2aAgent`，連接到遠端 A2A 服務。
- **代理卡 URL (Agent Card URL)**：指向遠端伺服器上眾所周知的代理卡端點。

### 遠端 Hello World 代理 (`remote_a2a/hello_world/agent.py`)

- **`roll_die(sides: int)`**：用於擲骰子並具備狀態管理的函式工具。
- **`check_prime(nums: list[int])`**：用於質數檢查的非同步函式。
- **`root_agent`**：具有完整說明的主要代理。
- **`a2a_app`**：使用 `to_a2a()` 工具建立的 A2A 應用程式。



## 疑難排解

**連線問題：**
- 確保 uvicorn 伺服器在 8001 連接埠上執行。
- 檢查是否有防火牆阻擋 localhost 連線。
- 確認根代理設定中的代理卡 URL。
- 檢查 uvicorn 日誌是否有任何啟動錯誤。

**代理無回應：**
- 檢查 uvicorn 伺服器日誌是否有錯誤。
- 確認代理的指令清晰明確。
- 確保 A2A 應用程式已使用正確的連接埠正確設定。

**Uvicorn 問題：**
- 確保模組路徑正確：`contributing.samples.a2a_root.remote_a2a.hello_world.agent:a2a_app`
- 檢查所有相依性是否已安裝。
