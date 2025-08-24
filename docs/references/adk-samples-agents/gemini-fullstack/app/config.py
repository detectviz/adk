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
from dataclasses import dataclass

import google.auth

# 若要使用 AI Studio 憑證：
# 1. 在 /app 目錄中建立一個 .env 檔案，內容如下：
#    GOOGLE_GENAI_USE_VERTEXAI=FALSE
#    GOOGLE_API_KEY=在此貼上您實際的API金鑰
# 2. 這將會覆寫預設的 Vertex AI 設定
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


@dataclass
class ResearchConfiguration:
    """研究相關模型和參數的設定。

    屬性：
        critic_model (str): 用於評估任務的模型。
        worker_model (str): 用於工作/生成任務的模型。
        max_search_iterations (int): 允許的最大搜尋迭代次數。
    """

    critic_model: str = "gemini-1.5-pro-latest"
    worker_model: str = "gemini-1.5-flash-latest"
    max_search_iterations: int = 5


config = ResearchConfiguration()
