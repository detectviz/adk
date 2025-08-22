# 檔案：sre_assistant/core/router.py
# 產生時間：2025-08-22T03:34:52.621849Z
# 專案：SRE Assistant（對齊 Google ADK），本檔案已補齊繁體中文註解以提升可讀性與可維護性。
# 說明：一般模組或測試檔，已加入中文檔頭說明。

from __future__ import annotations
from .intents import Intent

def simple_intent_classifier(text: str) -> Intent:
    """
    2025-08-22 03:37:34Z
    函式用途：`simple_intent_classifier` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `text`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    t = text.lower()
    if any(k in t for k in ["restart","rollout","scale","repair","fix"]):
        return Intent(type="remediation", raw_input=text, confidence=0.8)
    if any(k in t for k in ["postmortem","incident review","timeline"]):
        return Intent(type="postmortem", raw_input=text, confidence=0.8)
    if any(k in t for k in ["provision","dashboard","onboard","monitoring"]):
        return Intent(type="provisioning", raw_input=text, confidence=0.8)
    return Intent(type="diagnostic", raw_input=text, confidence=0.6)