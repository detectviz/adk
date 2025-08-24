# TASKS.md (待辦事項)

本文件追蹤 SRE Assistant 專案的開發與優化任務，依優先級分類管理。

- 參考資源：[ARCHITECTURE.md](ARCHITECTURE.md#151-參考資源)

## P0 - 必須立即完成（影響系統核心運作）

### 🔄 工作流程架構重構（新增 - 最高優先級）
- **[x] 從 SequentialAgent 遷移到 Workflow 模式** ： [workflows.md](workflows.md)
  - [x] 重構 `SRECoordinator` 採用工作流程架構
  - [x] 實作並行診斷 (`ParallelAgent`)
  - [x] 實作條件修復流程 (`ConditionalAgent`)
  - [x] 整合循環優化機制 (`LoopAgent`)
  - [x] 參考：[google-adk-workflows](docs/references/adk-samples-agents/google-adk-workflows)
  - [x] 參考：`docs/references/adk-python-samples/workflow_triage/` - 動態代理選擇模式
  - [x] 參考：`docs/references/adk-python-samples/multi_agent_loop_config/` - 循環工作流程
  - [x] 參考：`docs/references/adk-python-samples/parallel_functions/` - 並行執行模式

### 認證授權系統
- **[ ] 認證授權工廠模式設計**：[auth-factory.md](auth-factory.md)
  - [ ] 實作 `AuthProvider` 介面
  - [ ] 整合 IAM、OAuth2、API Key 支援
  - [ ] 實現速率限制和審計日誌
  - [ ] 參考：`docs/references/adk-python-samples/a2a_auth/` - OAuth 認證流程
  - [ ] 參考：`docs/references/adk-python-samples/spanner/agent.py` - 多種認證方式實作
  - [ ] 參考：`docs/references/adk-python-samples/google_api/` - Google API OAuth 整合

### RAG 引用系統
- **[ ] 標準化引用格式管理**
  - [ ] 實作 `SRECitationFormatter` 類別
  - [ ] 支援配置檔、事件、文檔等多種引用格式
  - [ ] 整合到 `DiagnosticExpert` 輸出
  - [ ] 參考：`docs/references/adk-samples-agents/RAG/` - 標準引用實作

### Session/Memory 持久化
- **[ ] Vertex AI 服務整合**
  - [ ] 遷移到 `VertexAiSessionService`
  - [ ] 實作 `VertexAiMemoryBankService`
  - [ ] 確保會話狀態持久化
  - [ ] 參考：`docs/references/adk-python-samples/session_state_agent/` - Session 狀態管理
  - [ ] 參考：`docs/references/adk-python-samples/history_management/` - 歷史記錄管理

## P1 - 重要功能（P0 完成後執行）

### GitHub 整合
- **[ ] 事件追蹤系統**
  - [ ] 實作 `SREIncidentTracker` 類別
  - [ ] GitHub Issues 自動創建和更新
  - [ ] PR 與事件關聯機制
  - [ ] 參考：`docs/references/adk-samples-agents/software-bug-assistant/` - GitHub 整合模式

### SRE 量化指標
- **[ ] 完整 SLO 管理系統**
  - [ ] 實作 Error Budget 計算
  - [ ] SLO 違規自動告警
  - [ ] 量化指標儀表板
- **[ ] 五個為什麼 (5 Whys) 模板**
  - [ ] 參考：[google-sre-book.md](google-sre-book.md)
  - [ ] 基於 [Google SRE Book Appendix D](docs/references/google-sre-book/Appendix%20D%20-%20Example%20Postmortem.md) 實作
  - [ ] 自動化根因分析流程

### 迭代優化框架
- **[ ] SLO 配置優化器**
  - [ ] 實作 `SREIterativeOptimizer` 類別
  - [ ] 支援多輪迭代改進
  - [ ] 配置效果評估機制
  - [ ] 參考：`docs/references/adk-samples-agents/machine-learning-engineering/` - 迭代優化模式
  - [ ] 參考：`docs/references/adk-python-samples/multi_agent_loop_config/` - Loop Agent 實作

### MCP 工具箱整合
- **[ ] 資料庫操作標準化**
  - [ ] 整合 MCP Toolbox for Databases
  - [ ] 實作 `SafeSQLQueryBuilder`
  - [ ] 時序資料查詢優化
  - [ ] 參考：`docs/references/adk-samples-agents/software-bug-assistant/tools/database_tools.py`
  - [ ] 參考：`docs/references/adk-python-samples/spanner/` - Spanner 工具整合

### 端到端測試
- **[ ] HITL 審批流程測試**
  - [ ] 完整的審批流程端到端測試
  - [ ] 高風險操作模擬
  - [ ] 參考：`docs/references/adk-python-samples/human_in_loop/` - HITL 完整實作
  - [ ] 參考：`docs/references/adk-python-samples/tool_human_in_the_loop_config/` - HITL 配置
  - [ ] 參考：`docs/references/adk-python-samples/a2a_human_in_loop/` - A2A HITL 模式
- **[ ] API 端到端測試**
  - [ ] 覆蓋所有 API 端點
  - [ ] 錯誤處理測試

## P2 - 增強功能（長期規劃）

### A2A 協議實現
- **[ ] 代理間通訊**
  - [ ] 實現 `AgentCard` 服務發現
  - [ ] 支援 `RemoteA2aAgent` 調用
  - [ ] 雙向串流通訊支援
  - [ ] 參考：`docs/references/adk-python-samples/a2a_auth/` - A2A 認證架構
  - [ ] 參考：`docs/references/adk-python-samples/a2a_human_in_loop/` - A2A HITL 整合
  - [ ] 參考：`docs/references/a2a-samples/` - A2A 協議範例

### 多模態分析
- **[ ] 視覺內容處理**
  - [ ] 監控面板截圖分析
  - [ ] 日誌圖表識別
  - [ ] 影片內容分析（如操作錄影）
  - [ ] 參考：`docs/references/adk-samples-agents/fomc-research/` - 多模態處理

### 可觀測性增強
- **[ ] OpenTelemetry 整合**
  - [ ] 追蹤 (traces) 實現
  - [ ] 自定義指標匯出
  - [ ] 分散式追蹤跨服務
  - [ ] 參考：`docs/references/adk-python-samples/callbacks/` - 回調機制
  - [ ] 參考：`docs/references/adk-python-samples/token_usage/` - 使用量追蹤

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
  - [ ] 參考：`docs/references/adk-python-samples/parallel_functions/` - 並行性能測試

## 建議的實施順序

### 第零階段（立即開始 - 1週）🔥
1. **工作流程架構重構**
   - Day 1-2: 分析現有 SequentialAgent 結構
   - Day 3-4: 實作並行診斷 (ParallelAgent)
   - Day 5-6: 整合條件執行邏輯
   - Day 7: 測試新架構效能提升

### 第一階段（1-2 週）
1. 完成其他 P0 任務（認證、RAG、Session）
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

## 工作流程架構重構詳細計劃（新增）

### 為何是最高優先級？
1. **性能提升**：並行診斷可減少 70% 診斷時間
2. **可維護性**：工作流程模式更清晰、易於調試
3. **擴展性**：便於新增專家代理和條件邏輯
4. **符合 ADK 最佳實踐**：Advanced Workflow Multi-Agent 模式

### 重構路線圖

#### Phase 0: 基礎架構遷移（Day 1-3）
```python
# 從現有架構
class SRECoordinator(SequentialAgent):
    agents = [診斷, 修復, 覆盤, 配置]

# 遷移到工作流程架構
class SREWorkflow(SequentialAgent):
    agents = [
        ParallelDiagnostics(),  # 新增
        ConditionalRemediation(),  # 新增
        PostmortemExpert(),
        IterativeOptimization()  # 新增
    ]
```

#### Phase 1: 並行診斷實作（Day 4-5）
```python
class ParallelDiagnostics(ParallelAgent):
    """並行執行多個診斷任務"""
    sub_agents = [
        PrometheusMetricsAgent(output_key="metrics_analysis"),
        ElasticsearchLogAgent(output_key="logs_analysis"),
        JaegerTraceAgent(output_key="traces_analysis"),
        HistoricalIncidentMatcher(output_key="similar_incidents")
    ]
```

#### Phase 2: 條件修復流程（Day 6-7）
```python
class ConditionalRemediation(BaseAgent):
    """基於風險等級的條件執行"""
    def _run_async_impl(self, ctx):
        severity = ctx.state['severity']
        if severity == 'P0':
            # 需要 HITL 審批
            agent = HITLRemediationAgent()
        elif severity == 'P1':
            # 自動修復但記錄
            agent = AutoRemediationWithLogging()
        else:
            # 計劃性修復
            agent = ScheduledRemediation()
        return agent.run_async(ctx)
```

#### Phase 3: 循環優化機制（Day 7）
```python
class IterativeOptimization(LoopAgent):
    """持續優化直到 SLO 達標"""
    sub_agent = SLOTuningAgent()
    max_iterations = 3
    termination_condition = lambda ctx: ctx.state.get('slo_met', False)
```

### 預期效益

| 指標 | 現狀 | 重構後 | 改善 |
|------|------|--------|------|
| 診斷時間 | 30秒 | 10秒 | -67% |
| 修復準確率 | 85% | 95% | +10% |
| 代碼可維護性 | 中 | 高 | ⬆️ |
| 新功能開發速度 | 2週/功能 | 1週/功能 | -50% |

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

1. **🔥 工作流程架構是基礎**：所有其他 P0 任務都應在新架構上實施
2. **優先級調整**：可根據實際業務需求調整任務優先級，但工作流程架構重構應保持最高優先級
3. **依賴關係**：某些 P1 任務可能依賴 P0 任務的完成
4. **資源分配**：建議至少分配 2-3 名工程師專注於工作流程重構
5. **文檔更新**：每完成一個任務都應更新相關文檔
6. **測試覆蓋**：新的工作流程架構必須有完整的單元測試和整合測試

## 📚 **P0 任務參考對照表**

| 任務 | 主要參考範例 | 路徑 |
|------|------------|------|
| **工作流程架構** | workflow_triage, multi_agent_loop_config, parallel_functions | `adk-python-samples/workflow_triage/`等 |
| **認證授權** | a2a_auth, spanner, google_api | `adk-python-samples/a2a_auth/`等 |
| **Session/Memory** | session_state_agent, history_management | `adk-python-samples/session_state_agent/`等 |

## 📚 **P1 任務參考對照表**

| 任務 | 主要參考範例 | 路徑 |
|------|------------|------|
| **HITL 測試** | human_in_loop, tool_human_in_the_loop_config, a2a_human_in_loop | `adk-python-samples/human_in_loop/`等 |
| **迭代優化** | multi_agent_loop_config | `adk-python-samples/multi_agent_loop_config/` |
| **資料庫工具** | spanner | `adk-python-samples/spanner/` |

## 📚 **P2 任務參考對照表**

| 任務 | 主要參考範例 | 路徑 |
|------|------------|------|
| **A2A 協議** | a2a_auth, a2a_human_in_loop | `adk-python-samples/a2a_auth/`等 |
| **可觀測性** | callbacks, token_usage | `adk-python-samples/callbacks/`等 |
| **並行性能** | parallel_functions | `adk-python-samples/parallel_functions/` |
