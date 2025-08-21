
# -*- coding: utf-8 -*-
# ADK Runtime 封裝（v14）：支援可切換 SessionService（InMemory / Database），符合官方 Runner/Session API。
# - 以環境變數 SESSION_BACKEND 控制：memory|db
# - DB 後端透過 DatabaseSessionService 連接 SQLite/PostgreSQL/MySQL 等（官方支援）
# - 保留 run_chat / run_chat_async 供 REST/SSE 層呼叫
from __future__ import annotations
import os, asyncio, time
from typing import Dict, Any, List, Optional

# --- ADK 正式匯入（以官方 API 名稱為準）---
from google.adk.runners import Runner, InMemoryRunner
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.events import Event
from google.adk.content import Content, Part

# 導入我們的 ADK 協調器（LoopAgent，內含 main_llm 與子專家 AgentTool）
from .coordinator import coordinator as ROOT_AGENT

APP_NAME = os.getenv("APP_NAME", "sre-assistant-adk")

def _build_runner() -> Runner:
    """
    根據環境變數建立 Runner：
    - SESSION_BACKEND=memory（預設）：使用 InMemoryRunner（內含 InMemorySessionService）
    - SESSION_BACKEND=db：以 DatabaseSessionService 連接資料庫 URI（SESSION_DB_URI）
    官方實踐：在生產環境用 DatabaseSessionService 或 VertexAiSessionService；本專案以官方 DatabaseSessionService 為準。
    """
    backend = os.getenv("SESSION_BACKEND", "memory").lower()
    if backend == "db":
        db_uri = os.getenv("SESSION_DB_URI", "sqlite:///./sessions.db")
        # 建議搭配連線參數與 Pool 設定（參考官方 issues 對應資料庫方言）
        session_service = DatabaseSessionService(database_uri=db_uri)
        return Runner(agent=ROOT_AGENT, app_name=APP_NAME, session_service=session_service)
    # 預設記憶體版本（教學/本地開發）
    return InMemoryRunner(agent=ROOT_AGENT, app_name=APP_NAME)

# 單例 Runner（可因環境切換而異）
RUNNER: Runner = _build_runner()

async def run_chat_async(user_id: str, session_id: str, message: str) -> Dict[str, Any]:
    """
    以 ADK Runner 非同步執行一次對話：建立/取得 Session → 串流事件 → 收斂最終回覆。
    注意：所有 SessionService 操作（create/get）皆為 async 介面（依官方 1.0 後規格）。
    """
    t0 = time.time()
    # 確保 Session 存在（多次呼叫同 session_id 安全）
    await RUNNER.session_service.create_session(app_name=APP_NAME, user_id=user_id, session_id=session_id)

    # 構造 Content 作為使用者訊息
    content = Content(parts=[Part(text=message)], role="user")

    # 串流事件，蒐集工具動作與最後回覆（符合官方 Event 流程）
    final_text: str = ""
    actions: List[dict] = []

    async for event in RUNNER.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if getattr(event, "actions", None):
            for a in event.actions:
                try:
                    actions.append(a if isinstance(a, dict) else a.__dict__)
                except Exception:
                    pass
        if event.is_final_response() and event.content and event.content.parts:
            txt = next((p.text for p in event.content.parts if getattr(p, "text", None)), "")
            if txt:
                final_text = txt

    dt_ms = int((time.time() - t0) * 1000)
    return {"response": final_text, "actions_taken": actions, "metrics": {"duration_ms": dt_ms}}

def run_chat(user_id: str, session_id: str, message: str) -> Dict[str, Any]:
    """同步封裝：供傳統 HTTP 端點直接呼叫。"""
    return asyncio.get_event_loop().run_until_complete(run_chat_async(user_id=user_id, session_id=session_id, message=message))
