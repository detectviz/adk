#!/bin/bash

# 啟動 ADK 多模態伺服器
echo "正在 8080 連接埠上啟動串流服務..."
cd "$(dirname "$0")"
python3 streaming_service.py &
ADK_PID=$!

# 稍待片刻以確保伺服器正常啟動
sleep 2

echo "串流服務現已啟用，PID 為： $ADK_PID"
echo ""
echo "若要停止伺服器，請按 Ctrl+C。"

# 攔截 Ctrl+C 以正常關閉伺服器
trap "echo '正在關閉串流服務...'; kill $ADK_PID; exit 0" INT

# 等待使用者按下 Ctrl+C
wait