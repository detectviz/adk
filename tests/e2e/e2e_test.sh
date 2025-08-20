#!/bin/bash

echo "=== E2E 測試開始 ==="

# 1. 啟動 Go Core
echo "啟動 Go Core..."
./bin/core-server &
CORE_PID=$!
sleep 2

# 2. 啟動 Python Agent
echo "啟動 Python Agent..."
python -m agents.sre_assistant &
AGENT_PID=$!
sleep 2

# 3. 執行測試對話
echo "執行測試對話..."
curl -X POST http://localhost:8080/chat 
  -H "Content-Type: application/json" 
  -d '{"message": "檢查系統健康狀態"}'

# 4. 驗證工具調用
echo "驗證工具調用..."
# 檢查日誌中是否有工具執行記錄
grep "Executing tool: check_disk" logs/core.log
grep "Executing tool: check_memory" logs/core.log

# 5. 清理
kill $CORE_PID $AGENT_PID

echo "=== E2E 測試完成 ==="