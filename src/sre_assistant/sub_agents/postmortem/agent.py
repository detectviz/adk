# src/sre_assistant/sub_agents/postmortem/agent.py
# 說明：(預留位置) 覆盤專家 (PostmortemExpert) 代理。
# 未來的實作將包含生成結構化事後檢討報告的工具。

from google.adk.agents import LlmAgent
from typing import Optional, Dict, Any

from google.genai.types import GenerateContentConfig

class PostmortemAgent(LlmAgent):
    """(預留位置) 覆盤專家代理"""
    def __init__(self, **kwargs: Any):
        # 說明：修改 __init__ 以接受 **kwargs，使其與 Pydantic 模型的行為一致。
        # 這樣可以從外部傳入 'name', 'config' 等參數，同時提供預設值。
        kwargs.setdefault("name", "PostmortemExpert")
        kwargs.setdefault("model", "gemini-1.5-flash-001")

        safety_settings = kwargs.pop("safety_settings", None)
        generation_config = kwargs.pop("generation_config", None)

        if safety_settings or generation_config:
            kwargs["generate_content_config"] = GenerateContentConfig(
                safety_settings=safety_settings,
                temperature=generation_config.temperature if generation_config else 0.4,
                top_p=generation_config.top_p if generation_config else 1.0,
                top_k=generation_config.top_k if generation_config else 32,
                candidate_count=generation_config.candidate_count if generation_config else 1,
                max_output_tokens=generation_config.max_output_tokens if generation_config else 8192,
            )

        super().__init__(**kwargs)
