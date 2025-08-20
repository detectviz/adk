
#!/bin/bash
# 功能：檢查磁碟使用率，輸出 JSON 結果
# 參數：$1 閾值百分比（預設 80）
set -euo pipefail

threshold="${1:-80}"

# 取得檔案系統使用率（過濾 tmpfs 與 devtmpfs）
disk_info=$(df -P -x tmpfs -x devtmpfs | awk 'NR>1 {print $6" "$5}' | sed 's/%//')

status="ok"
issues=0
items=()

while read -r mount usage; do
  if [ -z "$mount" ]; then
    continue
  fi
  item_status="ok"
  if [ "$usage" -ge "$threshold" ]; then
    item_status="warning"
    status="warning"
    issues=$((issues+1))
  fi
  items+=( "{"mount":"$mount","usage_percent":$usage,"status":"$item_status"}" )
done <<< "$disk_info"

data="["
if [ ${#items[@]} -gt 0 ]; then
  data="${data}$(IFS=,; echo "${items[*]}")"
fi
data="${data}]"

message="All disks healthy"
if [ "$status" != "ok" ]; then
  message="Some disks above threshold"
fi

# 輸出單行 JSON（保持與 ToolBridge 約定一致）
printf '{"status":"%s","message":"%s","data":%s}\n' "$status" "$message" "$data"
