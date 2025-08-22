
# 規劃器（Planner）：
# - 依 Intent 產生步驟（Step）序列
# - 支援簡單條件：診斷→若結果為空則補查 RAG；佈署→先建儀表板再查 Runbook
from __future__ import annotations
from typing import List
from .intents import Intent, Step

class RuleBasedPlanner:
    """最小可用 Planner。
    注意：實務可替換為 LLM 驅動的 Planner，或按服務定義 DSL 生成計畫。
    """
    def plan(self, intent: Intent) -> List[Step]:
        """
        2025-08-22 03:37:34Z
        函式用途：`plan` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
        參數說明：
        - `self`：參數用途請描述。
        - `intent`：參數用途請描述。
        回傳：請描述回傳資料結構與語義。
        """
        if intent.type == "diagnostic":
            # 先查 up 指標，再查 Runbook（orders 為範例）
            return [
                Step(tool="PromQLQueryTool", args={"query":"up","range":"5m"}),
                Step(tool="RunbookLookupTool", args={"service":"orders"}),
            ]
        if intent.type == "remediation":
            # 修復一律要求審批
            return [
                Step(tool="K8sRolloutRestartTool", args={"namespace":"staging","deployment_name":"orders-api","reason":"auto"}, require_approval=True)
            ]
        if intent.type == "provisioning":
            return [
                Step(tool="GrafanaDashboardTool", args={"service_type":"webapi"}),
                Step(tool="RunbookLookupTool", args={"service":"orders"}),
            ]
        if intent.type == "postmortem":
            # 後續可接入事件來源工具（暫略）
            return []
        return []