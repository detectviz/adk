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

import google.auth
import vertexai
from google import genai
from google.genai import types

# 常數
VERTEXAI = os.getenv("VERTEXAI", "true").lower() == "true"
LOCATION = "us-central1"
MODEL_ID = "gemini-live-2.5-flash-preview-native-audio"

# 初始化 Google Cloud 用戶端
credentials, project_id = google.auth.default()
vertexai.init(project=project_id, location=LOCATION)


if VERTEXAI:
    genai_client = genai.Client(project=project_id, location=LOCATION, vertexai=True)
else:
    # API 金鑰應使用 GOOGLE_API_KEY 環境變數設定
    genai_client = genai.Client(http_options={"api_version": "v1alpha"})


def get_weather(query: str) -> dict:
    """模擬網路搜尋。用它來獲取天氣資訊。

    Args:
        query: 一個包含要查詢天氣資訊地點的字串。

    Returns:
        一個包含所查詢地點模擬天氣資訊的字串。
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return {"output": "現在是華氏 60 度，有霧。"}
    return {"output": "現在是華氏 90 度，晴天。"}


# 設定代理可用的工具和即時連線
tool_functions = {"get_weather": get_weather}

live_connect_config = types.LiveConnectConfig(
    response_modalities=[types.Modality.AUDIO],
    tools=list(tool_functions.values()),
    system_instruction=types.Content(
        parts=[
            types.Part(
                text="""你是一個樂於助人的 AI 助理，旨在提供準確且有用的資訊。你能夠適應不同的語言和語氣。"""
            )
        ]
    ),
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Kore")
        )
    ),
    enable_affective_dialog=True,
)
