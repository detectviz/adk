
#!/bin/bash
# 功能：清理指定目錄中的舊日誌（*.log），輸出 JSON 結果
# 參數：$1 日誌目錄（預設 /var/log）
#      $2 天數（預設 30）
#      $3 是否為模擬模式 dry_run=true|false（預設 false）
set -euo pipefail

log_dir="${1:-/var/log}"
days="${2:-30}"
dry_run="${3:-false}"
trash_dir="/tmp/cleared_logs_$(date +%Y%m%d%H%M%S)"

mapfile -t files < <(find "$log_dir" -type f -name "*.log" -mtime +$days 2>/dev/null || true)
count="${#files[@]}"

if [ "$dry_run" = "true" ]; then
  printf '{"status":"dry_run","message":"Would move %s files to a trash directory","data":{"file_count":%s}}\n' "$count" "$count"
  exit 0
fi

if [ "$count" -gt 0 ]; then
  mkdir -p "$trash_dir"
  # 逐一移動以記錄
  moved_files=()
  for f in "${files[@]}"; do
    if mv -- "$f" "$trash_dir/"; then
      moved_files+=( "\"$(basename "$f")\"" )
    fi
  done
  moved_count="${#moved_files[@]}"
  moved_list=$(IFS=,; echo "${moved_files[*]}")

  printf '{"status":"ok","message":"Moved %s log files to %s","data":{"moved_count":%s,"trash_dir":"%s","moved_files":[%s]}}\n' "$moved_count" "$trash_dir" "$moved_count" "$trash_dir" "$moved_list"
else
  printf '{"status":"ok","message":"No old logs to clean","data":{"file_count":0}}\n'
fi
