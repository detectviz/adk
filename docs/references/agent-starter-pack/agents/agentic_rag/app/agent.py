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

# mypy: disable-error-code="arg-type"
import os

import google
import vertexai
from google.adk.agents import Agent
from langchain_google_vertexai import VertexAIEmbeddings

from {{cookiecutter.agent_directory}}.retrievers import get_compressor, get_retriever
from {{cookiecutter.agent_directory}}.templates import format_docs

EMBEDDING_MODEL = "text-embedding-005"
LLM_LOCATION = "global"
LOCATION = "us-central1"
LLM = "gemini-2.5-flash"

credentials, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", LLM_LOCATION)
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

vertexai.init(project=project_id, location=LOCATION)
embedding = VertexAIEmbeddings(
    project=project_id, location=LOCATION, model_name=EMBEDDING_MODEL
)

{% if cookiecutter.datastore_type == "vertex_ai_search" %}
EMBEDDING_COLUMN = "embedding"
TOP_K = 5

data_store_region = os.getenv("DATA_STORE_REGION", "us")
data_store_id = os.getenv("DATA_STORE_ID", "{{cookiecutter.project_name}}-datastore")

retriever = get_retriever(
    project_id=project_id,
    data_store_id=data_store_id,
    data_store_region=data_store_region,
    embedding=embedding,
    embedding_column=EMBEDDING_COLUMN,
    max_documents=10,
)
{% elif cookiecutter.datastore_type == "vertex_ai_vector_search" %}
vector_search_index = os.getenv(
    "VECTOR_SEARCH_INDEX", "{{cookiecutter.project_name}}-vector-search"
)
vector_search_index_endpoint = os.getenv(
    "VECTOR_SEARCH_INDEX_ENDPOINT", "{{cookiecutter.project_name}}-vector-search-endpoint"
)
vector_search_bucket = os.getenv(
    "VECTOR_SEARCH_BUCKET", f"{project_id}-{{cookiecutter.project_name}}-vs"
)

retriever = get_retriever(
    project_id=project_id,
    region=LOCATION,
    vector_search_bucket=vector_search_bucket,
    vector_search_index=vector_search_index,
    vector_search_index_endpoint=vector_search_index_endpoint,
    embedding=embedding,
)
{% endif %}
compressor = get_compressor(
    project_id=project_id,
)


def retrieve_docs(query: str) -> str:
    """
    用於根據查詢檢索相關文件。
    當您需要額外資訊來回答問題時使用此工具。

    Args:
        query (str): 使用者的問題或搜尋查詢。

    Returns:
        str: 包含根據查詢檢索和排序的相關文件內容的格式化字串。
    """
    try:
        # 使用檢索器根據查詢擷取相關文件
        retrieved_docs = retriever.invoke(query)
        # 使用 Vertex AI Rank 重新排序文件以獲得更好的相關性
        ranked_docs = compressor.compress_documents(
            documents=retrieved_docs, query=query
        )
        # 將排序後的文件格式化為一致的結構以供大型語言模型使用
        formatted_docs = format_docs.format(docs=ranked_docs)
    except Exception as e:
        return f"使用查詢呼叫檢索工具時：\n\n{query}\n\n引發了以下錯誤：\n\n{type(e)}: {e}"

    return formatted_docs


instruction = """你是一個用於問答任務的 AI 助理。
請使用提供的上下文盡力回答。
利用提供給您的工具來回答問題。
如果您已經知道問題的答案，可以直接回應而無需使用工具。"""

root_agent = Agent(
    name="root_agent",
    model="gemini-2.0-flash",
    instruction=instruction,
    tools=[retrieve_docs],
)
