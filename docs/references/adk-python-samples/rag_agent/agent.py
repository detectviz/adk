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

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag

load_dotenv()

ask_vertex_retrieval = VertexAiRagRetrieval(
    name="retrieve_rag_documentation",
    description=(
        "使用此工具從 RAG 語料庫中擷取問題的文件和參考資料，"
    ),
    rag_resources=[
        rag.RagResource(
            # 請填寫您自己的 RAG 語料庫
            # e.g. projects/123/locations/us-central1/ragCorpora/456
            rag_corpus=os.environ.get("RAG_CORPUS"),
        )
    ],
    similarity_top_k=1,
    vector_distance_threshold=0.6,
)

root_agent = Agent(
    model="gemini-2.0-flash-001",
    name="root_agent",
    instruction=(
        "您是一個可以存取專門文件語料庫的人工智慧助理。您的角色是根據可使用 ask_vertex_retrieval 擷取的文件，為問題提供準確簡潔的答案。"
    ),
    tools=[ask_vertex_retrieval],
)
