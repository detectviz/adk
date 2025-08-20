
#!/bin/bash
# 功能：檢查磁碟使用率，輸出單行 JSON 結果（支援 macOS 與 Linux）
# 參數：$1 閾值百分比（預設 80）
# 注意：
# - 避免使用 Linux 的 `df -x`（macOS 不支援），改以 awk 過濾檔案系統類型（tmpfs/devtmpfs/devfs/map/overlay）
# - 修正 JSON 引號，確保 items 陣列可正確輸出

set -euo pipefail
export LC_ALL=C

threshold="${1:-80}"

# 取得檔案系統使用率（過濾 tmpfs/devtmpfs/devfs/map/overlay）
# df -P 可輸出 POSIX 風格欄位：
#   $1 Filesystem, $5 Use%, $6 Mounted on
disk_info="$(df -P | awk 'NR>1 && $1 !~ /^(tmpfs|devtmpfs|devfs|map|overlay)$/ {print $6" "$5}' | sed "s/%//")"

status="ok"
issues=0
items=()

# 逐行解析：<mount> <usage_percent>
while read -r mount usage; do
  # 忽略空行或解析失敗的輸入
  if [ -z "${mount:-}" ] || [ -z "${usage:-}" ]; then
    continue
  fi
  item_status="ok"
  if [ "$usage" -ge "$threshold" ]; then
    item_status="warning"
    status="warning"
    issues=$((issues+1))
  fi
  # 正確引用 JSON 字串
  items+=( "{\"mount\":\"$mount\",\"usage_percent\":$usage,\"status\":\"$item_status\"}" )
done <<< "${disk_info}"

# 組裝 JSON 陣列
data="["
if [ ${#items[@]} -gt 0 ]; then
  data="${data}$(IFS=,; echo "${items[*]}")"
fi
data="${data}]"

message="All disks healthy"
if [ "$status" != "ok" ]; then
  message="Some disks above threshold"
fi

# 輸出單行 JSON（與 ToolBridge 約定一致）
printf '{"status":"%s","message":"%s","data":%s}\n' "$status" "$message" "$data"
