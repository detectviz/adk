import base64
import os

from typing import Any

from llama_cloud_services.parse import LlamaParse
from llama_index.core.llms import ChatMessage
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.llms.google_genai import GoogleGenAI
from pydantic import BaseModel, Field


## 工作流程事件 (Workflow Events)


class LogEvent(Event):
    msg: str


class InputEvent(StartEvent):
    msg: str
    attachment: str | None = None
    file_name: str | None = None


class ParseEvent(Event):
    attachment: str
    file_name: str
    msg: str


class ChatEvent(Event):
    msg: str


class ChatResponseEvent(StopEvent):
    response: str
    citations: dict[int, list[str]]


## 結構化輸出 (Structured Outputs)


class Citation(BaseModel):
    """對文件中特定行的引文。"""

    citation_number: int = Field(
        description='在回應文本中使用的特定內嵌引文編號。'
    )
    line_numbers: list[int] = Field(
        description='正在引用的文件中的行號。'
    )


class ChatResponse(BaseModel):
    """對使用者的回應，包含內嵌引文（若有）。"""

    response: str = Field(
        description='對使用者的回應，包含內嵌引文（若有）。'
    )
    citations: list[Citation] = Field(
        default=list,
        description='引文列表，其中每個引文都是一個物件，用於將引文編號映射到正在引用的文件中的行號。',
    )


class ParseAndChat(Workflow):
    def __init__(
        self,
        timeout: float | None = None,
        verbose: bool = False,
        **workflow_kwargs: Any,
    ):
        super().__init__(timeout=timeout, verbose=verbose, **workflow_kwargs)
        self._sllm = GoogleGenAI(
            model='gemini-2.0-flash', api_key=os.getenv('GOOGLE_API_KEY')
        ).as_structured_llm(ChatResponse)
        self._parser = LlamaParse(api_key=os.getenv('LLAMA_CLOUD_API_KEY'))
        self._system_prompt_template = """\
您是一個樂於助人的助理，可以回答有關文件的問題、提供引文並進行對話。

這是有行號的文件：
<document_text>
{document_text}
</document_text>

從文件中引用內容時：
1. 您的內嵌引文應在每個回應中從 [1] 開始，並為每個額外的內嵌引文增加 1。
2. 每個引文編號應對應文件中的特定行。
3. 如果一個內嵌引文涵蓋多個連續行，請盡力優先使用一個涵蓋所需行號的單一內嵌引文。
4. 如果引文需要涵蓋多個不連續的行，則可接受 [2, 3, 4] 之類的引文格式。
5. 例如，如果回應包含「變壓器架構... [1]。」和「注意力機制... [2]。」，並且這些分別來自第 10-12 行和第 45-46 行，那麼：citations = [[10, 11, 12], [45, 46]]
6. 始終從 [1] 開始您的引文，並為每個額外的內嵌引文增加 1。請勿使用行號作為內嵌引文編號，否則我會丟掉工作。
"""

    @step
    def route(self, ev: InputEvent) -> ParseEvent | ChatEvent:
        if ev.attachment:
            return ParseEvent(
                attachment=ev.attachment, file_name=ev.file_name, msg=ev.msg
            )
        return ChatEvent(msg=ev.msg)

    @step
    async def parse(self, ctx: Context, ev: ParseEvent) -> ChatEvent:
        ctx.write_event_to_stream(LogEvent(msg='正在解析文件...'))
        results = await self._parser.aparse(
            base64.b64decode(ev.attachment),
            extra_info={'file_name': ev.file_name},
        )
        ctx.write_event_to_stream(LogEvent(msg='文件解析成功。'))

        documents = await results.aget_markdown_documents(split_by_page=False)

        # 因為我們只有一個文件且不按頁面分割，所以我們可以直接使用第一個
        document = documents[0]

        # 將文件分割成行並添加行號
        # 這將用於引文
        document_text = ''
        for idx, line in enumerate(document.text.split('\n')):
            document_text += f"<line idx='{idx}'>{line}</line>\n"

        await ctx.set('document_text', document_text)
        return ChatEvent(msg=ev.msg)

    @step
    async def chat(self, ctx: Context, event: ChatEvent) -> ChatResponseEvent:
        current_messages = await ctx.get('messages', default=[])
        current_messages.append(ChatMessage(role='user', content=event.msg))
        ctx.write_event_to_stream(
            LogEvent(
                msg=f'正在與 {len(current_messages)} 則初始訊息聊天。'
            )
        )

        document_text = await ctx.get('document_text', default='')
        if document_text:
            ctx.write_event_to_stream(
                LogEvent(msg='正在插入系統提示...')
            )
            input_messages = [
                ChatMessage(
                    role='system',
                    content=self._system_prompt_template.format(
                        document_text=document_text
                    ),
                ),
                *current_messages,
            ]
        else:
            input_messages = current_messages

        response = await self._sllm.achat(input_messages)
        response_obj: ChatResponse = response.raw
        ctx.write_event_to_stream(
            LogEvent(msg='收到 LLM 回應，正在解析引文...')
        )

        current_messages.append(
            ChatMessage(role='assistant', content=response_obj.response)
        )
        await ctx.set('messages', current_messages)

        # 從文件文本中解析出引文
        citations = {}
        if document_text:
            for citation in response_obj.citations:
                line_numbers = citation.line_numbers
                for line_number in line_numbers:
                    start_idx = document_text.find(
                        f"<line idx='{line_number}'>"
                    )
                    end_idx = document_text.find(
                        f"<line idx='{line_number + 1}'>"
                    )
                    citation_text = (
                        document_text[
                            start_idx
                            + len(f"<line idx='{line_number}'>") : end_idx
                        ]
                        .replace('</line>', '')
                        .strip()
                    )

                    if citation.citation_number not in citations:
                        citations[citation.citation_number] = []
                    citations[citation.citation_number].append(citation_text)

        return ChatResponseEvent(
            response=response_obj.response, citations=citations
        )


async def main():
    """ParseAndChat 代理的測試腳本。"""
    agent = ParseAndChat()
    ctx = Context(agent)

    # 執行 `wget https://arxiv.org/pdf/1706.03762 -O attention.pdf` 來取得檔案
    # 或使用您自己的檔案
    with open('attention.pdf', 'rb') as f:
        attachment = f.read()

    handler = agent.run(
        start_event=InputEvent(
            msg='您好！關於這個文件，您可以告訴我些什麼？',
            attachment=attachment,
            file_name='test.pdf',
        ),
        ctx=ctx,
    )

    async for event in handler:
        if not isinstance(event, StopEvent):
            print(event)

    response: ChatResponseEvent = await handler

    print(response.response)
    for citation_number, citation_texts in response.citations.items():
        print(f'引文 {citation_number}: {citation_texts}')

    # 測試上下文持久性
    handler = agent.run(
        '我最後問了您什麼？',
        ctx=ctx,
    )
    response: ChatResponseEvent = await handler
    print(response.response)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
