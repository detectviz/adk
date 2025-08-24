import json
import logging

from collections.abc import AsyncIterable

from a2a.types import (
    SendStreamingMessageSuccessResponse,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatusUpdateEvent,
)
from a2a_mcp.common import prompts
from a2a_mcp.common.base_agent import BaseAgent
from a2a_mcp.common.utils import init_api_key
from a2a_mcp.common.workflow import Status, WorkflowGraph, WorkflowNode
from google import genai


logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """協調者代理。"""

    def __init__(self):
        init_api_key()
        super().__init__(
            agent_name='Orchestrator Agent',
            description='促進代理間的通訊',
            content_types=['text', 'text/plain'],
        )
        self.graph = None
        self.results = []
        self.travel_context = {}
        self.query_history = []
        self.context_id = None

    async def generate_summary(self) -> str:
        client = genai.Client()
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompts.SUMMARY_COT_INSTRUCTIONS.replace(
                '{travel_data}', str(self.results)
            ),
            config={'temperature': 0.0},
        )
        return response.text

    def answer_user_question(self, question) -> str:
        try:
            client = genai.Client()
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompts.QA_COT_PROMPT.replace(
                    '{TRIP_CONTEXT}', str(self.travel_context)
                )
                .replace('{CONVERSATION_HISTORY}', str(self.query_history))
                .replace('{TRIP_QUESTION}', question),
                config={
                    'temperature': 0.0,
                    'response_mime_type': 'application/json',
                },
            )
            return response.text
        except Exception as e:
            logger.info(f'回答使用者問題時出錯：{e}')
        return '{"can_answer": "no", "answer": "無法根據提供的上下文回答"}'

    def set_node_attributes(
        self, node_id, task_id=None, context_id=None, query=None
    ):
        attr_val = {}
        if task_id:
            attr_val['task_id'] = task_id
        if context_id:
            attr_val['context_id'] = context_id
        if query:
            attr_val['query'] = query

        self.graph.set_node_attributes(node_id, attr_val)

    def add_graph_node(
        self,
        task_id,
        context_id,
        query: str,
        node_id: str = None,
        node_key: str = None,
        node_label: str = None,
    ) -> WorkflowNode:
        """將節點新增至圖中。"""
        node = WorkflowNode(
            task=query, node_key=node_key, node_label=node_label
        )
        self.graph.add_node(node)
        if node_id:
            self.graph.add_edge(node_id, node.id)
        self.set_node_attributes(node.id, task_id, context_id, query)
        return node

    def clear_state(self):
        self.graph = None
        self.results.clear()
        self.travel_context.clear()
        self.query_history.clear()

    async def stream(
        self, query, context_id, task_id
    ) -> AsyncIterable[dict[str, any]]:
        """執行並串流回應。"""
        logger.info(
            f'正在為會話 {context_id}，任務 {task_id} - {query} 運行 {self.agent_name} 串流'
        )
        if not query:
            raise ValueError('查詢不能為空')
        if self.context_id != context_id:
            # 當上下文變更時清除狀態
            self.clear_state()
            self.context_id = context_id

        self.query_history.append(query)
        start_node_id = None
        # 圖不存在，使用規劃器節點啟動新圖。
        if not self.graph:
            self.graph = WorkflowGraph()
            planner_node = self.add_graph_node(
                task_id=task_id,
                context_id=context_id,
                query=query,
                node_key='planner',
                node_label='Planner',
            )
            start_node_id = planner_node.id
        # 暫停狀態是指代理可能需要更多資訊。
        elif self.graph.state == Status.PAUSED:
            start_node_id = self.graph.paused_node_id
            self.set_node_attributes(node_id=start_node_id, query=query)

        # 如果工作流程圖是動態的，或者
        # 是根據規劃器的結果建立的，而規劃器
        # 本身不是圖的一部分，則可以避免此循環。
        # TODO: 使圖可沿邊動態迭代
        while True:
            # 在節點上設定屬性，以便我們傳播任務和上下文
            self.set_node_attributes(
                node_id=start_node_id,
                task_id=task_id,
                context_id=context_id,
            )
            # 恢復工作流程，當工作流程節點更新時使用。
            should_resume_workflow = False
            async for chunk in self.graph.run_workflow(
                start_node_id=start_node_id
            ):
                if isinstance(chunk.root, SendStreamingMessageSuccessResponse):
                    # 圖節點返回 TaskStatusUpdateEvent
                    # 檢查節點是否完成並繼續到下一個節點
                    if isinstance(chunk.root.result, TaskStatusUpdateEvent):
                        task_status_event = chunk.root.result
                        context_id = task_status_event.context_id
                        if (
                            task_status_event.status.state
                            == TaskState.completed
                            and context_id
                        ):
                            ## yeild??
                            continue
                        if (
                            task_status_event.status.state
                            == TaskState.input_required
                        ):
                            question = task_status_event.status.message.parts[
                                0
                            ].root.text

                            try:
                                answer = json.loads(
                                    self.answer_user_question(question)
                                )
                                logger.info(f'代理回答 {answer}')
                                if answer['can_answer'] == 'yes':
                                    # 協調者可以代表使用者設定查詢
                                    # 從暫停狀態恢復工作流程。
                                    query = answer['answer']
                                    start_node_id = self.graph.paused_node_id
                                    self.set_node_attributes(
                                        node_id=start_node_id, query=query
                                    )
                                    should_resume_workflow = True
                            except Exception:
                                logger.info('無法轉換回答資料')

                    # 圖節點返回 TaskArtifactUpdateEvent
                    # 儲存節點並繼續。
                    if isinstance(chunk.root.result, TaskArtifactUpdateEvent):
                        artifact = chunk.root.result.artifact
                        self.results.append(artifact)
                        if artifact.name == 'PlannerAgent-result':
                            # 規劃代理返回資料，更新圖。
                            artifact_data = artifact.parts[0].root.data
                            if 'trip_info' in artifact_data:
                                self.travel_context = artifact_data['trip_info']
                            logger.info(
                                f'正在使用 {len(artifact_data["tasks"])} 個任務節點更新工作流程'
                            )
                            # 定義邊
                            current_node_id = start_node_id
                            for idx, task_data in enumerate(
                                artifact_data['tasks']
                            ):
                                node = self.add_graph_node(
                                    task_id=task_id,
                                    context_id=context_id,
                                    query=task_data['description'],
                                    node_id=current_node_id,
                                )
                                current_node_id = node.id
                                # 從新插入的子圖狀態重新啟動圖
                                # 從剛建立的新節點開始。
                                if idx == 0:
                                    should_resume_workflow = True
                                    start_node_id = node.id
                        else:
                            # 不是規劃器，而是來自其他任務的產物，
                            # 繼續工作流程中的下一個節點。
                            # 客戶端不會取得產物，
                            # 工作流程結束時會顯示摘要。
                            continue
                # 當工作流程需要恢復時，不要產生部分結果。
                if not should_resume_workflow:
                    logger.info('未偵測到工作流程恢復，正在產生區塊')
                    # 產生部分執行結果
                    yield chunk
            # 圖已完成且無更新，因此可以跳出循環。
            if not should_resume_workflow:
                logger.info(
                    '工作流程迭代完成且未請求重新啟動。正在退出主循環。'
                )
                break
            else:
                # 可讀日誌
                logger.info('正在重新啟動工作流程循環。')
        if self.graph.state == Status.COMPLETED:
            # 所有個別操作均已完成，現在產生摘要
            logger.info(f'正在為 {len(self.results)} 個結果產生摘要')
            summary = await self.generate_summary()
            self.clear_state()
            logger.info(f'摘要：{summary}')
            yield {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': summary,
            }
