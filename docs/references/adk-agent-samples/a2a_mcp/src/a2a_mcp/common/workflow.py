import json
import logging
import uuid

from collections.abc import AsyncIterable
from enum import Enum
from uuid import uuid4

import httpx
import networkx as nx

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendStreamingMessageRequest,
    SendStreamingMessageSuccessResponse,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)
from a2a_mcp.common.utils import get_mcp_server_config
from a2a_mcp.mcp import client


logger = logging.getLogger(__name__)


class Status(Enum):
    """表示工作流程及其關聯節點的狀態。"""

    READY = 'READY'
    RUNNING = 'RUNNING'
    COMPLETED = 'COMPLETED'
    PAUSED = 'PAUSED'
    INITIALIZED = 'INITIALIZED'


class WorkflowNode:
    """表示工作流程圖中的單一節點。

    每個節點都封裝了一個要執行的特定任務，例如尋找代理或呼叫代理的功能。它管理自己的狀態（例如，READY、RUNNING、COMPLETED、PAUSED）並且可以執行其分配的任務。

    """

    def __init__(
        self,
        task: str,
        node_key: str | None = None,
        node_label: str | None = None,
    ):
        self.id = str(uuid.uuid4())
        self.node_key = node_key
        self.node_label = node_label
        self.task = task
        self.results = None
        self.state = Status.READY

    async def get_planner_resource(self) -> AgentCard | None:
        logger.info(f'正在取得節點 {self.id} 的資源')
        config = get_mcp_server_config()
        async with client.init_session(
            config.host, config.port, config.transport
        ) as session:
            response = await client.find_resource(
                session, 'resource://agent_cards/planner_agent'
            )
            data = json.loads(response.contents[0].text)
            return AgentCard(**data['agent_card'][0])

    async def find_agent_for_task(self) -> AgentCard | None:
        logger.info(f'正在為任務尋找代理 - {self.task}')
        config = get_mcp_server_config()
        async with client.init_session(
            config.host, config.port, config.transport
        ) as session:
            result = await client.find_agent(session, self.task)
            agent_card_json = json.loads(result.content[0].text)
            logger.debug(f'為任務 {self.task} 找到了代理 {agent_card_json}')
            return AgentCard(**agent_card_json)

    async def run_node(
        self,
        query: str,
        task_id: str,
        context_id: str,
    ) -> AsyncIterable[dict[str, any]]:
        logger.info(f'正在執行節點 {self.id}')
        agent_card = None
        if self.node_key == 'planner':
            agent_card = await self.get_planner_resource()
        else:
            agent_card = await self.find_agent_for_task()
        async with httpx.AsyncClient() as httpx_client:
            client = A2AClient(httpx_client, agent_card)

            payload: dict[str, any] = {
                'message': {
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': query}],
                    'messageId': uuid4().hex,
                    'taskId': task_id,
                    'contextId': context_id,
                },
            }
            request = SendStreamingMessageRequest(
                id=str(uuid4()), params=MessageSendParams(**payload)
            )
            response_stream = client.send_message_streaming(request)
            async for chunk in response_stream:
                # 將產出儲存為節點的結果
                if isinstance(
                    chunk.root, SendStreamingMessageSuccessResponse
                ) and (isinstance(chunk.root.result, TaskArtifactUpdateEvent)):
                    artifact = chunk.root.result.artifact
                    self.results = artifact
                yield chunk


class WorkflowGraph:
    """表示工作流程節點的圖。"""

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self.nodes = {}
        self.latest_node = None
        self.node_type = None
        self.state = Status.INITIALIZED
        self.paused_node_id = None

    def add_node(self, node) -> None:
        logger.info(f'正在新增節點 {node.id}')
        self.graph.add_node(node.id, query=node.task)
        self.nodes[node.id] = node
        self.latest_node = node.id

    def add_edge(self, from_node_id: str, to_node_id: str) -> None:
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            raise ValueError('無效的節點 ID')

        self.graph.add_edge(from_node_id, to_node_id)

    async def run_workflow(
        self, start_node_id: str | None = None
    ) -> AsyncIterable[dict[str, any]]:
        logger.info('正在執行工作流程圖')
        if not start_node_id or start_node_id not in self.nodes:
            start_nodes = [n for n, d in self.graph.in_degree() if d == 0]
        else:
            start_nodes = [self.nodes[start_node_id].id]

        applicable_graph = set()

        for node_id in start_nodes:
            applicable_graph.add(node_id)
            applicable_graph.update(nx.descendants(self.graph, node_id))

        complete_graph = list(nx.topological_sort(self.graph))
        sub_graph = [n for n in complete_graph if n in applicable_graph]
        logger.info(f'子圖 {sub_graph} 大小 {len(sub_graph)}')
        self.state = Status.RUNNING
        # 另一種方法是遍歷所有節點，但我們只需要連接的節點。
        for node_id in sub_graph:
            node = self.nodes[node_id]
            node.state = Status.RUNNING
            query = self.graph.nodes[node_id].get('query')
            task_id = self.graph.nodes[node_id].get('task_id')
            context_id = self.graph.nodes[node_id].get('context_id')
            async for chunk in node.run_node(query, task_id, context_id):
                # 當工作流程節點暫停時，不要產生任何區塊
                # 而是讓循環完成。
                if node.state != Status.PAUSED:
                    if isinstance(
                        chunk.root, SendStreamingMessageSuccessResponse
                    ) and (
                        isinstance(chunk.root.result, TaskStatusUpdateEvent)
                    ):
                        task_status_event = chunk.root.result
                        context_id = task_status_event.context_id
                        if (
                            task_status_event.status.state
                            == TaskState.input_required
                            and context_id
                        ):
                            node.state = Status.PAUSED
                            self.state = Status.PAUSED
                            self.paused_node_id = node.id
                    yield chunk
            if self.state == Status.PAUSED:
                break
            if node.state == Status.RUNNING:
                node.state = Status.COMPLETED
        if self.state == Status.RUNNING:
            self.state = Status.COMPLETED

    def set_node_attribute(self, node_id, attribute, value) -> None:
        nx.set_node_attributes(self.graph, {node_id: value}, attribute)

    def set_node_attributes(self, node_id, attr_val) -> None:
        nx.set_node_attributes(self.graph, {node_id: attr_val})

    def is_empty(self) -> bool:
        return self.graph.number_of_nodes() == 0
