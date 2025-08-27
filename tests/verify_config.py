# tests/verify_config.py
# 說明：此腳本用於驗證 ConfigManager 的功能是否如預期。
import os
import sys
import importlib.util
import yaml # 導入 yaml，因為被測試的模組依賴它。

def load_and_print_config(description: str):
    """動態載入並印出 config_manager 的配置。"""
    print(f"--- {description} ---")

    # 定義路徑
    # 假設此腳本從專案根目錄執行。
    # 當前工作目錄應為根目錄。
    sre_assistant_root = os.path.abspath("sre_assistant")
    config_manager_path = os.path.join(sre_assistant_root, "config", "config_manager.py")

    # 我們需要確保 sre_assistant 目錄在搜尋路徑上，
    # 以便 `from enum import Enum` 等導入能夠正常運作。
    if sre_assistant_root not in sys.path:
         sys.path.insert(0, sre_assistant_root)

    # 為了強制重新載入，我們必須先移除已存在的模組。
    module_name = "sre_assistant.config.config_manager"
    if module_name in sys.modules:
        del sys.modules[module_name]

    # 動態載入模組
    spec = importlib.util.spec_from_file_location(module_name, config_manager_path)
    config_module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = config_module
    spec.loader.exec_module(config_module)

    config_manager = config_module.config_manager

    print(f"部署平台 (Deployment Platform): {config_manager.config.deployment.platform.value}")
    print(f"記憶體後端 (Memory Backend): {config_manager.config.memory.backend.value}")
    print(f"PostgreSQL 連線資訊: {config_manager.config.memory.postgres_connection_string}")
    print(f"Weaviate URL: {config_manager.config.memory.weaviate_url}")
    print("-" * 20 + "\n")

# --- 主要驗證邏輯 ---
print("正在驗證 ConfigManager 的載入邏輯...\n")

# 1. 測試預設環境 (應為 'development')
if "ENVIRONMENT" in os.environ: del os.environ["ENVIRONMENT"]
if "MEMORY_BACKEND" in os.environ: del os.environ["MEMORY_BACKEND"]
load_and_print_config("載入預設環境 (預期為 'development')")

# 2. 測試生產環境
os.environ["ENVIRONMENT"] = "production"
load_and_print_config("載入 'production' 環境設定")

# 3. 測試環境變數覆寫
os.environ["ENVIRONMENT"] = "production"
os.environ["MEMORY_BACKEND"] = "redis"
load_and_print_config("測試 'production' 環境並使用 MEMORY_BACKEND 覆寫")

# 清理環境變數
del os.environ["ENVIRONMENT"]
if "MEMORY_BACKEND" in os.environ:
    del os.environ["MEMORY_BACKEND"]

print("驗證完成。")
