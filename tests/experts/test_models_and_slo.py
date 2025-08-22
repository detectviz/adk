
# -*- coding: utf-8 -*-
# 驗證：experts/*.yaml 的 model 與 slo 會被 runtime 提供查詢
import os, yaml
from sre_assistant.adk_app.runtime import get_effective_models, get_slo_targets

def test_model_override_and_slo(tmp_path, monkeypatch):
    os.makedirs('experts', exist_ok=True)
    yaml.safe_dump({'model':'gemini-2.0-pro','slo':{'p95_response_ms': 2000}},
                   open('experts/diagnostic.yaml','w',encoding='utf-8'))
    yaml.safe_dump({'model':'gemini-2.0-flash'},
                   open('experts/remediation.yaml','w',encoding='utf-8'))
    models = get_effective_models()
    assert models.get('diagnostic')=='gemini-2.0-pro'
    assert models.get('remediation')=='gemini-2.0-flash'
    slos = get_slo_targets()
    assert slos.get('diagnostic',{}).get('p95_response_ms')==2000
