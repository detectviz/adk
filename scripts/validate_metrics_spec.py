
# -*- coding: utf-8 -*-
import yaml, re
from pathlib import Path
ALLOWED = {"agent_request_duration_seconds_bucket","agent_requests_total"}
def main()->int:
    p=Path("observability/slo_rules.yaml")
    if not p.exists(): print("missing slo_rules"); return 1
    data=yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    bad=set()
    for g in data.get("groups",[]):
        for r in g.get("rules",[]):
            expr=r.get("expr","")
            for n in set(re.findall(r"[a-zA-Z_:][a-zA-Z0-9_:]*", expr)):
                if n.startswith("agent:") or n in {"sum","rate","by","histogram_quantile"}: continue
                if n not in ALLOWED and ":" not in n: bad.add(n)
    if bad: print("Invalid metrics:",sorted(bad)); return 2
    print("OK"); return 0
if __name__=="__main__": import sys; sys.exit(main())
