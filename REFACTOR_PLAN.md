# REFACTOR_PLAN.md - SRE Assistant 程式碼重構計畫

本文件提供詳細的模組級重構指南，作為 [TASKS.md](TASKS.md) 的技術實施配套文件。

---

## 🎯 重構總體策略

### 核心原則
1. **漸進式重構**: 每個模組獨立重構，確保系統始終可運行
2. **測試驅動**: 先寫測試，再重構，確保功能不受影響
3. **向後相容**: 保持 API 介面穩定，內部實現逐步優化
4. **文檔同步**: 每次重構都更新相關文檔和註釋

### 優先順序
1. **Phase 1**: 核心工作流程 (`workflow.py`)
2. **Phase 2**: 子代理重構 (`sub_agents/`)
3. **Phase 3**: 整合層優化 (`auth/`, `session/`, `memory/`)
4. **Phase 4**: 工具與配置 (`tools.py`, `config/`)

---

## 📦 模組重構計畫

### 1. 主工作流程重構 (`workflow.py`)

#### 當前狀態
```python
# 現有實現 - 靜態條件邏輯
class ConditionalRemediation(BaseAgent):
    def _run_async_impl(self, ctx):
        severity = ctx.state['severity']
        if severity == 'P0':
            agent = HITLRemediationAgent()
        elif severity == 'P1':
            agent = AutoRemediationWithLogging()
        # ... 硬編碼邏輯
```

#### 目標架構
```python
# 新實現 - 智慧分診系統
class SREIntelligentDispatcher(BaseAgent):
    """
    動態分診系統，基於 LLM 智慧選擇專家代理
    參考: google-adk-workflows/dispatcher/
    """
    
    def __init__(self):
        # 專家代理註冊表
        self.expert_registry = ExpertRegistry()
        self.expert_registry.register_diagnostic_experts({
            "kubernetes": KubernetesDiagnosticAgent(),
            "database": DatabaseDiagnosticAgent(),
            "network": NetworkDiagnosticAgent(),
            "application": ApplicationDiagnosticAgent()
        })
        self.expert_registry.register_remediation_experts({
            "rollback": RollbackRemediationAgent(),
            "scaling": AutoScalingAgent(),
            "restart": ServiceRestartAgent(),
            "config": ConfigurationFixAgent()
        })
        
        # LLM 決策引擎
        self.dispatcher_llm = LlmAgent(
            model="gemini-2.0-flash",
            instruction=self._build_dispatcher_instruction()
        )
    
    async def _run_async_impl(self, ctx: InvocationContext):
        # 1. 分析診斷結果
        diagnostic_summary = self._summarize_diagnostics(ctx)
        
        # 2. LLM 決定需要的專家
        decision = await self.dispatcher_llm.run_async(
            prompt=f"Alert: {diagnostic_summary}\nSelect experts:"
        )
        
        # 3. 動態構建工作流程
        selected_experts = self._parse_expert_selection(decision)
        
        if len(selected_experts) > 1:
            # 並行執行多個專家
            workflow = ParallelAgent(sub_agents=selected_experts)
        else:
            # 單一專家執行
            workflow = selected_experts[0]
        
        # 4. 執行並返回結果
        result = await workflow.run_async(ctx)
        
        # 5. 記錄決策審計日誌
        await self._log_decision_audit(diagnostic_summary, selected_experts, result)
        
        return result
```

#### 實施步驟
1. **Week 1**: 建立 `ExpertRegistry` 類別和專家代理介面
2. **Week 1**: 實現 LLM 決策引擎和 prompt 工程
3. **Week 2**: 整合到主工作流程，保留舊邏輯作為 fallback
4. **Week 2**: 添加決策審計和監控
5. **Week 3**: 完整測試和性能優化

---

### 2. 驗證機制實現 (`workflow.py` 擴展)

#### 新增驗證階段
```python
class RemediationVerificationPhase(SequentialAgent):
    """
    修復後驗證階段
    參考: google-adk-workflows/self_critic/
    """
    
    def __init__(self):
        super().__init__(
            name="RemediationVerification",
            sub_agents=[
                HealthCheckAgent(),      # 重新執行健康檢查
                MetricsValidationAgent(), # 驗證關鍵指標
                VerificationCriticAgent() # 評估修復效果
            ]
        )

class HealthCheckAgent(BaseAgent):
    """重新執行關鍵診斷檢查"""
    
    async def _run_async_impl(self, ctx):
        # 獲取修復前的問題指標
        original_issues = ctx.state.get('diagnostic_issues', [])
        
        # 重新執行相關檢查
        current_health = await self._run_health_checks(original_issues)
        
        # 比較修復前後
        ctx.state['verification_health'] = current_health
        ctx.state['health_improved'] = self._compare_health(
            original_issues, current_health
        )
        
        return ctx

class VerificationCriticAgent(LlmAgent):
    """評估修復是否成功"""
    
    instruction = """
    分析修復前後的系統狀態，判斷：
    1. 原始問題是否已解決
    2. 是否引入新問題
    3. 系統是否達到預期狀態
    
    輸出: SUCCESS | PARTIAL | FAILED | NEW_ISSUES
    """
```

---

### 3. SLO 管理重構 (`slo_manager.py`)

#### 迭代優化實現
```python
class SLOIterativeOptimizer(LoopAgent):
    """
    SLO 配置迭代優化器
    參考: machine-learning-engineering/optimization/
    """
    
    def __init__(self):
        super().__init__(
            name="SLOOptimizer",
            sub_agent=SLOTuningRound(),
            max_iterations=5,
            termination_condition=self._check_slo_met
        )
        
    def _check_slo_met(self, ctx):
        """檢查 SLO 是否滿足"""
        current_metrics = ctx.state.get('current_slo_metrics', {})
        targets = ctx.state.get('slo_targets', {})
        
        # 所有指標都達標才終止
        return all(
            current_metrics.get(metric, 0) >= target
            for metric, target in targets.items()
        )

class SLOTuningRound(SequentialAgent):
    """單輪 SLO 調優"""
    
    def __init__(self):
        super().__init__(
            name="SLOTuningRound",
            sub_agents=[
                ProposeConfigChange(),    # 提出配置修改
                SimulateImpact(),         # 模擬影響
                ApplyIfBeneficial()       # 條件應用
            ]
        )
```

---

### 4. HITL 重構 (`sub_agents/remediation/`)

#### 異步審批實現
```python
class HITLRemediationAgent(BaseAgent):
    """
    需要人工審批的修復代理
    參考: human_in_loop/agent.py
    """
    
    def __init__(self):
        self.approval_timeout = 300  # 5分鐘超時
        self.notification_channels = ['slack', 'pagerduty']
    
    async def _run_async_impl(self, ctx):
        # 1. 生成審批請求
        approval_request = ApprovalRequest(
            id=str(uuid.uuid4()),
            action=ctx.state['proposed_action'],
            risk_level=self._assess_risk(ctx),
            context=self._build_context_summary(ctx),
            requester='sre_assistant'
        )
        
        # 2. 發送通知
        await self._send_notifications(approval_request)
        
        # 3. 等待審批（使用 LongRunningFunctionTool 模式）
        tool = LongRunningFunctionTool(
            function=self._execute_remediation,
            approval_required=True,
            timeout=self.approval_timeout
        )
        
        # 4. 處理審批結果
        try:
            result = await tool.execute_with_approval(
                approval_request,
                ctx.state['remediation_params']
            )
            ctx.state['remediation_result'] = 'approved_and_executed'
            return result
            
        except ApprovalTimeout:
            ctx.state['remediation_result'] = 'timeout'
            return self._handle_timeout(ctx)
            
        except ApprovalDenied:
            ctx.state['remediation_result'] = 'denied'
            return self._handle_denial(ctx)
```

---

### 5. GitHub 整合實現 (`tools/github_integration.py`)

#### 事件追蹤系統
```python
class SREGitHubIncidentTracker:
    """
    GitHub Issues 事件追蹤
    參考: software-bug-assistant/tools/github_tools.py
    """
    
    def __init__(self):
        self.github_client = GitHubClient()
        self.issue_template = self._load_issue_template()
    
    async def create_incident_issue(self, incident: Incident) -> str:
        """創建事件 Issue"""
        
        # 1. 生成結構化內容
        issue_body = self.issue_template.render(
            incident_id=incident.id,
            severity=incident.severity,
            service=incident.service,
            impact=incident.impact_assessment,
            diagnosis=incident.diagnosis,
            timeline=incident.generate_timeline(),
            action_items=incident.action_items
        )
        
        # 2. 確定標籤和負責人
        labels = self._determine_labels(incident)
        assignees = self._get_oncall_engineers(incident.service)
        
        # 3. 創建 Issue
        issue = await self.github_client.create_issue(
            title=f"[{incident.severity}] {incident.title}",
            body=issue_body,
            labels=labels,
            assignees=assignees
        )
        
        # 4. 關聯相關 PR/Issues
        await self._link_related_items(issue, incident)
        
        return issue.url
```

---

## 🧪 測試策略

### 單元測試覆蓋
- 每個新模組 > 80% 覆蓋率
- 關鍵路徑 100% 覆蓋
- Mock 外部依賴

### 整合測試
- 端到端工作流程測試
- HITL 審批流程模擬
- 故障注入測試

### 性能測試
- 診斷時間 < 15s
- 並發處理 > 10 事件
- Memory 使用 < 2GB

---

## 📊 成功標準

### 代碼品質
- [ ] 所有測試通過
- [ ] 無關鍵 SonarQube 問題
- [ ] 文檔覆蓋率 > 90%

### 功能完整性
- [ ] 智慧分診正確率 > 95%
- [ ] 驗證機制捕獲率 > 90%
- [ ] HITL 響應時間 < 5分鐘

### 性能指標
- [ ] 診斷延遲降低 50%
- [ ] 並發能力提升 3倍
- [ ] 資源使用優化 30%

---

## 🚦 風險管理

| 風險 | 緩解措施 |
|------|----------|
| 重構引入新 bug | 保留舊實現作為 fallback，灰度發布 |
| 性能退化 | 建立基準測試，持續監控 |
| 整合困難 | 模組化設計，獨立測試 |
| 團隊學習曲線 | 提供培訓，詳細文檔 |

---

**文檔維護者**: Google ADK 首席架構師
**最後更新**: 2025-08-25
**版本**: 2.0.0