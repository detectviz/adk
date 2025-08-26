# src/sre_assistant/a2a/protocol.py
# 說明：此檔案定義了 A2A (Agent-to-Agent) Streaming 的標準化資料契約。
# 參考 ARCHITECTURE.md 第 6.1 節的 StreamingChunk 設計。
# **技術債務改進**: 根據 `purchasing-concierge` 範例，引入了完整的 A2A Task 協議。

from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List, Union, Callable, Annotated
from datetime import datetime
import uuid
from enum import Enum

# --- 舊版 StreamingChunk (可選，或標記為 deprecated) ---
class StreamingChunk(BaseModel):
    """
    A2A Streaming 資料塊的標準化 Pydantic Schema。
    (注意：此模型為舊版，新協議使用基於 Task 的事件)
    """
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    type: Literal["progress", "partial_result", "metrics_update", "final_result", "error"]
    progress: Optional[float] = None
    partial_result: Optional[Dict[str, Any]] = None
    final_result: Optional[Dict[str, Any]] = None
    metrics_update: Optional[Dict[str, Any]] = None
    error_details: Optional[Dict[str, Any]] = None
    idempotency_token: str

# --- 新版 A2A Task 協議 (基於 purchasing-concierge 範例) ---

class TaskState(str, Enum):
    """定義 A2A 任務的標準狀態"""
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    UNKNOWN = "unknown"

class TextPart(BaseModel):
    type: Literal["text"] = "text"
    text: str

Part = Annotated[Union[TextPart], Field(discriminator="type")]

class Message(BaseModel):
    role: Literal["user", "agent"]
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = None

class TaskStatus(BaseModel):
    state: TaskState
    message: Optional[Message] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Artifact(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = None

class Task(BaseModel):
    id: str
    sessionId: Optional[str] = None
    status: TaskStatus
    artifacts: Optional[List[Artifact]] = None
    history: Optional[List[Message]] = None
    metadata: Optional[Dict[str, Any]] = None

# --- Streaming 和 Callback 定義 ---

class TaskStatusUpdateEvent(BaseModel):
    """任務狀態更新事件"""
    id: str
    status: TaskStatus
    final: bool = False

class TaskArtifactUpdateEvent(BaseModel):
    """任務產物更新事件"""
    id: str
    artifact: Artifact

# **技術債務實現**: 定義 TaskUpdateCallback
TaskCallbackArg = Union[Task, TaskStatusUpdateEvent, TaskArtifactUpdateEvent]
TaskUpdateCallback = Callable[[TaskCallbackArg, 'AgentCard'], None]


# --- Agent Card 定義 (用於服務發現) ---

class AgentCapabilities(BaseModel):
    streaming: bool = False
    pushNotifications: bool = False

class AgentSkill(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    examples: Optional[List[str]] = None

class AgentCard(BaseModel):
    """
    代理卡片，用於向其他代理描述自身能力。
    """
    name: str
    description: Optional[str] = None
    url: str
    version: str
    capabilities: AgentCapabilities
    skills: List[AgentSkill]
    authentication: Optional[Dict[str, Any]] = None # e.g., {"type": "oauth2", "scheme": "bearer"}
