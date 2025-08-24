# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import os
from pathlib import Path
import sys

from mcp.server.fastmcp import FastMCP

# 建立一個名為 MCP 伺服器
mcp = FastMCP("Filesystem Server", host="localhost", port=3000)


# 新增一個讀取檔案內容的工具
@mcp.tool(description="讀取檔案內容")
def read_file(filepath: str) -> str:
  """讀取並傳回檔案內容。"""
  with open(filepath, "r") as f:
    return f.read()


# 新增一個列出目錄內容的工具
@mcp.tool(description="列出目錄內容")
def list_directory(dirpath: str) -> list:
  """列出指定目錄中的所有檔案和目錄。"""
  return os.listdir(dirpath)


# 新增一個取得目前工作目錄的工具
@mcp.tool(description="取得目前工作目錄")
def get_cwd() -> str:
  """傳回目前工作目錄。"""
  return str(Path.cwd())


# 優雅關機處理常式
async def shutdown(signal, loop):
  """與服務關機相關的清理工作。"""
  print(f"\n收到結束訊號 {signal.name}...")

  # 取得所有執行中的工作
  tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

  # 取消所有工作
  for task in tasks:
    task.cancel()

  print(f"正在取消 {len(tasks)} 個未完成的工作")
  await asyncio.gather(*tasks, return_exceptions=True)

  # 停止迴圈
  loop.stop()
  print("關機完成！")


# 帶有優雅關機處理的主要進入點
if __name__ == "__main__":
  try:
    # MCP 執行函式最終會在內部使用 asyncio.run()
    mcp.run(transport="sse")
  except KeyboardInterrupt:
    print("\n伺服器正在優雅關機...")
    # asyncio 事件迴圈已被 KeyboardInterrupt 停止
    print("伺服器已關機。")
  except Exception as e:
    print(f"非預期的錯誤：{e}")
    sys.exit(1)
  finally:
    print("感謝您使用檔案系統 MCP 伺服器！")
