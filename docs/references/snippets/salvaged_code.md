# 被挽救的程式碼與邏輯 (Salvaged Code and Logic)

本文件包含在主要架構重構期間，從被刪除的檔案中挽救出的、可能有用的程式碼片段和邏輯。
這些檔案因為其總體結構與目標的 ADK Provider 和 Tool 模型不符而從主要程式碼庫中移除，但其內部邏輯可能對未來的開發有價值。

---

## 1. SLO 錯誤預算計算邏輯

- **來源 (Source):** `src/sre_assistant/slo_manager.py`
- **上下文 (Context):** 此邏輯可在創建標準化的 `SLOQueryTool` 時進行調整。`calculate_burn_rate` 函式包含核心公式，而 `get_alert_for_burn_rate` 函式則包含 Google SRE 手冊推薦的多窗口告警閾值。

```python
from typing import Dict, Any
from datetime import timedelta

def calculate_burn_rate(sli: float, slo_target: float) -> float:
    """
    計算錯誤預算燃燒率。
    燃燒率 = (1 - SLI) / (1 - SLO) = 錯誤率 / 錯誤預算
    """
    # 計算實際錯誤率
    error_rate = 1 - sli
    # 計算允許的錯誤預算
    error_budget = 1 - slo_target

    # 避免除以零的錯誤
    if error_budget == 0:
        return float('inf') if error_rate > 0 else 0

    burn_rate = error_rate / error_budget
    return burn_rate

def get_alert_for_burn_rate(burn_rate: float, window_hours: int) -> Dict[str, Any]:
    """
    根據燃燒率決定是否應觸發告警。
    此策略基於 Google SRE 手冊的多窗口告警方法。
    """
    # 告警閾值:
    # 1小時窗口 > 14.4倍: 會在 2 小時內耗盡月度預算 (緊急)
    # 6小時窗口 > 6倍: 會在 1 天內耗盡月度預算 (嚴重)
    # 72小時 (3天) 窗口 > 1倍: 會在 1 個月內耗盡預算 (警告)
    alert_thresholds = {
        1: (14.4, "CRITICAL"),
        6: (6.0, "HIGH"),
        72: (1.0, "MEDIUM")
    }

    # 獲取當前時間窗口對應的閾值和嚴重性
    threshold, severity = alert_thresholds.get(window_hours, (None, None))

    # 如果燃燒率超過閾值，則構建告警物件
    if threshold and burn_rate > threshold:
        return {
            "fire": True,
            "severity": severity,
            "summary": f"[{severity}] SLO 錯誤預算燃燒率過高！",
            "details": {
                "burn_rate": f"{burn_rate:.2f}x",
                "window_hours": window_hours,
                "threshold": threshold,
            }
        }
    # 若未超過，則返回不需告警
    return {"fire": False}
```

---

## 2. 引用格式化邏輯 (Citation Formatting Logic)

- **來源 (Source):** `src/sre_assistant/citation_manager.py`
- **上下文 (Context):** 這些格式化函式可在設計 RAG 代理的最終輸出呈現時作為參考。可以透過設計 Prompt 來讓代理產生類似的、結構化且易讀的引用來源。

```python
def format_document_citation(source: Dict[str, Any]) -> str:
    """
    格式化文件來源的引用。
    預期輸入: {'type': 'document', 'title': '...', 'section': '...', 'url': '...'}
    """
    title = source.get('title', 'N/A')
    section = source.get('section')
    url = source.get('url')

    citation = f"[文件] 標題: {title}"
    if section:
        citation += f", 章節: {section}"
    if url:
        citation += f" (來源: {url})"
    return citation

def format_config_citation(source: Dict[str, Any]) -> str:
    """
    格式化設定檔來源的引用。
    預期輸入: {'type': 'config', 'file_path': '...', 'key': '...'}
    """
    file_path = source.get('file_path', 'N/A')
    key = source.get('key', 'N/A')
    return f"[設定檔] 路徑: {file_path}, 鍵: {key}"

def format_log_citation(source: Dict[str, Any]) -> str:
    """
    格式化日誌來源的引用。
    預期輸入: {'type': 'log', 'source_name': '...', 'timestamp': '...'}
    """
    source_name = source.get('source_name', 'N/A')
    timestamp = source.get('timestamp', 'N/A')
    return f"[日誌] 來源: {source_name}, 時間戳: {timestamp}"

def format_kb_citation(source: Dict[str, Any]) -> str:
    """
    格式化知識庫文章的引用。
    預期輸入: {'type': 'kb', 'article_id': '...', 'title': '...'}
    """
    article_id = source.get('article_id', 'N/A')
    title = source.get('title', 'N/A')
    return f"[知識庫] 文章ID: {article_id}, 標題: {title}"

def format_generic_citation(source: Dict[str, Any]) -> str:
    """
    格式化通用或未知來源的引用。
    """
    description = source.get('description', '沒有提供描述。')
    return f"[通用來源] {description}"

# 分派器邏輯 (Dispatcher logic)
def format_citations(sources: List[Dict[str, Any]]) -> str:
    """
    將一個來源字典列表，格式化成一個完整的、帶有編號的引用字串。
    """
    if not sources:
        return ""

    # 將來源類型映射到對應的格式化函式
    formatters = {
        "document": format_document_citation,
        "config": format_config_citation,
        "log": format_log_citation,
        "kb": format_kb_citation,
        "generic": format_generic_citation,
    }

    formatted_list = []
    for i, source in enumerate(sources, 1):
        # 根據來源類型選擇格式化函式，若無則使用通用函式
        formatter = formatters.get(source.get("type", "generic"), format_generic_citation)
        formatted_list.append(f"{i}. {formatter(source)}")

    return "引用來源:\n" + "\n".join(formatted_list)
```

---

## 3. ADK 架構模式範例 (ADK Architectural Patterns)

- **來源 (Source):** `review.md`, `review-2.md`
- **上下文 (Context):** 以下程式碼片段是從 ADK 首席架構師的審查報告中提取的核心範例。它們展示了實現 SRE Assistant 進階功能的最佳實踐，應作為 `TASKS.md` 中相關重構任務的主要藍圖。

### 3.1 增強型 SRE 工作流程 (Enhanced SRE Workflow)
```python
# sre_assistant/workflow_enhanced.py
"""增強版 SRE Workflow - 符合 ADK 最佳實踐"""

from typing import Dict, Any, List, Optional
from google.adk.agents import (
    SequentialAgent, 
    ParallelAgent, 
    LoopAgent,
    InvocationContext,
    BeforeAgentCallback,
    AfterAgentCallback
)
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from pydantic import BaseModel

class EnhancedSREWorkflow(SequentialAgent):
    """符合 ADK 最佳實踐的 SRE 工作流程實現"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        diagnostic_phase = self._create_diagnostic_phase()
        remediation_phase = self._create_remediation_phase()
        verification_phase = self._create_verification_phase()
        
        super().__init__(
            name="EnhancedSREWorkflow",
            sub_agents=[
                diagnostic_phase,
                remediation_phase,
                verification_phase
            ],
            before_agent_callback=self._workflow_pre_check,
            after_agent_callback=self._workflow_post_process
        )
    
    def _create_diagnostic_phase(self) -> ParallelAgent:
        """創建符合最佳實踐的並行診斷階段"""
        return ParallelAgent(
            name="DiagnosticPhase",
            sub_agents=[
                # MetricsAnalyzer(), LogAnalyzer(), TraceAnalyzer(), ...
            ],
            aggregation_strategy="custom",
            aggregation_function=self._aggregate_diagnostics,
            timeout_seconds=30,
            allow_partial_failure=True
        )
    
    def _aggregate_diagnostics(self, results: List[Dict]) -> Dict:
        """自定義診斷結果聚合邏輯"""
        # ... 聚合邏輯 ...
        print("Aggregating diagnostic results...")
        return {"aggregated_diagnosis": "...details..."}
    
    def _create_remediation_phase(self) -> 'IntelligentDispatcher':
        """創建智能分診修復階段"""
        return IntelligentDispatcher(
            name="RemediationPhase",
            expert_registry={
                # "k8s_issues": KubernetesRemediationAgent(), ...
            },
            before_agent_callback=self._check_remediation_safety
        )
    
    def _create_verification_phase(self) -> 'VerificationAgent':
        """創建修復後驗證階段 - ADK self-critic 模式"""
        return VerificationAgent(
            name="VerificationPhase",
            sub_agents=[
                # HealthCheckAgent(), SLOValidationAgent(), ...
            ],
            on_failure_callback=self._trigger_rollback
        )
    
    def _workflow_pre_check(self, context: CallbackContext) -> Optional[types.Content]:
        """工作流程開始前的檢查"""
        print("Performing workflow pre-check...")
        return None
    
    def _workflow_post_process(self, context: CallbackContext) -> Optional[types.Content]:
        """工作流程完成後的處理"""
        print("Performing workflow post-process...")
        return None
    
    def _check_remediation_safety(self, context: CallbackContext) -> Optional[types.Content]:
        """修復前的安全檢查"""
        print("Checking remediation safety...")
        # 移至 HumanApprovalTool
        return None
    
    def _trigger_rollback(self, context: CallbackContext):
        """觸發回滾機制"""
        print("Verification failed, triggering rollback...")
        context.state["rollback_required"] = True

# --- 輔助代理與模型 ---

class DispatchDecision(BaseModel):
    """分診決策的結構化輸出"""
    selected_experts: List[str]
    reasoning: str
    confidence: float

class IntelligentDispatcher(LlmAgent):
    """智能分診器 - 動態選擇專家代理"""
    def __init__(self, expert_registry: Dict[str, BaseAgent], **kwargs):
        super().__init__(
            name="IntelligentDispatcher",
            instruction="Analyze the diagnosis and select the best expert(s) to fix the issue.",
            output_schema=DispatchDecision,
            **kwargs
        )
        self.expert_registry = expert_registry

    async def run_async(self, context: InvocationContext):
        decision = await super().run_async(context)
        # ... 根據 decision 執行對應的專家代理 ...
        print(f"Dispatcher decided to run: {decision.selected_experts}")
        return {"status": "dispatched"}

class VerificationAgent(SequentialAgent):
    """修復後驗證代理 - 實現 ADK self-critic 模式"""
    def __init__(self, on_failure_callback=None, **kwargs):
        self.on_failure_callback = on_failure_callback
        super().__init__(**kwargs)
    
    async def run_async(self, context: InvocationContext):
        result = await super().run_async(context)
        # 假設驗證結果儲存在 state 中
        if not context.state.get("verification_passed", False):
            if self.on_failure_callback:
                self.on_failure_callback(context)
        return result
```

### 3.2 標準化工具模式 (Standardized Tool Patterns)

```python
from google.adk.tools import FunctionTool, LongRunningFunctionTool
from google.adk.tools.types import ToolContext, ToolResult, ToolEvent
from typing import Dict, Any, AsyncIterator

# --- 無狀態認證工具 ---
@FunctionTool
async def verify_token(
    token: str,
    tool_context: ToolContext
) -> ToolResult:
    """無狀態的認證工具，狀態由 session state 管理"""
    # 驗證邏輯...
    user_id = "user-123"
    tool_context.session_state["user_id"] = user_id
    return ToolResult(success=True, data={"user_id": user_id})

# --- 標準化人類介入 (HITL) 工具 ---
class HumanApprovalTool(LongRunningFunctionTool):
    """使用 ADK 的長時間運行工具實現 HITL"""
    async def run(self, request: Dict[str, Any]) -> AsyncIterator[ToolEvent]:
        # 1. 發送審批請求
        request_id = "req-abc-123"
        print(f"Human approval requested for action: {request.get('action')}. Request ID: {request_id}")
        yield ToolEvent(type="pending", data={"request_id": request_id})
        
        # 2. 在實際應用中，此處會等待外部回調
        #    此處為模擬，等待 5 秒後自動批准
        # await asyncio.sleep(5) 
        approval_result = {"status": "approved", "approver": "system"}
        
        # 3. 返回最終結果
        yield ToolEvent(type="completed", data=approval_result)
```

### 3.3 ADK 評估框架整合 (Evaluation Framework Integration)
```python
from google.adk.eval import EvaluationFramework

def setup_evaluation():
    """設置 ADK 評估框架的範例"""
    
    # 假設 sre_workflow 是已實例化的 EnhancedSREWorkflow
    sre_workflow = EnhancedSREWorkflow()
    
    # 從 JSONL 文件加載黃金測試案例
    # test_cases = load_test_cases_from_jsonl("eval/golden_dataset.jsonl")
    test_cases = [
        {"input": "API server is down", "expected_output": "k8s_issues"},
        {"input": "Database latency is high", "expected_output": "database_issues"},
    ]

    evaluator = EvaluationFramework(
        agent=sre_workflow,
        test_cases=test_cases,
        metrics=["accuracy", "latency", "cost"]
    )
    
    # 運行評估
    # results = evaluator.run()
    # print(results)
    
    return evaluator
```
