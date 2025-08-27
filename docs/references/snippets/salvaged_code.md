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
