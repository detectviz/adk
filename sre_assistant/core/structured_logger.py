# 結構化日誌模組
import logging
import json
import sys
from typing import Dict, Any

class JsonFormatter(logging.Formatter):
    """將日誌記錄格式化為單行的 JSON 字串。"""
    def format(self, record: logging.LogRecord) -> str:
        log_object: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
        }
        # 如果有額外的資料，將其加入到 log 物件中
        if hasattr(record, 'extra_data') and isinstance(record.extra_data, dict):
            log_object.update(record.extra_data)
        
        return json.dumps(log_object, ensure_ascii=False)

def setup_logging():
    """設定全域的日誌記錄器。"""
    logger = logging.getLogger("sre_assistant")
    logger.setLevel(logging.INFO)
    
    # 避免重複加入 handler
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = JsonFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

# 在模組載入時執行設定
setup_logging()

def get_logger(name: str) -> logging.Logger:
    """獲取一個已設定好的 logger 實例。"""
    return logging.getLogger(name)

def log_event(logger: logging.Logger, event_name: str, data: Dict[str, Any]):
    """記錄一個結構化的事件。
    
    Args:
        logger: logging 的實例。
        event_name: 事件的名稱。
        data: 一個包含事件相關資訊的字典。
    """
    extra_content = {"event": event_name, **data}
    logger.info(f"Event: {event_name}", extra={"extra_data": extra_content})
