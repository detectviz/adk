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

import os


def load_instruction_from_file(
    filename: str, default_instruction: str = "預設指令。"
) -> str:
    """從相對於此腳本的檔案中讀取指令文字。"""
    instruction = default_instruction
    try:
        # 建構相對於目前腳本檔案 (__file__) 的路徑
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, "r", encoding="utf-8") as f:
            instruction = f.read()
        print(f"成功從 {filename} 載入指令")
    except FileNotFoundError:
        print(f"警告：找不到指令檔案：{filepath}。使用預設指令。")
    except Exception as e:
        print(f"錯誤：載入指令檔案 {filepath} 時發生錯誤：{e}。使用預設指令。")
    return instruction
