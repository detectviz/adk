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

# mypy: ignore-errors
from {{cookiecutter.agent_directory}}.agent import agent


def test_agent_stream() -> None:
    """
    代理串流功能的整合測試。
    測試代理是否返回有效的串流回應。
    """
    input_dict = {
        "messages": [
            {"type": "human", "content": "Hi"},
            {"type": "ai", "content": "Hi there!"},
            {"type": "human", "content": "Write a fibonacci function in python"},
        ]
    }

    events = [
        message for message, _ in agent.stream(input_dict, stream_mode="messages")
    ]
    # 驗證我們是否收到合理數量的訊息
    assert len(events) > 0, "Expected at least one message"

    # 第一則訊息應該是 AI 訊息
    assert events[0].type == "AIMessageChunk"

    # 至少有一則訊息應該有內容
    has_content = False
    for event in events:
        if hasattr(event, "content") and event.content:
            has_content = True
            break
    assert has_content, "Expected at least one message with content"
