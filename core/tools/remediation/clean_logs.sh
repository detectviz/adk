
#!/bin/bash
# 功能：清理指定目錄中的舊日誌（*.log），輸出 JSON 結果
# 參數：$1 日誌目錄（預設 /var/log）
#      $2 天數（預設 30）
#      $3 是否為模擬模式 dry_run=true|false（預設 false）
set -euo pipefail

log_dir="${1:-/var/log}"
days="${2:-30}"
dry_run="${3:-false}"

mapfile -t files < <(find "$log_dir" -type f -name "*.log" -mtime +$days 2>/dev/null || true)
count="${#files[@]}"

if [ "$dry_run" = "true" ]; then
  printf '{"status":"dry_run","message":"Would delete %s files","data":{"files":%s}}\n' "$count" "$count"
  exit 0
fi

if [ "$count" -gt 0 ]; then
  # 逐一刪除避免引號問題
  for f in "${files[@]}"; do
    rm -f -- "$f"
  done
  printf '{"status":"ok","message":"Cleaned %s log files","data":{"files":%s}}\n' "$count" "$count"
else
  printf '{"status":"ok","message":"No old logs to clean","data":{"files":0}}\n'
fi
