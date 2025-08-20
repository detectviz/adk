#!/bin/bash
# 功能：檢查磁碟使用率

set -e

# 標準化輸出格式（JSON）
output_json() {
    local status=$1
    local message=$2
    local data=$3
    echo "{"status":"$status","message":"$message","data":$data}"
}

# 主邏輯
check_disk_usage() {
    local threshold=${1:-80}  # 預設閾值 80%
    
    # 獲取磁碟使用資訊
    disk_info=$(df -h | grep -E '^/dev/' | awk '{print $5" "$6}')
    
    # 構建 JSON 數據
    data="["
    first=true
    while IFS= read -r line; do
        usage=$(echo $line | awk '{print $1}' | sed 's/%//')
        mount=$(echo $line | awk '{print $2}')
        
        if [ "$first" = true ]; then
            first=false
        else
            data="$data,"
        fi
        
        status="ok"
        if [ "$usage" -gt "$threshold" ]; then
            status="warning"
        fi
        
        data="$data{"mount":"$mount","usage":$usage,"status":"$status"}"
    done <<< "$disk_info"
    data="$data]"
    
    # 判斷整體狀態
    if echo "$disk_info" | awk '{print $1}' | sed 's/%//' | 
       awk -v t="$threshold" '{if($1>t) exit 1}'; then
        output_json "ok" "All disks healthy" "$data"
    else
        output_json "warning" "Some disks above threshold" "$data"
    fi
}

# 執行
check_disk_usage "$@"