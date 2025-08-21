
# -*- coding: utf-8 -*-
# 命令列工具：對話、審批與回放查詢
import argparse, asyncio, json
from .core.assistant import SREAssistant
from ..adk_runtime.main import build_registry
from .core.hitl import APPROVALS
from .core.persistence import DB

def main():
    parser = argparse.ArgumentParser(description="SRE Assistant CLI")
    sub = parser.add_subparsers(dest="cmd")
    p_chat = sub.add_parser("chat"); p_chat.add_argument("message", type=str)
    p_ap = sub.add_parser("approve"); p_ap.add_argument("approval_id", type=int)
    sub.add_parser("decisions")
    sub.add_parser("execs")
    args = parser.parse_args()
    a = SREAssistant(build_registry())
    if args.cmd == "chat":
        res = asyncio.run(a.chat(args.message))
        print(json.dumps(res, ensure_ascii=False, indent=2))
        pend = [s for s in res["actions_taken"] if s.get("error_code")=="E_REQUIRE_APPROVAL"]
        if pend:
            print("需要審批ID：", [p["data"]["approval_id"] for p in pend])
    elif args.cmd == "approve":
        APPROVALS.decide(args.approval_id, status="approved", decided_by="cli", reason="ok")
        res = asyncio.run(a.execute_approval(args.approval_id))
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.cmd == "decisions":
        print(json.dumps(DB.list_decisions(limit=20), ensure_ascii=False, indent=2))
    elif args.cmd == "execs":
        print(json.dumps(DB.list_tool_execs(limit=20), ensure_ascii=False, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
