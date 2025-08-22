
# 測試：experts/diagnostic.yaml 的 model 能覆蓋 adk.yaml.agent.model（僅檢查合併後設定，不依賴 ADK 套件）
from sre_assistant.core.config import load_combined_config
from pathlib import Path
import yaml

def test_experts_yaml_model_override(tmp_path, monkeypatch):
    # 建立 adk.yaml（agent.model=flash）
    """
    2025-08-22 03:37:34Z
    函式用途：`test_experts_yaml_model_override` 的用途請填寫。此為自動生成之繁體中文註解，請依實際邏輯補充。
    參數說明：
    - `tmp_path`：參數用途請描述。
    - `monkeypatch`：參數用途請描述。
    回傳：請描述回傳資料結構與語義。
    """
    adk = {
        "agent": {"model": "gemini-2.0-flash"},
        "experts": {
            "diagnostic": {"tools_allowlist": ["rag_search"]}
        }
    }
    (tmp_path / "adk.yaml").write_text(yaml.safe_dump(adk), encoding="utf-8")
    # 建立 experts/diagnostic.yaml（model=pro）
    (tmp_path / "experts").mkdir(parents=True, exist_ok=True)
    (tmp_path / "experts" / "diagnostic.yaml").write_text("model: gemini-2.0-pro\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    cfg = load_combined_config("adk.yaml")
    assert cfg.get("experts", {}).get("diagnostic", {}).get("model") == "gemini-2.0-pro"