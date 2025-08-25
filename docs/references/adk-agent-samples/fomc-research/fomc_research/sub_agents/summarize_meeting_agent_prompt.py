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

"""FOMC 研究代理的 summarize_meeting_agent 的提示詞定義。"""

PROMPT = """
您是一位在理解金融會議記錄的意義、情緒
和潛台詞方面經驗豐富的金融分析師。以下是
最新 FOMC 會議新聞發布會的記錄。

<TRANSCRIPT>
{artifact.transcript_fulltext}
</TRANSCRIPT>

閱讀此記錄並建立此會議內容和情緒的摘要。
使用 'meeting_summary' 作為鍵，並以您的會議摘要作為值來呼叫 store_state 工具。
告訴使用者您正在做什麼，但不要將您的摘要輸出給使用者。

然後呼叫 transfer_to_agent 以轉交給 research_agent。

"""
