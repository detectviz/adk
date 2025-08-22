
# 測試：experts/diagnostic.yaml 的 model 能覆蓋 adk.yaml.agent.model（僅檢查合併後設定，不依賴 ADK 套件）
from sre_assistant.core.config import load_combined_config
from pathlib import Path
import yaml

def test_experts_yaml_model_override(tmp_path, monkeypatch):
    # 建立 adk.yaml（agent.model=flash）
    
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