
# -*- coding: utf-8 -*-
# 簡單的 Secrets 管理（以環境變數為資料來源；繁體中文註解）。
import os

class SecretsManager:
    def get_secret(self, name: str) -> str:
        val = os.getenv(name, "")
        if not val:
            # 空字串代表未設定，呼叫端需自行決定是否為致命錯誤
            return ""
        return val
