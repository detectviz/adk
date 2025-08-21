## v14 任務

1. Session 支援可切換 InMemorySessionService 跟 DatabaseSessionService 。
2. 將 HITL 由政策閘改為 request_credential 互動流，並在前端處理 adk_request_credential 事件。
3. 以下範例映射表可以參考，請全面檢視是否有達到最佳實踐。(檔案在 python.zip 裡面)
4. 程式碼都需要繁中註解。

## 參考資料

ADK 官方網站：https://google.github.io/adk-docs
官方GitHub範例： https://github.com/google/adk-samples

## 範例映射表

基於 ADK 官方範例庫的實際專案，映射到 SRE Assistant 的技術實現：

| ADK 範例 | SRE 模組 | 關鍵接口 | 實現重點 | 測試策略 |
|----------|----------|----------|----------|----------|
| **camel/** | SecurityPolicy | `evaluate_tool_call()` | CaMeL 安全框架，細粒度權限控制，防止注入攻擊 | 安全邊界測試、注入防護測試 |
| **software-bug-assistant/** | DiagnosticExpert | `analyze_issue()` | 整合內部票務系統、GitHub MCP、StackOverflow、RAG 搜尋 | 資料源整合測試、診斷準確性測試 |
| **travel-concierge/** | RemediationExpert | `plan_workflow()` | 多階段工作流編排（pre-trip/in-trip/post-trip） | 工作流程測試、狀態轉換測試 |
| **fomc-research/** | PostmortemExpert | `analyze_documents()` | PDF 文件分析、會議記錄摘要、根因定位 | 文件處理測試、分析品質測試 |
| **personalized-shopping/** | MainAgent | `session_management()` | 使用者偏好學習、多輪對話管理、個性化推薦 | 對話連貫性測試、推薦相關性測試 |
| **machine-learning-engineering/** | AutoRemediationAgent | `optimize_solution()` | 自動模型選擇、參數調優、效能優化 | 優化效果測試、自動化程度測試 |
| **marketing-agency/** | ConfigExpert | `generate_configs()` | 基礎設施即代碼、配置生成、策略制定 | 配置正確性測試、生成品質測試 |
| **auto-insurance-agent/** | PolicyEngine | `validate_actions()` | API 整合（Apigee）、業務規則引擎、審批流程 | 規則引擎測試、API 互動測試 |
| **data-science/** | MetricsAnalyzer | `analyze_patterns()` | 時間序列分析、異常檢測、預測模型 | 預測準確度測試、異常檢測率測試 |
| **image-scoring/** | ComplianceChecker | `validate_compliance()` | 策略合規檢查、評分機制、自動審核 | 合規性測試、評分一致性測試 |
| **vertex-ai-retrieval-agent/** | KnowledgeBase | `rag_search()` | Vertex AI RAG Engine 整合、向量搜尋、引用追蹤 | RAG 準確性測試、引用完整性測試 |

### 技術借鑒重點

#### 從 software-bug-assistant 學習：
- **MCP Toolbox 整合**：用於資料庫操作
- **GitHub MCP Server**：外部問題追蹤
- **Cloud SQL + RAG**：向量搜尋與相似問題匹配
- **應用到 SRE**：診斷相似故障、知識庫搜尋

#### 從 camel 學習：
- **安全策略引擎**：執行前檢查、資料流控制
- **QLLM/PLLM 分離**：程式碼生成與執行隔離
- **應用到 SRE**：生產環境操作審批、敏感資料保護

#### 從 travel-concierge 學習：
- **多階段 Agent 協作**：planning → booking → in-trip → post-trip
- **狀態持久化**：session state 管理
- **應用到 SRE**：故障處理流程（檢測→診斷→修復→覆盤）

#### 從 machine-learning-engineering 學習：
- **自動優化循環**：模型選擇→訓練→評估→優化
- **程式碼生成與執行**：動態生成解決方案
- **應用到 SRE**：自動修復腳本生成、性能調優