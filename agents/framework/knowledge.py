
# -*- coding: utf-8 -*-
# 說明：簡易知識管理器（僅供 MVP 使用）。
# - 以記憶體保存執行紀錄，提供「學習模式」與「建議行動」雛形。
# - 後續可替換為資料庫或向量資料庫，並加上檢索與統計。

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

@dataclass
class Execution:
    """單次工具或 Agent 執行的觀測資料。"""
    agent: str
    decision: str
    result: Dict[str, Any]
    ts: float = field(default_factory=lambda: time.time())

@dataclass
class Suggestion:
    """基於歷史的簡易建議結構。"""
    title: str
    reason: str
    actions: List[str]

class KnowledgeManager:
    """極簡知識管理器。

    限制：
    - 僅在記憶體保存，不具備持久化。
    - 建議後續導入事件匯流排與時序資料供更完整分析。
    """
    def __init__(self) -> None:
        self._executions: List[Execution] = []

    async def record_execution(self, agent: str, decision: str, result: Dict[str, Any]) -> None:
        """記錄每次執行（繁體中文註解）。

        參數：
        - agent: 執行者名稱，例如 SREAssistant
        - decision: 主要決策或採取的行動，例如「PromQL 檢查 5xx」
        - result: 執行結果原始資料，建議為可序列化結構
        """
        self._executions.append(Execution(agent=agent, decision=decision, result=result))

    async def learn_pattern(self, executions: Optional[List[Execution]] = None) -> Dict[str, Any]:
        """學習成功模式（簡化版）。

        回傳：
        - 基於關鍵字頻率的粗略統計，用於日後擴充規則。
        """
        data = executions if executions is not None else self._executions
        keyword_count: Dict[str, int] = {}
        for ex in data:
            for k in ("status", "message"):
                val = str(ex.result.get(k, "")).lower()
                if val:
                    keyword_count[val] = keyword_count.get(val, 0) + 1
        return {"keywords": keyword_count, "total": len(data)}

    async def suggest_action(self, context: Dict[str, Any]) -> List[Suggestion]:
        """基於歷史提供建議（簡化版）。

        規則：
        - 若 context 指出 5xx or error，建議查指標與日誌。
        - 否則回傳一般健康檢查建議。
        """
        text = (str(context.get("symptom", "")) + " " + str(context.get("message", ""))).lower()
        if "5xx" in text or "error" in text or "latency" in text:
            return [Suggestion(
                title="優先檢查應用層錯誤率",
                reason="觀察到錯誤關鍵字，建議先比對 SLI 變化再查日誌",
                actions=[
                    "使用 PromQL 檢查 5xx 指標",
                    "使用 LogQL 篩選目標服務的錯誤堆疊",
                    "檢視同時段 Kubernetes 事件與重啟紀錄"
                ]
            )]
        return [Suggestion(
            title="例行健康檢查",
            reason="未偵測到特定錯誤關鍵字",
            actions=[
                "檢查 CPU/記憶體/磁碟 使用率",
                "確認最近配置變更與部署紀錄",
                "抽樣檢視服務日誌是否有異常"
            ]
        )]
