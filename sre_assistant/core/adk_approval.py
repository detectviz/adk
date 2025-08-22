"""
標準 ADK Approval Framework 實作
替代原有的自訂 request_credential 實作
"""
from __future__ import annotations
import asyncio
import uuid
from typing import Dict, Any, Optional
from enum import Enum
import logging

try:
    from google.adk.approval import ApprovalRequest, RiskLevel, ApprovalStatus
    ADK_APPROVAL_AVAILABLE = True
except ImportError:
    ADK_APPROVAL_AVAILABLE = False

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """風險等級定義"""
    LOW = "LOW"
    MEDIUM = "MEDIUM" 
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ApprovalStatus(Enum):
    """審批狀態"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class StandardApprovalService:
    """標準 ADK Approval Framework 實作"""
    
    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approval_handlers: Dict[str, Any] = {}
    
    async def request_approval(
        self,
        action: str,
        resource: str,
        risk_level: RiskLevel,
        context: Optional[Dict[str, Any]] = None,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        請求審批
        
        Args:
            action: 要執行的操作
            resource: 操作目標資源
            risk_level: 風險等級
            context: 額外上下文信息
            timeout_seconds: 超時時間
            
        Returns:
            審批結果
        """
        if ADK_APPROVAL_AVAILABLE:
            return await self._use_adk_approval(
                action, resource, risk_level, context, timeout_seconds
            )
        else:
            return await self._fallback_approval(
                action, resource, risk_level, context, timeout_seconds
            )
    
    async def _use_adk_approval(
        self,
        action: str,
        resource: str,
        risk_level: RiskLevel,
        context: Optional[Dict[str, Any]],
        timeout_seconds: int
    ) -> Dict[str, Any]:
        """使用官方 ADK Approval Framework"""
        try:
            approval_request = ApprovalRequest(
                action=action,
                resource=resource,
                risk_level=risk_level.value,
                description=f"請求審批執行 {action} 在資源 {resource}",
                context=context or {},
                timeout_seconds=timeout_seconds
            )
            
            response = await approval_request.request()
            
            return {
                "approved": response.status == ApprovalStatus.APPROVED,
                "status": response.status,
                "request_id": response.request_id,
                "reason": response.reason,
                "approver_id": response.approver_id
            }
            
        except Exception as e:
            logger.error(f"ADK 審批請求失敗: {e}")
            # 降級到內建實作
            return await self._fallback_approval(
                action, resource, risk_level, context, timeout_seconds
            )
    
    async def _fallback_approval(
        self,
        action: str,
        resource: str,
        risk_level: RiskLevel,
        context: Optional[Dict[str, Any]],
        timeout_seconds: int
    ) -> Dict[str, Any]:
        """回退到內建審批實作"""
        request_id = str(uuid.uuid4())
        
        # 低風險操作自動通過
        if risk_level == RiskLevel.LOW:
            return {
                "approved": True,
                "status": ApprovalStatus.APPROVED.value,
                "request_id": request_id,
                "reason": "低風險操作自動通過",
                "approver_id": "system"
            }
        
        # 其他操作需要人工審批
        approval_data = {
            "action": action,
            "resource": resource,
            "risk_level": risk_level.value,
            "context": context or {},
            "status": ApprovalStatus.PENDING.value,
            "created_at": asyncio.get_event_loop().time()
        }
        
        self.pending_approvals[request_id] = approval_data
        
        logger.info(
            f"審批請求已提交: {request_id}, 操作: {action}, 資源: {resource}, 風險等級: {risk_level.value}"
        )
        
        # 等待審批決定（簡化版實作）
        try:
            await asyncio.wait_for(
                self._wait_for_approval(request_id),
                timeout=timeout_seconds
            )
            
            approval = self.pending_approvals.get(request_id, {})
            return {
                "approved": approval.get("status") == ApprovalStatus.APPROVED.value,
                "status": approval.get("status", ApprovalStatus.EXPIRED.value),
                "request_id": request_id,
                "reason": approval.get("reason", "審批超時"),
                "approver_id": approval.get("approver_id", "unknown")
            }
            
        except asyncio.TimeoutError:
            self.pending_approvals[request_id]["status"] = ApprovalStatus.EXPIRED.value
            return {
                "approved": False,
                "status": ApprovalStatus.EXPIRED.value,
                "request_id": request_id,
                "reason": "審批超時",
                "approver_id": None
            }
    
    async def _wait_for_approval(self, request_id: str):
        """等待審批決定"""
        while True:
            approval = self.pending_approvals.get(request_id)
            if not approval or approval["status"] != ApprovalStatus.PENDING.value:
                break
            await asyncio.sleep(1)
    
    def submit_approval_decision(
        self,
        request_id: str,
        approved: bool,
        approver_id: str,
        reason: str = ""
    ) -> bool:
        """提交審批決定"""
        if request_id not in self.pending_approvals:
            return False
        
        approval = self.pending_approvals[request_id]
        if approval["status"] != ApprovalStatus.PENDING.value:
            return False
        
        approval.update({
            "status": ApprovalStatus.APPROVED.value if approved else ApprovalStatus.REJECTED.value,
            "approver_id": approver_id,
            "reason": reason,
            "decided_at": asyncio.get_event_loop().time()
        })
        
        logger.info(
            f"審批決定已提交: {request_id}, 結果: {'通過' if approved else '拒絕'}, "
            f"審批人: {approver_id}, 原因: {reason}"
        )
        
        return True
    
    def get_pending_approvals(self) -> Dict[str, Dict[str, Any]]:
        """獲取待審批的請求"""
        return {
            request_id: approval
            for request_id, approval in self.pending_approvals.items()
            if approval["status"] == ApprovalStatus.PENDING.value
        }

# 全局審批服務實例
_approval_service = StandardApprovalService()

async def request_approval(
    action: str,
    resource: str,
    risk_level: RiskLevel = RiskLevel.MEDIUM,
    context: Optional[Dict[str, Any]] = None,
    timeout_seconds: int = 300
) -> Dict[str, Any]:
    """
    請求審批的便利函數
    
    Args:
        action: 要執行的操作
        resource: 操作目標資源  
        risk_level: 風險等級
        context: 額外上下文信息
        timeout_seconds: 超時時間
        
    Returns:
        審批結果
    """
    return await _approval_service.request_approval(
        action, resource, risk_level, context, timeout_seconds
    )

def submit_approval_decision(
    request_id: str,
    approved: bool,
    approver_id: str,
    reason: str = ""
) -> bool:
    """提交審批決定的便利函數"""
    return _approval_service.submit_approval_decision(
        request_id, approved, approver_id, reason
    )

def get_pending_approvals() -> Dict[str, Dict[str, Any]]:
    """獲取待審批請求的便利函數"""
    return _approval_service.get_pending_approvals()