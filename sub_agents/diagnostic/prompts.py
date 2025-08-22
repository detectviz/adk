
# -*- coding: utf-8 -*-
# 檔案：sub_agents/diagnostic/prompts.py
# 角色：由 experts/diagnostic.yaml 讀取並導出 PROMPT 供 ADK 掛載。
from __future__ import annotations
from sre_assistant.sub_agents._loader import get_prompt
PROMPT: str = get_prompt("diagnostic")
