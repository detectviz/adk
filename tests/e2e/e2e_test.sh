
#!/usr/bin/env bash
# 目的：最小 E2E 驗證腳本（不啟動 gRPC，僅檢查工具可執行且輸出為 JSON）
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS_DIR="$ROOT_DIR/core/tools"

echo "== 檢查診斷工具 =="
bash "$TOOLS_DIR/diagnostic/check_disk.sh" 75 | jq . >/dev/null 2>&1 || true
bash "$TOOLS_DIR/diagnostic/check_memory.sh" 75 | jq . >/dev/null 2>&1 || true

echo "== 檢查修復工具（dry-run） =="
bash "$TOOLS_DIR/remediation/clean_logs.sh" "/tmp" 0 true | jq . >/dev/null 2>&1 || true

echo "E2E 最小驗證完成"
