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

import json
import os

from vertexai.preview.extensions import Extension


def list_all_extensions():
  extensions = Extension.list(location='us-central1')
  for extension in extensions:
    print('名稱:', extension.gca_resource.name)
    print('顯示名稱:', extension.gca_resource.display_name)
    print('描述:', extension.gca_resource.description)


def get_env_var(var_name):
  """擷取環境變數的值。

  Args:
    var_name: 環境變數的名稱。

  Returns:
    環境變數的值，如果未設定則為 None。

  Raises:
    ValueError: 如果未設定環境變數。
  """
  try:
    value = os.environ[var_name]
    return value
  except KeyError:
    raise ValueError(f'缺少環境變數：{var_name}')


def get_image_bytes(filepath):
  """讀取圖片檔案並回傳其位元組。

  Args:
    filepath: 圖片檔案的路徑。

  Returns:
    圖片檔案的位元組，如果檔案不存在或無法讀取，則為 None。
  """
  try:
    with open(filepath, 'rb') as f:  # "rb" 模式用於二進位讀取
      image_bytes = f.read()
    return image_bytes
  except FileNotFoundError:
    print(f'錯誤：在 {filepath} 找不到檔案')
    return None
  except Exception as e:
    print(f'讀取檔案時發生錯誤：{e}')
    return None


def extract_json_from_model_output(model_output):
  """從可能包含 markdown 程式碼區塊的字串中擷取 JSON 物件。

  Args:
    model_output: 一個可能包含包在 markdown 程式碼區塊 (```json ... ```) 中的 JSON 物件的字串。

  Returns:
    一個代表擷取的 JSON 物件的 Python 字典，
    如果 JSON 擷取失敗，則為 None。
  """
  try:
    cleaned_output = (
        model_output.replace('```json', '').replace('```', '').strip()
    )
    json_object = json.loads(cleaned_output)
    return json_object
  except json.JSONDecodeError as e:
    msg = f'解碼 JSON 時發生錯誤：{e}'
    print(msg)
    return {'error': msg}


if __name__ == '__main__':
  list_all_extensions()
