#!/bin/bash
# 功能：檢查記憶體使用率，輸出單行 JSON 結果（支援 Linux 與 macOS）
# 參數：$1 閾值百分比（預設 80）
set -euo pipefail
export LC_ALL=C

threshold="${1:-80}"

to_json() {
  # 參數：status message total_mb used_mb available_mb usage_percent
  printf '{"status":"%s","message":"%s","data":{"total_mb":%s,"used_mb":%s,"available_mb":%s,"usage_percent":%s}}\n' \
    "$1" "$2" "$3" "$4" "$5" "$6"
}

linux_free() {
  # Linux 常見發行版有 free
  mem_total=$(free -m | awk '/Mem:/ {print $2}')
  mem_used=$(free -m | awk '/Mem:/ {print $3}')
  mem_avail=$(free -m | awk '/Mem:/ {print $7}')
}

linux_proc() {
  # BusyBox 或精簡容器沒有 free，改讀 /proc/meminfo
  mem_total=$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)
  mem_avail=$(awk '/MemAvailable/ {print int($2/1024)}' /proc/meminfo)
  mem_used=$((mem_total - mem_avail))
}

mac_vmstat() {
  # macOS 沒有 free，透過 vm_stat 與 sysctl 計算
  # 可用記憶體近似：free + inactive + speculative
  page_size=$(vm_stat | awk '/page size of/ {print $8}')
  [ -z "${page_size:-}" ] && page_size=4096
  free=$(vm_stat | awk '/Pages free/ {print $3}' | tr -d '.')
  spec=$(vm_stat | awk '/Pages speculative/ {print $3}' | tr -d '.')
  inactive=$(vm_stat | awk '/Pages inactive/ {print $3}' | tr -d '.')
  avail_pages=$((free + spec + inactive))
  avail_bytes=$((avail_pages * page_size))
  total_bytes=$(sysctl -n hw.memsize)
  used_bytes=$((total_bytes - avail_bytes))
  mem_total=$((total_bytes / 1024 / 1024))
  mem_avail=$((avail_bytes / 1024 / 1024))
  mem_used=$((used_bytes / 1024 / 1024))
}

# 偵測環境
if command -v free >/dev/null 2>&1; then
  linux_free
elif [ -r /proc/meminfo ]; then
  linux_proc
elif [ "$(uname -s)" = "Darwin" ]; then
  mac_vmstat
else
  printf '{"status":"error","message":"unsupported os","data":{}}\n'
  exit 1
fi

usage_percent=$((mem_used * 100 / mem_total))
status="ok"; message="Memory healthy"
if [ "$usage_percent" -gt "$threshold" ]; then
  status="warning"; message="Memory usage high"
fi

to_json "$status" "$message" "$mem_total" "$mem_used" "$mem_avail" "$usage_percent"
