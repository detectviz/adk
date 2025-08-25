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

"""FOMC 研究代理中 extract_page_data_agent 的提示詞定義"""

PROMPT = """
您的工作是從網頁中擷取重要資料。

 <PAGE_CONTENTS>
 {page_contents}
 </PAGE_CONTENTS>

<INSTRUCTIONS>
網頁內容如上方的 'page_contents' 區段所示。
所需的資料欄位在使用者輸入的 'data_to_extract' 區段中提供。

請閱讀網頁內容並擷取所要求的資料。
不要使用任何其他的 HTML 解析器，只需自行檢查 HTML 並擷取資訊。

首先，使用 store_state 工具將擷取的資料儲存在 ToolContext 中。

其次，以 JSON 格式將您找到的資訊回傳給使用者。
 </INSTRUCTIONS>

"""
