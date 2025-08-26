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
# ruff: noqa
# mypy: disable-error-code="no-untyped-def"

import os

from unittest.mock import MagicMock
from langchain_google_community.vertex_rank import VertexAIRank
from langchain_google_vertexai import VertexAIEmbeddings
{% if cookiecutter.datastore_type == "vertex_ai_search" -%}
from langchain_google_community import VertexAISearchRetriever


def get_retriever(
    project_id: str,
    data_store_id: str,
    data_store_region: str,
    embedding: VertexAIEmbeddings,
    embedding_column: str = "embedding",
    max_documents: int = 10,
    custom_embedding_ratio: float = 0.5,
) -> VertexAISearchRetriever:
    """
    建立並傳回檢索器服務的實例。

    如果 INTEGRATION_TEST 環境變數設定為 "TRUE"，則使用模擬服務，
    否則初始化真實的 Vertex AI 檢索器。
    """
    try:
        return VertexAISearchRetriever(
            project_id=project_id,
            data_store_id=data_store_id,
            location_id=data_store_region,
            engine_data_type=1,
            # 當您想在 Agent Builder 中使用自訂嵌入進行搜尋時，
            # 會使用以下參數。
            # 預設比例設定為 0.5，以混合使用自訂嵌入，
            # 但您可以根據需要調整比例。
            custom_embedding_ratio=custom_embedding_ratio,
            custom_embedding=embedding,
            custom_embedding_field_path=embedding_column,
            # 在重新排序前擷取 20 個文件。
            max_documents=max_documents,
            beta=True,
        )
    except Exception:
        retriever = MagicMock()

        def raise_exception(*args, **kwargs) -> None:
            """當檢索器不可用時引發異常的函式。"""
            raise Exception("檢索器不可用")

        retriever.invoke = raise_exception
        return retriever
{% elif cookiecutter.datastore_type == "vertex_ai_vector_search" -%}
from google.cloud import aiplatform
from langchain_google_vertexai import VectorSearchVectorStore
from langchain_core.vectorstores import VectorStoreRetriever


def get_retriever(
    project_id: str,
    region: str,
    vector_search_bucket: str,
    vector_search_index: str,
    vector_search_index_endpoint: str,
    embedding: VertexAIEmbeddings,
) -> VectorStoreRetriever:
    """
    建立並傳回檢索器服務的實例。
    """
    try:
        aiplatform.init(
            project=project_id,
            location=region,
            staging_bucket=vector_search_bucket,
        )

        my_index = aiplatform.MatchingEngineIndex(vector_search_index)

        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            vector_search_index_endpoint
        )

        return VectorSearchVectorStore.from_components(
            project_id=project_id,
            region=region,
            gcs_bucket_name=vector_search_bucket.replace("gs://", ""),
            index_id=my_index.name,
            endpoint_id=my_index_endpoint.name,
            embedding=embedding,
            stream_update=True,
        ).as_retriever()
    except Exception:
        retriever = MagicMock()

        def raise_exception(*args, **kwargs) -> None:
            """當檢索器不可用時引發異常的函式。"""
            raise Exception("檢索器不可用")

        retriever.invoke = raise_exception
        return retriever
{% endif %}

def get_compressor(project_id: str, top_n: int = 5) -> VertexAIRank:
    """
    建立並傳回壓縮器服務的實例。
    """
    try:
        return VertexAIRank(
            project_id=project_id,
            location_id="global",
            ranking_config="default_ranking_config",
            title_field="id",
            top_n=top_n,
        )
    except Exception:
        compressor = MagicMock()
        compressor.compress_documents = lambda x: []
        return compressor
