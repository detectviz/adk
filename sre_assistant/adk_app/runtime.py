
# -*- coding: utf-8 -*-
# ADK Runtime 封裝：以官方 Runner / InMemoryRunner 與 SessionService 管理對話狀態
# 參考：ADK Python API - runners、sessions、runtime、state、events 文件
# - Runner / InMemoryRunner：協調事件循環並提供 session_service（官方推薦模式）
# - session.state：保存任務狀態、跨步驟變量
# - run_async：串流事件（Event），最終回傳最終回覆與動作清單
from __future__ import annotations
import os, asyncio, time
from typing import Dict, Any, List

# --- ADK 匯入（依官方 API）---
from google.adk.runners import InMemoryRunner, Runner
from google.adk.events import Event
from google.adk.content import Content, Part

# 導入我們的 ADK 協調器（LoopAgent，內含 main_llm 與子專家 AgentTool）
from .coordinator import coordinator as ROOT_AGENT

APP_NAME = os.getenv("APP_NAME", "sre-assistant-adk")

# 單例 Runner：預設使用 InMemoryRunner（學習/開發環境）
# 生產可切換 Runner 並外掛 DatabaseSessionService，以避免 in-memory 的易失性
RUNNER = InMemoryRunner(agent=ROOT_AGENT, app_name=APP_NAME)

async def run_chat_async(user_id: str, session_id: str, message: str) -> Dict[str, Any]:
    """
    以 ADK Runner 非同步執行一次對話。
    - 建立/取得 session
    - 串流處理事件直到最終回覆
    - 回傳統一格式：{response, actions_taken, metrics}
    備註：符合 ADK 官方「Runner 與 SessionService」模式。
    """
    t0 = time.time()
    # 1) 確保 Session 存在（官方：runner.session_service.create_session(...)）
    await RUNNER.session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)

    # 2) 構造 Content（官方：Content/Part 作為輸入）
    content = Content(parts=[Part(text=message)], role="user")

    # 3) 串流事件（events）：依官方 runtime/event 機制
    final_text = ""
    actions: List[dict] = []
    async for event in RUNNER.run_async(user_id=user_id, session_id=session_id, new_message=content):
        # 收集工具調用與其他行為（官方：Event 與 actions）
        if getattr(event, "actions", None):
            for a in event.actions:
                try:
                    actions.append(a if isinstance(a, dict) else a.__dict__)
                except Exception:
                    pass
        # 擷取最終回覆（官方：event.is_final_response()）
        if event.is_final_response() and event.content and event.content.parts:
            # 以最簡形式取得純文字回覆（多段則取第一段文字）
            txt = next((p.text for p in event.content.parts if getattr(p, "text", None)), "")
            if txt:
                final_text = txt

    dt_ms = int((time.time() - t0) * 1000)
    return {"response": final_text, "actions_taken": actions, "metrics": {"duration_ms": dt_ms}}

def run_chat(user_id: str, session_id: str, message: str) -> Dict[str, Any]:
    """同步封裝：供傳統 HTTP 端點直接呼叫。"""
    return asyncio.get_event_loop().run_until_complete(run_chat_async(user_id=user_id, session_id=session_id, message=message))
