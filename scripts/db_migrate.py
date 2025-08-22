
# 檔案：scripts/db_migrate.py
# 用途：初始化資料表（pgvector / hitl_audits）。以簡易連線字串區分 PG/SQLite。
import os, sys, pathlib

def _read_sql(rel: str) -> str:
    p = pathlib.Path("sre_assistant")/rel
    return p.read_text(encoding="utf-8")

def _pg_conn():
    import psycopg
    dsn = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
    return psycopg.connect(dsn)

def _sqlite_conn():
    import sqlite3
    path = os.getenv("SQLITE_PATH", "sre-assistant.db")
    return sqlite3.connect(path)

def main()->int:
    """
    {ts}
    函式用途：依環境變數選擇資料庫並執行初始化 SQL。
    參數說明：無。
    回傳：0 成功；非零失敗。
    """.format(ts=__import__('datetime').datetime.utcnow().isoformat()+"Z")
    backend = os.getenv("DB_BACKEND","sqlite").lower()
    try:
        if backend == "postgres":
            conn = _pg_conn()
            with conn.cursor() as cur:
                cur.execute(_read_sql("rag/sql/init_pgvector.sql"))
                cur.execute(_read_sql("core/sql/hitl_audit.sql"))
            conn.commit(); conn.close()
        else:
            conn = _sqlite_conn()
            cur = conn.cursor()
            # SQLite 版：不支援 pgvector，建立相容表（embedding 存為 JSON/text）
            cur.execute("CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY, source_id TEXT, version INT, content TEXT, embedding TEXT, created_at TEXT)" )
            cur.execute(_read_sql("core/sql/hitl_audit.sql").replace("BIGSERIAL","INTEGER").replace("TIMESTAMPTZ","TEXT"))
            conn.commit(); conn.close()
        print("DB migration OK")
        return 0
    except Exception as e:
        print("DB migration failed:", e)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
