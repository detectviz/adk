# sre-assistant/contracts.py - v1.2.1 標準化 API 契約
# 說明：此檔案定義了 SRE Assistant 所有介面的資料模型（契約），
# 使用 Pydantic 進行類型驗證，確保資料的一致性和可靠性。
# 這些模型被用於 API 請求/回應、代理之間的資料傳遞以及狀態管理。
from pydantic import BaseModel, Field, validator, root_validator
from typing import Dict, List, Optional, Union, Literal, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    """SRE 事件嚴重程度等級 (Enum)
    用於標準化事件的優先級，確保所有組件對嚴重性有相同的理解。
    """
    P0 = "P0"  # 關鍵事件，需要立即處理
    P1 = "P1"  # 高優先級事件
    P2 = "P2"  # 中優先級事件
    P3 = "P3"  # 低優先級事件

class RiskLevel(str, Enum):
    """SRE 操作風險等級定義 (Enum)
    用於評估自動化操作可能帶來的風險，是 HITL (Human-in-the-Loop) 審批流程的核心依據。
    """
    LOW = "low"         # 低風險，可自動執行
    MEDIUM = "medium"   # 中等風險，可能需要日誌記錄
    HIGH = "high"       # 高風險，需要人工審批
    CRITICAL = "critical" # 嚴重風險，需要多級審批或立即告警

class SRERequest(BaseModel):
    """標準化 SRE 請求模型 (Pydantic Model)
    定義了向 SRE Assistant 發起請求時的標準格式。
    """
    incident_id: str = Field(..., description="事件的唯一標識符，用於追蹤整個處理流程。")
    severity: SeverityLevel = Field(..., description="事件的嚴重程度，使用 SeverityLevel Enum。")
    input: str = Field(..., min_length=1, description="使用者的原始輸入或告警內容。")
    affected_services: List[str] = Field(default_factory=list, description="受影響的服務列表。")
    context: Dict[str, Any] = Field(default_factory=dict, description="包含額外上下文資訊的字典，如追蹤 ID、日誌連結等。")
    session_id: Optional[str] = Field(None, description="用於保持對話狀態的會話 ID。")
    trace_id: Optional[str] = Field(None, description="用於分散式追蹤的追蹤 ID。")

    @validator('affected_services')
    def validate_services(cls, v):
        """驗證受影響服務的數量不超過限制"""
        if len(v) > 50:  # 避免過大的請求
            raise ValueError('受影響服務的數量不能超過 50 個')
        return v

class SLOStatus(BaseModel):
    """詳細的服務水平目標 (SLO) 狀態模型 (Pydantic Model)
    用於表示一個服務在特定時間點的健康狀況。
    """
    availability_sli: float = Field(..., ge=0.0, le=1.0, description="可用性 SLI 指標值。")
    latency_p95: float = Field(..., ge=0.0, description="P95 延遲（秒）。")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="錯誤率。")
    slo_target: float = Field(..., ge=0.0, le=1.0, description="該服務的 SLO 目標值。")
    is_violation: bool = Field(description="是否已違反 SLO。")
    is_warning: bool = Field(description="是否處於 SLO 警告狀態。")
    is_critical_violation: bool = Field(description="是否處於關鍵違規狀態，可能觸發緊急流程。")
    risk_level: RiskLevel = Field(description="根據 SLO 狀態評估的風險等級。")

    def to_dict(self) -> Dict[str, Any]:
        """將模型轉換為字典，方便序列化。"""
        return self.dict()

class ErrorBudgetStatus(BaseModel):
    """錯誤預算狀態模型 (Pydantic Model)
    用於追蹤服務的錯誤預算消耗情況。
    """
    remaining_percentage: float = Field(..., ge=0.0, le=1.0, description="錯誤預算的剩餘百分比。")
    consumed_this_period: float = Field(..., ge=0.0, description="當前 SLO 週期內已消耗的預算。")
    burn_rate_1h: float = Field(..., ge=0.0, description="過去 1 小時的錯誤預算燃燒率。")
    burn_rate_6h: float = Field(..., ge=0.0, description="過去 6 小時的錯誤預算燃燒率。")
    is_exhausted: bool = Field(description="錯誤預算是否已耗盡。")
    is_low: bool = Field(description="錯誤預算是否處於低水位。")
    estimated_exhaustion_time: Optional[datetime] = Field(None, description="預估的錯誤預算耗盡時間。")

    def to_dict(self) -> Dict[str, Any]:
        """將模型轉換為字典，方便序列化。"""
        return self.dict()

class SREResponse(BaseModel):
    """標準化 SRE 回應模型 (Pydantic Model)
    定義了 SRE Assistant 回應外部呼叫時的標準格式。
    """
    output: str = Field(description="Agent 執行的最終文字輸出。")
    status: Literal["success", "error", "partial"] = Field(description="執行的最終狀態。")
    error: Optional[str] = Field(None, description="如果執行出錯，此處會包含錯誤訊息。")

    # SRE 核心指標
    slo_impact: float = Field(0.0, ge=0.0, le=1.0, description="本次操作對 SLO 的預估影響分數。")
    error_budget_consumed: float = Field(0.0, ge=0.0, description="本次操作消耗的錯誤預算。")
    mttr_contribution: Optional[float] = Field(None, description="本次操作對平均修復時間 (MTTR) 的貢獻（秒）。")

    # v1.2.1 回應品質指標
    response_quality_score: float = Field(0.0, ge=0.0, le=1.0, description="模型回應的品質分數。")
    factual_accuracy: Optional[float] = Field(None, ge=0.0, le=1.0, description="回應內容的事實準確性評分。")
    hallucination_detected: bool = Field(False, description="是否在回應中檢測到幻覺。")

    # 合規性和安全性
    compliance_status: Literal["compliant", "warning", "violation"] = Field("compliant", description="操作的合規狀態。")
    pii_detected: bool = Field(False, description="是否在處理過程中檢測到個人身份資訊 (PII)。")
    safety_violations: List[str] = Field(default_factory=list, description="檢測到的安全違規列表。")

class AgentState(BaseModel):
    """標準化 Agent 狀態模型 (Pydantic Model)
    用於在 Session 中持久化 Agent 的內部狀態。
    """
    current_phase: Literal["idle", "diagnostic", "remediation", "postmortem", "config"] = "idle"
    workflow_progress: float = Field(0.0, ge=0.0, le=1.0, description="當前工作流的完成進度。")

    # 核心狀態
    session_id: Optional[str] = None
    incident_id: Optional[str] = None
    trace_id: Optional[str] = None

    # SRE 特定狀態
    slo_status: Optional[SLOStatus] = None
    error_budget_status: Optional[ErrorBudgetStatus] = None
    current_risk_level: RiskLevel = RiskLevel.MEDIUM

    # 審批和安全狀態
    pending_approvals: List[str] = Field(default_factory=list, description="等待人工審批的項目列表。")
    safety_checks_passed: bool = True
    compliance_validated: bool = True

    class Config:
        # 允許模型包含未明確定義的字段，以增強擴展性。
        extra = "allow"

class RiskAssessment(BaseModel):
    """風險評估結果模型 (Pydantic Model)
    用於封裝對某個操作的完整風險評估結果。
    """
    level: RiskLevel = Field(description="綜合風險等級。")
    requires_approval: bool = Field(description="根據風險等級，此操作是否需要人工審批。")
    reason: str = Field(description="風險評估的詳細理由。")

    # SRE 特定指標
    slo_impact: float = Field(0.0, ge=0.0, le=1.0, description="對 SLO 的潛在影響。")
    error_budget_impact: float = Field(0.0, ge=0.0, le=1.0, description="對錯誤預算的潛在影響。")
    estimated_mttr_impact: Optional[float] = Field(None, description="對 MTTR 的預估影響（秒）。")
    compliance_impact: Optional[str] = Field(None, description="對合規性的潛在影響。")

    # 動態指標
    blast_radius: Optional[str] = Field(None, description="操作的影響範圍（例如，影響的客戶數量、系統模組）。")
    customer_impact_level: Optional[str] = Field(None, description="對客戶的影響程度。")

class SREConfigSchema(BaseModel):
    """Agent 配置文件 (agent_config.json) 的驗證結構 (Pydantic Model)
    用於在載入時驗證配置文件的格式和內容。
    """
    agent_name: str = Field(description="Agent 的名稱。")
    version: str = Field(description="Agent 的版本號。")

    # SRE 指標配置
    slo_targets: Dict[str, float] = Field(description="服務的 SLO 目標值。")
    error_budget_policies: Dict[str, Any] = Field(description="錯誤預算相關的策略配置。")

    # 安全配置
    safety_config: Dict[str, Any] = Field(description="安全框架相關的配置。")
    compliance_requirements: List[str] = Field(description="需要遵守的合規性要求列表。")

    # 監控配置
    monitoring_config: Dict[str, Any] = Field(description="監控系統的端點和認證配置。")

    @validator('slo_targets')
    def validate_slo_targets(cls, v):
        """驗證是否包含所有必要的 SLO 目標"""
        required_targets = ['availability', 'latency_p95', 'error_rate']
        missing = [t for t in required_targets if t not in v]
        if missing:
            raise ValueError(f'缺少必要的 SLO 目標: {missing}')
        return v
