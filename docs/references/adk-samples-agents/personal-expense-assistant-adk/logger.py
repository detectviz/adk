"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import logging
import sys

# 為 GCP 設定結構化日誌記錄
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 設定處理常式以輸出與 GCP 搭配良好的 JSON 日誌
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


def log_structured(severity, message, **kwargs):
    """
    記錄與 Google Cloud Logging 相容的結構化訊息。

    參數：
        severity：日誌嚴重性（'INFO'、'ERROR'、'WARNING'、'DEBUG'）
        message：主要日誌訊息
        **kwargs：要包含在日誌中的其他鍵值對
    """
    log_entry = {"severity": severity, "message": message, **kwargs}

    json_entry = json.dumps(log_entry)
    if severity == "ERROR":
        logger.error(json_entry)
    elif severity == "WARNING":
        logger.warning(json_entry)
    elif severity == "DEBUG":
        logger.debug(json_entry)
    else:
        logger.info(json_entry)


# 便利方法
def info(message, **kwargs):
    """記錄 INFO 層級的訊息"""
    log_structured("INFO", message, **kwargs)


def error(message, **kwargs):
    """記錄 ERROR 層級的訊息"""
    log_structured("ERROR", message, **kwargs)


def warning(message, **kwargs):
    """記錄 WARNING 層級的訊息"""
    log_structured("WARNING", message, **kwargs)


def debug(message, **kwargs):
    """記錄 DEBUG 層級的訊息"""
    log_structured("DEBUG", message, **kwargs)
