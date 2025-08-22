
# 檔案：scripts/export_slo_rules.py
# 用途：將 adk.yaml 與 experts/*.yaml 中的 SLO 門檻導出為 Prometheus 規則（observability/slo_rules.yaml）
# 說明：生成 Recording Rules 與 Alerting Rules，針對每個專家代理（Diagnostic/Remediation/Postmortem/Config）
#      計算 P95 延遲與成功率，並建立對應的警報。
from __future__ import annotations
import os, sys, yaml, datetime
from pathlib import Path

# 為腳本本身加入簡短中文 Docstring
"""
{ts}
函式用途：此模組提供命令列工具，將 SLO 配置轉為 Prometheus 規則檔。
參數說明：透過命令列執行，不接受參數；讀寫路徑為專案固定位置。
回傳：無（在檔案系統寫出 observability/slo_rules.yaml）。
""".format(ts=datetime.datetime.utcnow().isoformat()+"Z")

def _load_yaml(path: Path) -> dict:
    """
    {ts}
    函式用途：載入 YAML 檔並回傳字典。
    參數說明：
    - `path`：YAML 檔路徑。
    回傳：`dict`，若讀取失敗則回傳空 dict。
    """.format(ts=datetime.datetime.utcnow().isoformat()+"Z")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

def _load_config() -> dict:
    """
    {ts}
    函式用途：聚合 adk.yaml 與 experts/*.yaml 的設定。
    參數說明：無。
    回傳：合併後的設定 dict，重點在 `experts.*.slo` 與 `agent.model`。
    """.format(ts=datetime.datetime.utcnow().isoformat()+"Z")
    root = Path(".")
    cfg = _load_yaml(root / "adk.yaml")
    exp = cfg.setdefault("experts", {})
    for name in ("diagnostic","remediation","postmortem","config"):
        y = None
        for d in (root/"experts", root/"sre_assistant/experts"):
            p = d / f"{name}.yaml"
            if p.exists():
                y = _load_yaml(p)
                break
        if y:
            exp.setdefault(name, {}).update(y)
    return cfg

def _mk_group(name: str, rules: list[dict]) -> dict:
    """
    {ts}
    函式用途：建立 Prometheus 規則群組。
    參數說明：
    - `name`：群組名稱。
    - `rules`：規則物件清單（recording 或 alerting）。
    回傳：符合 Prometheus 規格的 `group` 字典。
    """.format(ts=datetime.datetime.utcnow().isoformat()+"Z")
    return {"name": name, "interval": "30s", "rules": rules}

def _recording_and_alerts_for_expert(expert: str, slo: dict) -> list[dict]:
    """
    {ts}
    函式用途：為單一專家生成 Recording 與 Alerting 規則集合。
    參數說明：
    - `expert`：專家名稱（如 diagnostic）。
    - `slo`：包含 `p95_latency_seconds` 與 `success_rate_threshold` 的門檻設定。
    回傳：規則清單，包含 recording rules 與 alert rules。
    """.format(ts=datetime.datetime.utcnow().isoformat()+"Z")
    p95 = float(slo.get("p95_latency_seconds", 2.0))
    succ = float(slo.get("success_rate_threshold", 0.98))

    # 指標命名對齊：來自 SPEC 的建議
    # - agent_request_duration_seconds_bucket{agent=...}
    # - agent_requests_total{agent=..., status="ok|error"}
    # 以 5 分鐘窗口估算 P95 與成功率
    rec = [
        {
            "record": f"agent:{expert}:p95_latency_seconds",
            "expr": f'histogram_quantile(0.95, sum(rate(agent_request_duration_seconds_bucket{{agent="{expert}"}}[5m])) by (le))'
        },
        {
            "record": f"agent:{expert}:success_rate",
            "expr": f'sum(rate(agent_requests_total{{agent="{expert}",status="ok"}}[5m])) / sum(rate(agent_requests_total{{agent="{expert}"}}[5m]))'
        }
    ]
    alerts = [
        {
            "alert": f"{expert.capitalize()}P95LatencyHigh",
            "expr": f'agent:{expert}:p95_latency_seconds > {p95}',
            "for": "10m",
            "labels": {"severity": "warning", "component": "sre-assistant"},
            "annotations": {
                "summary": f"{expert} P95 延遲過高",
                "description": f"P95 超過 {p95}s 持續 10m。請檢查模型或外部工具延遲。"
            }
        },
        {
            "alert": f"{expert.capitalize()}SuccessRateLow",
            "expr": f'agent:{expert}:success_rate < {succ}',
            "for": "10m",
            "labels": {"severity": "warning", "component": "sre-assistant"},
            "annotations": {
                "summary": f"{expert} 成功率過低",
                "description": f"成功率低於 {succ:.2%} 持續 10m。請檢查工具錯誤與知識庫品質。"
            }
        }
    ]
    return rec + alerts

def main() -> int:
    """
    {ts}
    函式用途：主執行流程。讀取設定、生成各專家的 recording/alert 規則，並寫出 YAML。
    參數說明：無。
    回傳：程序代碼，0 代表成功。
    """.format(ts=datetime.datetime.utcnow().isoformat()+"Z")
    cfg = _load_config()
    experts = (cfg.get("experts") or {})
    groups = []
    for expert, econf in experts.items():
        if not isinstance(econf, dict): 
            continue
        slo = econf.get("slo") or {}
        rules = _recording_and_alerts_for_expert(expert, slo)
        groups.append(_mk_group(f"sre-assistant-{expert}", rules))
    out = {"groups": groups}
    out_path = Path("observability") / "slo_rules.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.safe_dump(out, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
