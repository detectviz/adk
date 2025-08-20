#!/bin/bash
# 功能：更新配置文件

set -e

update_config() {
    local config_file=$1
    local key=$2
    local value=$3
    
    # 驗證參數
    if [ -z "$config_file" ] || [ -z "$key" ] || [ -z "$value" ]; then
        echo "{"status":"error","message":"Missing parameters"}"
        exit 1
    fi
    
    # 備份原配置
    cp "$config_file" "${config_file}.bak.$(date +%Y%m%d%H%M%S)"
    
    # 更新配置
    if grep -q "^$key=" "$config_file"; then
        sed -i "s/^$key=.*/$key=$value/" "$config_file"
        echo "{"status":"ok","message":"Config updated","data":{"file":"$config_file","key":"$key","value":"$value"}}"
    else
        echo "$key=$value" >> "$config_file"
        echo "{"status":"ok","message":"Config added","data":{"file":"$config_file","key":"$key","value":"$value"}}"
    fi
}

update_config "$@"