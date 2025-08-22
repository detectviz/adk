
# 命令列工具：對話、審批、回放查詢、API Key 管理。
import argparse, asyncio, json, secrets
from .core.assistant import SREAssistant
from ..adk_runtime.main import build_registry
from .core.hitl import APPROVALS
from .core.persistence import DB

def main():
    
    parser = argparse.ArgumentParser(description="SRE Assistant CLI")
    sub = parser.add_subparsers(dest="cmd")
    p_chat = sub.add_parser("chat"); p_chat.add_argument("message", type=str)
    p_ap = sub.add_parser("approve"); p_ap.add_argument("approval_id", type=int)
    sub.add_parser("decisions"); sub.add_parser("execs")
    p_key = sub.add_parser("apikey"); sp = p_key.add_subparsers(dest="op")
    p_add = sp.add_parser("add"); p_add.add_argument("--role", default="viewer"); p_add.add_argument("--key", default=None)
    sp.add_parser("list")

    args = parser.parse_args()
    if args.cmd == "chat":
        a = SREAssistant(build_registry())
        res = asyncio.run(a.chat(args.message))
        print(json.dumps(res, ensure_ascii=False, indent=2))
        pend = [s for s in res["actions_taken"] if s.get("error_code")=="E_REQUIRE_APPROVAL"]
        if pend:
            print("需要審批ID：", [p["data"]["approval_id"] for p in pend])
    elif args.cmd == "approve":
        a = SREAssistant(build_registry())
        APPROVALS.decide(args.approval_id, status="approved", decided_by="cli", reason="ok")
        res = asyncio.run(a.execute_approval(args.approval_id))
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif args.cmd == "decisions":
        print(json.dumps(DB.list_decisions(limit=50), ensure_ascii=False, indent=2))
    elif args.cmd == "execs":
        print(json.dumps(DB.list_tool_execs(limit=50), ensure_ascii=False, indent=2))
    elif args.cmd == "apikey":
        if args.op == "add":
            key = args.key or secrets.token_urlsafe(24)
            rec = DB.add_api_key(key, args.role)
            print(json.dumps({"key": key, "role": rec["role"]}, ensure_ascii=False, indent=2))
        elif args.op == "list":
            # 簡單直接查 DB 表（為了簡化示例）
            import sqlite3
            conn = sqlite3.connect(DB.path); cur=conn.cursor()
            cur.execute("SELECT id, role, created_at FROM api_keys ORDER BY id DESC")
            rows = [{"id":r[0],"role":r[1],"created_at":r[2]} for r in cur.fetchall()]
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            print("用法：apikey add|list")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()