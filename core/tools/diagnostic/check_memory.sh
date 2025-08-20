#!/bin/bash
# 功能：檢查記憶體使用率

set -e

check_memory_usage() {
    local threshold=${1:-80}
    
    # 獲取記憶體資訊
    mem_total=$(free -b | grep Mem | awk '{print $2}')
    mem_used=$(free -b | grep Mem | awk '{print $3}')
    mem_available=$(free -b | grep Mem | awk '{print $7}')
    
    # 計算使用率
    usage_percent=$((mem_used * 100 / mem_total))
    
    # 構建 JSON 結果
    data="{
        "total_bytes": $mem_total,
        "used_bytes": $mem_used,
        "available_bytes": $mem_available,
        "usage_percent": $usage_percent
    }"
    
    # 判斷狀態
    if [ "$usage_percent" -gt "$threshold" ]; then
        echo "{"status":"warning","message":"Memory usage high","data":$data}"
    else
        echo "{"status":"ok","message":"Memory healthy","data":$data}"
    fi
}

check_memory_usage "$@"