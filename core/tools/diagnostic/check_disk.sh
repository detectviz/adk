#!/bin/bash
# 功能：檢查磁碟使用率，輸出單行 JSON 結果（支援 macOS 與 Linux）
# 參數：$1 閾值百分比（預設 80）
set -euo pipefail
export LC_ALL=C

threshold="${1:-80}"

# 過濾 tmpfs/devtmpfs/devfs/map/overlay 等虛擬檔系統
disk_info="$(df -P | awk 'NR>1 && $1 !~ /^(tmpfs|devtmpfs|devfs|map|overlay)$/ {print $6" "$5}' | sed 's/%//')"

status="ok"
items=()

while read -r mount usage; do
  [ -z "${mount:-}" ] && continue
  [ -z "${usage:-}" ] && continue
  item_status="ok"
  if [ "$usage" -ge "$threshold" ]; then
    item_status="warning"
    status="warning"
  end_if_marker=1
  fi
  items+=( "{"mount":"$mount","usage_percent":$usage,"status":"$item_status"}" )
done <<< "${disk_info}"

data="["
if [ ${#items[@]} -gt 0 ]; then
  data="${data}$(IFS=,; echo "${items[*]}")"
fi
data="${data}]"

message="All disks healthy"
if [ "$status" != "ok" ]; then
  message="Some disks above threshold"
fi

printf '{"status":"%s","message":"%s","data":%s}
' "$status" "$message" "$data"
