#!/bin/bash
# 功能：檢查磁碟使用率，輸出單行 JSON 結果（支援 macOS 與 Linux）
# 參數：$1 閾值百分比（預設 80）
set -euo pipefail
export LC_ALL=C

threshold="${1:-80}"

get_disk_info_linux() {
    df -P | awk 'NR>1 && $1 !~ /^(tmpfs|devtmpfs|overlay)$/ {print $6" "$5}' | sed 's/%//'
}

get_disk_info_macos() {
    # macOS `df -P` has usage at col 5 and mount at col 9
    df -P | awk 'NR>1 && $1 !~ /^(devfs|map)/ {print $9" "$5}' | sed 's/%//'
}

disk_info=""
case "$(uname -s)" in
    Linux*)
        disk_info=$(get_disk_info_linux)
        ;;
    Darwin*)
        disk_info=$(get_disk_info_macos)
        ;;
    *)
        printf '{"status":"error","message":"Unsupported OS: %s"}' "$(uname -s)"
        exit 1
        ;;
esac

status="ok"
items=()

while read -r mount usage; do
  [ -z "${mount:-}" ] && continue
  [ -z "${usage:-}" ] && continue
  item_status="ok"
  if [ "$usage" -ge "$threshold" ]; then
    item_status="warning"
    status="warning"
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
