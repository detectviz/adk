# sre-assistant/a2a/protocol.py
# 說明：此檔案定義了 A2A (Agent-to-Agent) Streaming 的標準化資料契約。
# 參考 ARCHITECTURE.md 第 6.1 節的 StreamingChunk 設計。

from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime
import uuid

class StreamingChunk(BaseModel):
    """
    A2A Streaming 資料塊的標準化 Pydantic Schema。

    此模型確保了在 streaming 通訊中傳輸的每個數據塊都具有
    一致且可驗證的結構。
    """
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="每個數據塊的唯一標識符")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="數據塊生成的時間戳")
    type: Literal["progress", "partial_result", "metrics_update", "final_result", "error"] = Field(..., description="數據塊的類型")

    # 根據類型可選的欄位
    progress: Optional[float] = Field(None, description="操作的進度，介於 0.0 和 1.0 之間")
    partial_result: Optional[Dict[str, Any]] = Field(None, description="部分的、非最終的結果")
    final_result: Optional[Dict[str, Any]] = Field(None, description="最終的、完整的結果")
    metrics_update: Optional[Dict[str, Any]] = Field(None, description="即時指標更新")
    error_details: Optional[Dict[str, Any]] = Field(None, description="當 type 為 'error' 時的錯誤詳情")

    # 用於確保冪等性 (idempotency)
    idempotency_token: str = Field(..., description="用於防止重複處理的冪等性令牌")

    class Config:
        """Pydantic 模型配置"""
        # 允許在模型實例上賦任意屬性
        extra = "allow"
        # 使用 JSON 編碼器來處理 datetime 等複雜類型
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
