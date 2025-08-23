# sre_assistant/slo_manager.py
# 說明：此檔案負責管理服務等級目標 (SLO) 和錯誤預算。
# 它提供了計算錯誤預算燃燒率和根據預算消耗觸發警報的功能。
# 參考 ARCHITECTURE.md 第 12.2 節 和 Google SRE Book 第 4 章。

from typing import Dict, Optional, Any
from datetime import timedelta

class SREErrorBudgetManager:
    """
    管理 SRE 錯誤預算。

    **技術債務實現**
    此類別實現了 tech_debt_checklist.md 中提出的 SRE 量化指標功能。

    Features:
    - 計算多時間窗口的錯誤預算燃燒率。
    - 根據燃燒率閾值觸發警報。
    - 整合 SLO 配置。
    """

    def __init__(self, slo_target: float, slo_window_days: int):
        """
        初始化錯誤預算管理器。

        Args:
            slo_target: 服務等級目標 (e.g., 0.999 for 99.9%)。
            slo_window_days: SLO 的評估窗口天數 (e.g., 30)。
        """
        if not (0 < slo_target < 1):
            raise ValueError("SLO target must be between 0 and 1.")
        self.slo_target = slo_target
        self.slo_window = timedelta(days=slo_window_days)
        self.error_budget = 1 - slo_target
        print(f"Initialized SREErrorBudgetManager with SLO={self.slo_target}, Budget={self.error_budget:.4f}")

    def _fetch_sli_data(self, window: timedelta) -> float:
        """
        模擬從監控系統獲取服務等級指標 (SLI) 數據。
        在實際應用中，這裡會調用 Prometheus, Cloud Monitoring 或其他監控 API。

        Args:
            window: 查詢數據的時間窗口。

        Returns:
            在該窗口內的平均 SLI 值。
        """
        print(f"Fetching SLI data for the last {window}...")
        # 模擬數據：返回一個略低於目標的 SLI 值
        # 例如，如果 SLO 是 0.999，返回一個像 0.9985 這樣的值
        # 燃燒率越高，這個值應該越低
        if window == timedelta(hours=1):
            # 模擬極高的燃燒率，足以觸發 CRITICAL 警報 (e.g., > 14.4x)
            return self.slo_target - (self.error_budget * 15)
        elif window == timedelta(hours=6):
            # 模擬中等燃燒率，足以觸發 HIGH 警報 (e.g., > 6x)
            return self.slo_target - (self.error_budget * 7)
        else:
            # 模擬低燃燒率，足以觸發 MEDIUM 警報 (e.g., > 1x)
            return self.slo_target - (self.error_budget * 1.1)

    def calculate_burn_rate(self, window_hours: int) -> float:
        """
        計算在給定時間窗口內的錯誤預算燃燒率。
        燃燒率 = (1 - SLI) / (1 - SLO) = 錯誤率 / 錯誤預算

        Args:
            window_hours: 計算燃燒率的時間窗口（小時）。

        Returns:
            錯誤預算燃燒率。燃燒率 > 1 表示消耗速度快於預期。
        """
        window = timedelta(hours=window_hours)
        if window > self.slo_window:
            raise ValueError("Calculation window cannot be larger than the SLO window.")

        sli = self._fetch_sli_data(window)
        error_rate = 1 - sli

        if self.error_budget == 0:
            return float('inf') if error_rate > 0 else 0

        burn_rate = error_rate / self.error_budget
        print(f"Window: {window_hours}h, SLI: {sli:.5f}, Error Rate: {error_rate:.5f}, Burn Rate: {burn_rate:.2f}x")
        return burn_rate

    def trigger_alert_if_needed(self, burn_rate: float, window_hours: int):
        """
        根據燃燒率觸發警報 (基於 Google SRE Book 的多窗口警報策略)。

        Args:
            burn_rate: 當前的燃燒率。
            window_hours: 燃燒率對應的時間窗口。
        """
        # 警報閾值 (基於 Google SRE 書籍建議)
        # 1小時窗口 > 14.4x: 會在 2 小時內耗盡月度預算 (緊急)
        # 6小時窗口 > 6x: 會在 1 天內耗盡月度預算 (嚴重)
        # 3天 (72小時) 窗口 > 1x: 會在 1 個月內耗盡預算 (警告)
        alert_thresholds = {
            1: (14.4, "CRITICAL"),
            6: (6.0, "HIGH"),
            72: (1.0, "MEDIUM")
        }

        threshold, severity = alert_thresholds.get(window_hours, (None, None))

        if threshold and burn_rate > threshold:
            self.alert(
                f"[{severity}] SLO budget burn rate is too high!",
                details={
                    "burn_rate": f"{burn_rate:.2f}x",
                    "window_hours": window_hours,
                    "threshold": threshold,
                    "slo_target": self.slo_target
                }
            )

    def alert(self, summary: str, details: Dict[str, Any]):
        """
        模擬發送警報。
        在實際應用中，這裡會整合 PagerDuty, Slack 或其他警報系統。
        """
        print("\n--- 🚨 ALERT TRIGGERED 🚨 ---")
        print(f"Summary: {summary}")
        for key, value in details.items():
            print(f"  - {key}: {value}")
        print("---------------------------\n")


# --- 示例使用 ---
if __name__ == "__main__":
    print("--- SRE Error Budget Manager Demo ---")

    # 假設我們有一個 99.9% 可用性的 SLO，評估週期為 30 天
    slo_manager = SREErrorBudgetManager(slo_target=0.999, slo_window_days=30)

    # --- 場景 1: 嚴重事件，燃燒率急劇上升 ---
    print("\nScenario 1: Critical event, high burn rate in 1-hour window.")
    burn_rate_1h = slo_manager.calculate_burn_rate(window_hours=1)
    slo_manager.trigger_alert_if_needed(burn_rate_1h, window_hours=1)

    # --- 場景 2: 持續性問題，燃燒率在中期窗口較高 ---
    print("\nScenario 2: Ongoing issue, medium burn rate in 6-hour window.")
    burn_rate_6h = slo_manager.calculate_burn_rate(window_hours=6)
    slo_manager.trigger_alert_if_needed(burn_rate_6h, window_hours=6)

    # --- 場景 3: 輕微問題，長期來看消耗預算 ---
    print("\nScenario 3: Minor issue, low burn rate over 3 days.")
    burn_rate_72h = slo_manager.calculate_burn_rate(window_hours=72)
    slo_manager.trigger_alert_if_needed(burn_rate_72h, window_hours=72)
