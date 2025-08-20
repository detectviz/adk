
#!/bin/bash
# 功能：檢查記憶體使用率，輸出 JSON 結果
# 參數：$1 閾值百分比（預設 80）
set -euo pipefail

threshold="${1:-80}"

mem_total=$(free -m | awk '/Mem:/ {print $2}')
mem_used=$(free -m | awk '/Mem:/ {print $3}')
mem_available=$(free -m | awk '/Mem:/ {print $7}')

usage_percent=$((mem_used * 100 / mem_total))

status="ok"
message="Memory healthy"
if [ "$usage_percent" -gt "$threshold" ]; then
  status="warning"
  message="Memory usage high"
fi

printf '{"status":"%s","message":"%s","data":{"total_mb":%s,"used_mb":%s,"available_mb":%s,"usage_percent":%s}}\n'       "$status" "$message" "$mem_total" "$mem_used" "$mem_available" "$usage_percent"
