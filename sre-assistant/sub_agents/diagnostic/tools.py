# sre-assistant/sub_agents/diagnostic/tools.py
# 說明：此檔案包含了診斷專家 (DiagnosticExpert) 所使用的工具。
# 根據 ADK 的設計模式，這些工具被實作為獨立的 Python 函數。
# 每個函數都有清晰的類型提示 (type hints) 和文檔字串 (docstring)，
# ADK 框架會利用這些資訊自動為大型語言模型 (LLM) 生成工具的描述。

from typing import Dict, Any, List

# --- 模組級別的客戶端初始化 ---
# 說明：將客戶端在模組加載時初始化一次，以供後續函數調用。
# 在生產級應用中，可能會使用更複雜的模式（如單例或依賴注入）來管理客戶端實例。
try:
    from prometheus_api_client import PrometheusConnect
    prom_client = PrometheusConnect(url="http://prometheus:9090", disable_ssl=True)
except ImportError:
    print("Warning: prometheus_api_client not installed. promql_query tool will not be functional.")
    prom_client = None

# --- 工具函數定義 ---

def promql_query(query: str, time_range: str = "5m") -> Dict[str, Any]:
    """
    對 Prometheus 執行 PromQL 查詢以獲取時間序列監控指標。
    當需要分析如 CPU 使用率、記憶體消耗或服務延遲等指標時，應使用此工具。

    Args:
        query (str): 要執行的 PromQL 查詢語句。例如 'sum(rate(container_cpu_usage_seconds_total{pod="my-pod"}[5m]))'
        time_range (str, optional): 查詢的時間範圍，例如 '5m', '1h'。預設為 '5m'。

    Returns:
        dict: 一個包含查詢結果的字典。
              成功時: {'status': 'success', 'data': [查詢結果]}
              失敗時: {'status': 'error', 'error': '錯誤訊息'}
    """
    if not prom_client:
        return {"status": "error", "error": "prometheus_api_client is not installed."}

    try:
        # 執行查詢
        result = prom_client.custom_query_range(
            query=query,
            start_time=f"now-{time_range}",
            end_time="now",
            step="30s"
        )
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "error": f"Prometheus query failed: {e}"}

def log_search(query: str, time_range: str = "10m") -> Dict[str, Any]:
    """
    (預留位置) 在日誌系統中搜尋與事件相關的日誌。
    當需要尋找錯誤訊息、堆疊追蹤或特定事件的日誌記錄時，應使用此工具。

    Args:
        query (str): 日誌搜尋的關鍵字或查詢語句。
        time_range (str, optional): 搜尋的時間範圍。預設為 '10m'。

    Returns:
        dict: 包含日誌搜尋結果的字典。
    """
    print(f"--- TOOL: log_search(query='{query}', time_range='{time_range}') ---")
    return {"status": "success", "logs": [f"Found log for '{query}' in range {time_range}"]}

def trace_analysis(trace_id: str) -> Dict[str, Any]:
    """
    (預留位置) 分析分散式追蹤以找出延遲瓶頸或錯誤。
    當需要理解一個請求在多個服務之間的完整路徑和耗時時，應使用此工具。

    Args:
        trace_id (str): 要分析的追蹤 ID。

    Returns:
        dict: 包含追蹤分析摘要的字典。
    """
    print(f"--- TOOL: trace_analysis(trace_id='{trace_id}') ---")
    return {"status": "success", "trace_summary": f"Trace {trace_id} shows high latency in the 'service-auth' component."}

def anomaly_detection(metric_name: str) -> Dict[str, Any]:
    """
    (預留位置) 對時間序列數據執行異常檢測。
    當需要自動識別指標數據中的異常模式（如突波、驟降）時，應使用此工具。

    Args:
        metric_name (str): 要進行異常檢測的指標名稱。

    Returns:
        dict: 包含檢測到的異常點列表的字典。
    """
    print(f"--- TOOL: anomaly_detection(metric_name='{metric_name}') ---")
    return {"status": "success", "anomalies": [{"timestamp": "2025-08-23T06:30:00Z", "value": 95.5, "metric": metric_name}]}
