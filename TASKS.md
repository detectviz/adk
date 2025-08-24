# TASKS.md (待辦事項)

本文件追蹤 SRE Assistant 專案的開發與優化任務，依優先級分類管理。

- 參考資源：[ARCHITECTURE.md](ARCHITECTURE.md#151-參考資源)

## P0 - 必須立即完成（影響系統核心運作）

### 認證授權系統
- **[ ] 認證授權工廠模式設計**：[auth-factory.md](auth-factory.md)
  - [ ] 實作 `AuthProvider` 介面
  - [ ] 整合 IAM、OAuth2、API Key 支援
  - [ ] 實現速率限制和審計日誌

### RAG 引用系統
- **[ ] 標準化引用格式管理**
  - [ ] 實作 `SRECitationFormatter` 類別
  - [ ] 支援配置檔、事件、文檔等多種引用格式
  - [ ] 整合到 `DiagnosticExpert` 輸出

### Session/Memory 持久化
- **[ ] Vertex AI 服務整合**
  - [ ] 遷移到 `VertexAiSessionService`
  - [ ] 實作 `VertexAiMemoryBankService`
  - [ ] 確保會話狀態持久化

## P1 - 重要功能（P0 完成後執行）

### GitHub 整合
- **[ ] 事件追蹤系統**
  - [ ] 實作 `SREIncidentTracker` 類別
  - [ ] GitHub Issues 自動創建和更新
  - [ ] PR 與事件關聯機制

### SRE 量化指標
- **[ ] 完整 SLO 管理系統**
  - [ ] 實作 Error Budget 計算
  - [ ] SLO 違規自動告警
  - [ ] 量化指標儀表板
- **[ ] 五個為什麼 (5 Whys) 模板**
  - [ ] 基於 [Google SRE Book Appendix D](docs/references/google-sre-book/Appendix%20D%20-%20Example%20Postmortem.md) 實作
  - [ ] 自動化根因分析流程

### 迭代優化框架
- **[ ] SLO 配置優化器**
  - [ ] 實作 `SREIterativeOptimizer` 類別
  - [ ] 支援多輪迭代改進
  - [ ] 配置效果評估機制

### MCP 工具箱整合
- **[ ] 資料庫操作標準化**
  - [ ] 整合 MCP Toolbox for Databases
  - [ ] 實作 `SafeSQLQueryBuilder`
  - [ ] 時序資料查詢優化

### 端到端測試
- **[ ] HITL 審批流程測試**
  - [ ] 完整的審批流程端到端測試
  - [ ] 高風險操作模擬
- **[ ] API 端到端測試**
  - [ ] 覆蓋所有 API 端點
  - [ ] 錯誤處理測試

## P2 - 增強功能（長期規劃）

### A2A 協議實現
- **[ ] 代理間通訊**
  - [ ] 實現 `AgentCard` 服務發現
  - [ ] 支援 `RemoteA2aAgent` 調用
  - [ ] 雙向串流通訊支援

### 多模態分析
- **[ ] 視覺內容處理**
  - [ ] 監控面板截圖分析
  - [ ] 日誌圖表識別
  - [ ] 影片內容分析（如操作錄影）

### 可觀測性增強
- **[ ] OpenTelemetry 整合**
  - [ ] 追蹤 (traces) 實現
  - [ ] 自定義指標匯出
  - [ ] 分散式追蹤跨服務

### 部署優化
- **[ ] 進階部署策略**
  - [ ] 金絲雀 (Canary) 部署
  - [ ] 藍綠 (Blue-Green) 部署
  - [ ] SLO 違規自動回滾

### 基礎設施即程式碼
- **[ ] Terraform 模組**
  - [ ] Agent Engine 部署模組
  - [ ] Cloud Run 部署模組
  - [ ] 網路和安全配置

### 容器化優化
- **[ ] Docker 映像檔優化**
  - [ ] 多階段建置
  - [ ] 基礎映像最小化
  - [ ] 安全掃描整合

### 成本優化
- **[ ] 成本分析系統**
  - [ ] 實作 `CostOptimizationAdvisor`
  - [ ] 資源使用分析
  - [ ] 自動化成本節省建議

### 性能基準測試
- **[ ] 完整基準測試套件**
  - [ ] 負載測試腳本
  - [ ] 延遲基準測試
  - [ ] 並發處理測試

## 建議的實施順序

### 第一階段（1-2 週）
1. 完成所有 P0 任務
2. 建立基礎測試框架
3. 確保核心功能穩定

### 第二階段（3-4 週）
1. 實施 P1 中的 GitHub 整合
2. 完成 SRE 量化指標系統
3. 建立 HITL 測試

### 第三階段（5-8 週）
1. 實施迭代優化框架
2. 整合 MCP 工具箱
3. 完成所有 P1 測試

### 第四階段（長期）
1. 逐步實施 P2 功能
2. 根據使用反饋調整優先級
3. 持續優化和改進

## 部署策略建議

### 開發環境
- **配置**：Local + PostgreSQL
- **用途**：功能開發和單元測試
- **成本**：最低

### 測試環境
- **配置**：Cloud Run + Weaviate
- **用途**：整合測試和 UAT
- **成本**：中等

### 生產環境
- **配置**：Agent Engine + Weaviate（成本效益）或 Vertex AI（全託管）
- **用途**：正式服務
- **成本**：依使用量計費

## 監控和維護計劃

### 日常監控
- 使用 `SREErrorBudgetManager` 監控服務健康
- 檢查 SLO 合規性
- 審查錯誤日誌

### 版本管理
- 透過 `VersionedToolRegistry` 管理工具升級
- 確保向後相容性
- 記錄所有變更

### 零停機部署
- 利用配置系統實現熱更新
- 使用金絲雀部署降低風險
- 自動回滾機制

## 注意事項

1. **優先級調整**：可根據實際業務需求調整任務優先級
2. **依賴關係**：某些 P1 任務可能依賴 P0 任務的完成
3. **資源分配**：建議至少分配 2-3 名工程師專注於 P0 任務
4. **文檔更新**：每完成一個任務都應更新相關文檔