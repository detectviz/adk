# ARCHITECTURE 參考

## 參考連結：
- [官方文檔目錄](https://google.github.io/adk-docs/get-started/about/#key-capabilities)
- [基於代理程式的解決方案](https://codelabs.developers.google.com/instavibe-adk-multi-agents/instructions)
- [ADK 專案總覽與架構](https://github.com/google/adk-python/blob/main/contributing/adk_project_overview_and_architecture.md)
- [代理啟動套件](https://github.com/GoogleCloudPlatform/agent-starter-pack)
- [建立智慧 AI 代理程式的綜合指南](https://blog.gopenai.com/googles-agent-development-kit-adk-a-comprehensive-guide-to-building-intelligent-ai-agents-6ef8762e391e) 
- [Google ADK Comprehensive Samples](https://github.com/pawankumar94/agent-development-kit-samples)

---

## ADK 關鍵組件：

![ADK 關鍵組件圖](./adk-components.png)

- **核心組件**：Agents (代理)、Tool (工具)、Orchestration (編排)、Callbacks (回調)。
- **功能組件**：Bidirectional Streaming (雙向串流)、Session Management (會話管理)、Evaluation (評估)、Deployment (部署)。
- **管理組件**：Artifact Management (構件管理)、Memory (記憶)、Code Execution (代碼執行)、Planning (規劃)。
- **支援組件**：Debugging (除錯)、Trace (追蹤)、Models (模型)。

---

## 高階架構組成 ADK High Level Architecture

![ADK 高階架構圖](./adk-high-level-architecture.png)

### 該架構主要分為四個層次：

- **使用者介面(User Interfaces)**：位於最上層，包含
  - 命令列介面(CLI)
  - 網頁使用者介面(Web UI)
  - API 端點(API Endpoints)
  - 自訂前端(Custom Frontend)
  - 提供與使用者互動的管道

- **ADK 執行時與執行器(ADK Runtime & Runner)**：
  - 負責事件循環(Event Loop)
  - 協調(Orchestration)
  - 服務管理(Service Management)

- **代理系統(Agent System)**：
  - LLM 代理(LLM Agents)：負責推理和決策。
  - 工作流程代理(Workflow Agents)：處理順序、並行和循環的工作流程。
      - 順序代理(Sequential Agent)：當您希望執行按照固定、嚴格的順序進行時使用。
      - 並行代理(Parallel Agent)：當子代理彼此之間沒有依賴關係時，它們的任務可以並發執行，從而顯著縮短總體處理時間。
      - 循環代理(Loop Agent)：當您的工作流程涉及重複或迭代改進（例如修改程式碼）時使用。
  - 自訂代理(Custom Agents)：實現專門的行為。

- **基礎組件(Foundation Components)**：位於最底層，提供代理運作所需的基礎功能
  - 會話(Session)
  - 狀態(State)
  - 記憶體(Memory)
  - 事件(Events)
  - 工具(Tools) 
  - 構件(Artifacts)

---

## 基於代理程式的解決方案（原型概念）An Agent-Based Solution (Prototype Concept)

https://codelabs.developers.google.com/instavibe-adk-multi-agents/instructions

- **A Agent**:

- **B Agent**:

- **C Agent**:

- **Orchestrator Agent**: 

---

## ADK Architecture Overview

![ADK Architecture Overview](adk-architecture-overview.gif)

---

## 關鍵建築元素和技術 Key Architectural Elements and Technologies

![ADK 關鍵建築元素和技術圖](./adk-key-architectural-elements-and-technologies.png)

Platform Overview:

- **Models**: 

- **Tools**: 

- **Orchestrator**: 

- **Callbacks**: 
