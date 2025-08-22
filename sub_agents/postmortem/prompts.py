
# 檔案：sub_agents/postmortem/prompts.py
# 角色：由 experts/postmortem.yaml 讀取並導出 PROMPT 供 ADK 掛載。
from __future__ import annotations
from sre_assistant.sub_agents._loader import get_prompt
PROMPT: str = get_prompt("postmortem")
