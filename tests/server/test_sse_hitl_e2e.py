
# -*- coding: utf-8 -*-
# 測試：啟動 FastAPI 應用，訂閱 /api/v1/events，並呼叫 /api/v1/hitl/mock_request 觸發事件。
import asyncio, json, pytest, sys
pytestmark = pytest.mark.asyncio

async def _read_one_event(ac):
    # 讀取 SSE 的一個事件（簡化解析）
    async with ac.stream("GET", "/api/v1/events") as r:
        async for line in r.aiter_lines():
            if line.startswith("data: "):
                payload = json.loads(line[len("data: ") : ])
                return payload

async def test_sse_hitl_flow():
    try:
        from sre_assistant.server.app import app
    except Exception:
        pytest.skip("app 不存在，略過")
    import httpx
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        # 並行啟動讀取與觸發事件
        reader = asyncio.create_task(_read_one_event(ac))
        await ac.post("/api/v1/hitl/mock_request", data={"function_call_id": "fc-demo"})
        ev = await asyncio.wait_for(reader, timeout=5.0)
        assert ev.get("type") == "adk_request_credential"
        assert ev.get("function_call_id") == "fc-demo"
