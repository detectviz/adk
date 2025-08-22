
import os
import yaml
from glob import glob

def collect_slo_from_experts(root="experts"):
    rules = {}
    for path in glob(os.path.join(root, "*.yaml")):
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        slo = data.get("slo") or {}
        # Merge by simple dict update
        for k, v in slo.items():
            rules[k] = v
    return rules

def export(out_path="observability/slo_rules.yaml", root="experts"):
    rules = collect_slo_from_experts(root)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(rules, f, sort_keys=True, allow_unicode=True)

if __name__ == "__main__":
    export()
