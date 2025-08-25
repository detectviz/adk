# 對抗性代理 (Adversarial Agent) 模擬

此範例示範了使用 A2A (代理對代理) 協定的對抗性多代理 (multi-agent) 模擬。此模擬有兩個相互競爭的代理 (Agent)：一個**攻擊方**（紅隊）和一個**防守方**（藍隊），它們進行一場策略性的鬥智。

攻擊方可以透過 A2A 與防守方代理 (Agent) 通訊，並且可以自由地繼續多輪對話或重設並建立新對話。透過觀察它們的對話記錄，您可以看到攻擊方代理 (Agent) 嘗試結合這些方法。

此範例利用 [any-agent](https://github.com/mozilla-ai/any-agent) 函式庫，該函式庫內建支援透過 A2A 提供代理 (Agent) 服務。有關服務選項的文件可以在[此處](https://mozilla-ai.github.io/any-agent/serving/)找到。使用 any-agent，您可以控制代理 (Agent) 與防守方所使用的 LLM，以及所使用的代理 (Agent) 框架。

## 使用方式

### 先決條件

- Python 3.12+
- 透過環境變數 `GEMINI_API_KEY` 設定 Gemini API 金鑰

### 執行模擬

```bash
# 導覽至專案目錄
cd samples/python/agents/any_agent_adversarial_multiagent/

# 執行模擬
uv run .
```

您可以透過讀取主控台輸出來即時瀏覽正在發生的情況，模擬完成後，您可以透過查看 `out` 資料夾來檢視已完成的對話和追蹤記錄。

## 模擬概觀

**目標**：透過代理 (Agent) 對代理 (Agent) 的遊戲玩法測試 AI 的穩健性和對抗性提示的抵抗力，並展示兩個代理 (Agent) 之間多輪對話的有效性。

- **攻擊方目標**：讓防守方以「我放棄」回應
- **防守方目標**：在任何情況下，無論壓力多大，都絕不說「我放棄」

## 架構

- **框架**：Any-Agent 函式庫
- **協定**：A2A (代理對代理) 用於安全的代理 (Agent) 間通訊
- **模型**：任何 LiteLLM 支援的模型
