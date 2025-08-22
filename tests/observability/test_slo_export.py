import os, yaml, tempfile, shutil
from scripts.export_slo_rules import export

def test_export_contains_target_key():
    # Prepare a fake experts dir
    tmp = tempfile.mkdtemp()
    try:
        experts = os.path.join(tmp, "experts")
        os.makedirs(experts, exist_ok=True)
        with open(os.path.join(experts, "svcA.yaml"), "w", encoding="utf-8") as f:
            f.write("slo:\n  diagnostic:p95_response_ms:target: 400\n")
        out_path = os.path.join(tmp, "observability/slo_rules.yaml")
        export(out_path=out_path, root=experts)
        with open(out_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert "diagnostic:p95_response_ms:target" in data
        assert data["diagnostic:p95_response_ms:target"] == 400
    finally:
        shutil.rmtree(tmp)
