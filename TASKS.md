# TASKS.md - SRE Assistant 開發路線圖

本文件為 SRE Assistant 專案的權威任務清單，整合了架構分析、參考範例研究和多方建議後的最終版本。

- **架構基礎**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **參考資源**: [reference-list.md](reference-list.md)
- **重構計畫**: [REFACTOR_PLAN.md](REFACTOR_PLAN.md)

---

## ✅ P0 - 核心基礎設施（已完成）

SRE Assistant 的核心架構已全部完成並通過測試：

### 完成項目
- ✅ **進階工作流程架構**: 成功從 `SequentialAgent` 遷移到混合式工作流程，整合 `ParallelAgent`、`ConditionalAgent`、`LoopAgent`
- ✅ **統一認證系統**: `AuthFactory` 和 `AuthManager` 已實現，支援多種認證方式和 RBAC
- ✅ **RAG 引用系統**: `SRECitationFormatter` 已整合到診斷流程
- ✅ **持久化層**: Session (`FirestoreTaskStore`) 和 Memory (`VertexAIBackend`) 均已實現

**系統已準備好進入功能擴展階段**

---

## 🚨 P0 - 關鍵架構修復 (P1 前置任務)

### 1. 🔐 [P0-CRITICAL] 重構 AuthManager 以支援可擴展狀態管理
**目標**: 將 `AuthManager` 的狀態管理從記憶體遷移到 ADK 的持久化 `SessionService`。

**問題描述**:
目前 `AuthManager` 的快取、速率限制和審計日誌都存在記憶體中。這在多實例部署（GKE/Cloud Run）時會導致狀態不一致、速率限制失效、日誌丟失，完全違背了專案的可擴展性目標。

**解決方案**:
遵循 `sessions-state.md` 官方文件，將狀態存儲在 `context.state` 中，並使用 `user:` 前綴。
- **認證快取**: `context.state['user:auth_cache']`
- **速率限制**: `context.state['user:rate_limit_timestamps']`
- **審計日誌**: 應重構為寫入標準日誌服務 (如 Cloud Logging)，而非 session state。

**參考**: `docs/references/adk-docs/sessions-state.md`
**預期效益**:
- 實現真正的無狀態服務，支援水平擴展
- 確保所有實例間的安全策略一致
- 符合 ADK 最佳實踐

---

## 🔥 P1 - 核心功能升級（當前重點）

以下任務是即將進行的開發週期的主要焦點，按實施順序排列：

### 1. 🧠 [P1-高] 智慧分診系統升級
**目標**: 將現有的靜態 `ConditionalRemediation` 升級為 LLM 驅動的動態分診系統

**實施計畫**:
```python
# 替換現有的條件邏輯
class SREIntelligentDispatcher(BaseAgent):
    """基於 LLM 的動態分診器"""
    def __init__(self):
        self.expert_registry = {
            "k8s_diagnostic": KubernetesDiagnosticAgent(),
            "db_diagnostic": DatabaseDiagnosticAgent(),
            "network_diagnostic": NetworkDiagnosticAgent(),
            "rollback_fix": RollbackRemediationAgent(),
            "scaling_fix": AutoScalingAgent(),
            "config_fix": ConfigurationFixAgent()
        }
```

**參考**: `google-adk-workflows/dispatcher/agent.py`
**預期效益**: 
- 提升 30% 診斷準確率
- 支援動態擴展新專家代理
- 減少硬編碼邏輯

---

### 2. ✔️ [P1-高] 修復後驗證機制
**目標**: 在修復操作後加入自動驗證步驟，確保修復成功且未引入新問題

**實施計畫**:
- 在工作流程中新增 `VerificationPhase`
- 實現 `HealthCheckAgent` 重新執行關鍵診斷
- 實現 `VerificationCriticAgent` 評估修復效果

**參考**: `google-adk-workflows/self_critic/agent.py`
**預期效益**:
- 減少 50% 的修復失敗率
- 自動檢測修復引起的副作用
- 提供修復效果的量化評估

---

### 3. 🐙 [P1-中] GitHub 事件管理系統
**目標**: 實現完整的事件生命週期追蹤

**實施要點**:
- 使用結構化 Markdown 模板創建 issue
- 實現 P0/P1/P2 自動標籤系統
- 建立 PR 與事件的自動關聯

**參考**: `software-bug-assistant/tools/github_tools.py`
**交付標準**:
- [ ] 自動創建事件 issue
- [ ] 狀態同步更新
- [ ] 事後檢討報告自動附加

---

### 4. 📊 [P1-中] SLO 管理與五個為什麼
**目標**: 建立數據驅動的可靠性管理系統

**核心功能**:
```yaml
slo_manager:
  error_budget:
    calculation: automatic
    alerting: multi-window
  five_whys:
    template: google-sre-book
    automation: llm-assisted
```

**參考**: `machine-learning-engineering/optimization/`
**關鍵指標**:
- Error Budget 消耗率實時追蹤
- 多窗口燃燒率警報
- 自動化根因分析報告

---

### 5. 🤝 [P1-中] HITL 審批工作流程
**目標**: 為高風險操作建立人工審批機制

**技術架構**:
- 使用 `LongRunningFunctionTool` 模式
- 整合通知系統 (Slack/PagerDuty)
- 實現審批超時自動處理

**參考**: `human_in_loop/agent.py`
**風險矩陣**:
| 操作 | 開發環境 | 測試環境 | 生產環境 |
|------|---------|---------|---------|
| Pod 重啟 | 自動 | 自動 | 需審批 |
| 配置變更 | 自動 | 需審批 | 需審批 |
| 資料庫故障轉移 | 需審批 | 需審批 | 需審批+確認 |

---

## 🔷 P2 - 長期架構演進

### 1. [P2] A2A 聯邦架構
**願景**: 建立分散式 SRE 專家代理聯邦
- 實現 `AgentCard` 服務發現
- 建立安全的 A2A 通訊協議
- 支援跨團隊代理協作

### 2. [P2] 全面可觀測性
**目標**: 使用 OpenTelemetry 實現端到端追蹤
- 代理決策追蹤
- Token 使用分析
- 性能瓶頸識別

### 3. [P2] 宣告式配置
**轉型**: 從程式碼到 YAML 配置
- 工作流程 YAML 定義
- 動態代理載入
- 熱更新支援

### 4. [P2] 智慧成本優化
**功能**: 自動化成本管理
- Token 使用優化建議
- 資源配置優化
- ROI 分析儀表板

### 5. [P2-Security] 整合 Secret Manager 進行令牌存儲
**目標**: 遵循 ADK 安全最佳實踐，將敏感的認證令牌（特別是刷新令牌）存儲在專用的密鑰管理器中。
**問題描述**: 直接將令牌存儲在會話狀態中會帶來安全風險。
**解決方案**:
1. 將獲取的令牌存儲在 Google Secret Manager 或 HashiCorp Vault 中。
2. 在 `context.state` 中僅存儲對密鑰的引用或短期的訪問令牌。
3. `AuthManager` 在需要時從密鑰管理器中檢索令牌。
**參考**: `docs/references/adk-docs/tools-authentication.md` (Security Warning)
**預期效益**:
- 大幅提升系統安全性，防止令牌洩露。
- 符合生產環境部署的合規性要求。

---

## 📈 關鍵成功指標

### 技術指標
| 指標 | 當前值 | P1 目標 | P2 目標 |
|------|--------|---------|---------|
| 診斷準確率 | 85% | > 95% | > 98% |
| 平均診斷時間 | 30s | < 15s | < 10s |
| MTTR | 30min | < 15min | < 10min |
| 自動修復率 | 60% | > 80% | > 90% |
| 錯誤預算效率 | 70% | > 85% | > 95% |

### 業務價值
| 成果 | 衡量方式 | P1 目標 | P2 目標 |
|------|----------|---------|---------|
| 減少人工介入 | 自動化率 | 75% | 90% |
| 提升可靠性 | SLO 達成率 | 99.9% | 99.95% |
| 降低成本 | 營運成本節省 | 30% | 50% |
| 團隊滿意度 | NPS 分數 | > 7 | > 8.5 |

---

## 🗓️ 實施時間表

### Sprint 1-2 (週 1-4)
- 完成智慧分診系統
- 實現修復後驗證機制
- 開始 GitHub 整合開發

### Sprint 3-4 (週 5-8)
- 完成 GitHub 事件管理
- 實現 SLO 管理系統
- 開發五個為什麼模板

### Sprint 5-6 (週 9-12)
- 完成 HITL 審批流程
- 全面測試 P1 功能
- 準備生產環境部署

### Q2+ (長期)
- 逐步實施 P2 功能
- 根據使用反饋迭代
- 探索新的 AI 能力整合

---

## ⚠️ 風險與緩解

| 風險 | 影響 | 機率 | 緩解策略 |
|------|------|------|----------|
| LLM 分診錯誤 | 高 | 中 | 實施雙重確認機制，保留人工覆核選項 |
| HITL 延遲 | 中 | 高 | 設置合理超時，建立升級路徑 |
| 整合複雜度 | 中 | 中 | 採用漸進式整合，每個系統獨立測試 |
| 成本超支 | 低 | 中 | 實施 Token 預算管理，優化 prompt |

---

## 📝 關鍵決策記錄

### ADR-001: 採用智慧分診替代靜態條件
- **決策**: 使用 LLM 驅動的動態分診
- **原因**: 提高靈活性，支援複雜場景
- **權衡**: 增加延遲，但提升準確性

### ADR-002: HITL 使用 LongRunningFunctionTool
- **決策**: 採用異步審批模式
- **原因**: 避免阻塞，支援並發處理
- **權衡**: 實現複雜度增加

### ADR-003: 優先實施驗證機制
- **決策**: 在新功能前先完善驗證
- **原因**: 確保系統可靠性
- **權衡**: 延後新功能開發

---

**文檔維護者**: Google ADK 首席架構師
**最後更新**: 2025-08-25
**下次審查**: 2025-09-08
**版本**: 3.0.0