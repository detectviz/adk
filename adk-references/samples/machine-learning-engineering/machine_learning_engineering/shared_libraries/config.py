"""機器學習工程代理的設定。"""

import dataclasses
import os


@dataclasses.dataclass
class DefaultConfig:
    """預設設定。"""
    data_dir: str = "./machine_learning_engineering/tasks/"  # 儲存機器學習任務及其資料的目錄路徑。
    task_name: str = "california-housing-prices"  # 要載入和處理的特定任務的名稱。
    task_type: str = "Tabular Regression"  # 機器學習問題的類型。
    lower: bool = True  # 如果指標值越低越好，則為 True。
    workspace_dir: str = "./machine_learning_engineering/workspace/"  # 用於儲存中繼輸出、結果、日誌的目錄。
    agent_model: str = os.environ.get("ROOT_AGENT_MODEL", "gemini-2.0-flash-001")  # 代理要使用的 LLM 模型名稱。
    task_description: str = ""  # 任務的詳細描述。
    task_summary: str = ""  # 任務的簡潔摘要。
    start_time: float = 0.0  # 表示任務開始時間的時間戳。通常以自 epoch 以來的秒數表示。
    seed: int = 42  # 用於確保實驗可重現性的隨機種子值。
    exec_timeout: int = 600  # 完成任務所允許的最長時間（秒）。
    num_solutions: int = 2  # 為給定任務生成或嘗試的不同解決方案的數量。
    num_model_candidates: int = 2  # 作為候選的不同模型架構或超參數集的數量。
    max_retry: int = 10  # 重試失敗操作的最大次數。
    max_debug_round: int = 5  # 除錯步驟所允許的最大迭代或回合數。
    max_rollback_round: int = 2  # 在發生錯誤或性能不佳時，系統可以回滾到先前狀態的最大次數。
    inner_loop_round: int = 1  # 在系統的內部迴圈中執行的迭代或回合數。
    outer_loop_round: int = 1  # 在外部迴圈中執行的迭代或回合數，可能包含多個內部迴圈。
    ensemble_loop_round: int = 1  # 用於集成、組合多個模型或解決方案的回合或迭代數。
    num_top_plans: int = 2  # 要選擇或保留的得分最高的計畫或策略的數量。
    use_data_leakage_checker: bool = False  # 啟用 (`True`) 或停用 (`False`) 機器學習管線中的資料洩漏檢查。
    use_data_usage_checker: bool = False  # 啟用 (`True`) 或停用 (`False`) 對資料使用方式的檢查，可能用於合規性或最佳實踐。


CONFIG = DefaultConfig()
