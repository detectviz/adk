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
from pathlib import Path
from dotenv import load_dotenv, set_key
import vertexai
from vertexai import rag


# 定義 .env 檔案的路徑
env_file_path = Path(__file__).parent.parent.parent / ".env"
print(env_file_path)

# 從指定的 .env 檔案載入環境變數
load_dotenv(dotenv_path=env_file_path)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

display_name = "bqml_referenceguide_corpus"

paths = [
    "gs://cloud-samples-data/adk-samples/data-science/bqml"
]  # 支援 Google Cloud Storage 和 Google Drive 連結


# 每個會話僅初始化一次 Vertex AI API
vertexai.init(project=PROJECT_ID, location="us-central1")


def create_RAG_corpus():
    # 建立 RagCorpus
    # 設定嵌入模型，例如 "text-embedding-005"。
    embedding_model_config = rag.RagEmbeddingModelConfig(
        vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
            publisher_model="publishers/google/models/text-embedding-005"
        )
    )

    backend_config = rag.RagVectorDbConfig(
        rag_embedding_model_config=embedding_model_config
    )

    bqml_corpus = rag.create_corpus(
        display_name=display_name,
        backend_config=backend_config,
    )

    write_to_env(bqml_corpus.name)

    return bqml_corpus.name


def ingest_files(corpus_name):

    transformation_config = rag.TransformationConfig(
        chunking_config=rag.ChunkingConfig(
            chunk_size=512,
            chunk_overlap=100,
        ),
    )

    rag.import_files(
        corpus_name,
        paths,
        transformation_config=transformation_config,  # 可選
        max_embedding_requests_per_min=1000,  # 可選
    )

    # 列出 rag 語料庫中的檔案
    rag.list_files(corpus_name)


def rag_response(query: str) -> str:
    """從 RAG 語料庫中擷取與上下文相關的資訊。

    Args:
        query (str): 要在語料庫中搜尋的查詢字串。

    Returns:
        vertexai.rag.RagRetrievalQueryResponse: 包含從語料庫中擷取資訊的回應。
    """
    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    rag_retrieval_config = rag.RagRetrievalConfig(
        top_k=3,  # 可選
        filter=rag.Filter(vector_distance_threshold=0.5),  # 可選
    )
    response = rag.retrieval_query(
        rag_resources=[
            rag.RagResource(
                rag_corpus=corpus_name,
            )
        ],
        text=query,
        rag_retrieval_config=rag_retrieval_config,
    )
    return str(response)


def write_to_env(corpus_name):
    """將語料庫名稱寫入指定的 .env 檔案。

    Args:
        corpus_name: 要寫入的語料庫名稱。
    """

    load_dotenv(env_file_path)  # 載入任何現有的變數

    # 在 .env 檔案中設定鍵值對
    set_key(env_file_path, "BQML_RAG_CORPUS_NAME", corpus_name)
    print(f"已將 BQML_RAG_CORPUS_NAME '{corpus_name}' 寫入 {env_file_path}")


if __name__ == "__main__":
    # rag_corpus = rag.list_corpora()

    corpus_name = os.getenv("BQML_RAG_CORPUS_NAME")

    print("正在建立語料庫。")
    corpus_name = create_RAG_corpus()
    print(f"語料庫名稱：{corpus_name}")

    print(f"正在將檔案匯入語料庫：{corpus_name}")
    ingest_files(corpus_name)
    print(f"已將檔案匯入語料庫：{corpus_name}")
