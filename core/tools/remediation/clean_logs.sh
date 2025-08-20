#!/bin/bash
# 功能：清理日誌文件

set -e

clean_logs() {
    local log_dir=${1:-/var/log}
    local days=${2:-30}
    local dry_run=${3:-false}
    
    # 查找舊日誌
    old_logs=$(find "$log_dir" -name "*.log" -type f -mtime +$days)
    count=$(echo "$old_logs" | wc -l)
    
    if [ "$dry_run" = "true" ]; then
        # 模擬模式
        echo "{"status":"dry_run","message":"Would delete $count files","data":{"files":$count}}"
    else
        # 實際清理
        if [ -n "$old_logs" ]; then
            echo "$old_logs" | xargs rm -f
            echo "{"status":"ok","message":"Cleaned $count log files","data":{"files":$count}}"
        else
            echo "{"status":"ok","message":"No old logs to clean","data":{"files":0}}"
        fi
    fi
}

clean_logs "$@"