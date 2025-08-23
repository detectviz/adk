# sre-assistant/utils/a2a_client.py
"""
A2A 客戶端：消費外部代理，符合 2025 I/O A2A 增強協議
參考 ARCHITECTURE.md 第 6.3 節
"""

import os
import uuid
import asyncio
from typing import Dict, Any, List

# --- 模擬 ADK/A2A SDK 元件 ---
# 說明：由於我們無法訪問真實的 google.adk 或 a2a_sdk，
# 我們在這裡創建最小化的模擬類別，以使程式碼結構完整且可測試。

class MockRemoteA2aAgent:
    def __init__(self, endpoint: str, auth_config: Dict, streaming_config: Dict):
        self.endpoint = endpoint
        self.auth_config = auth_config
        self.streaming_config = streaming_config

    async def invoke(self, action: str, parameters: Dict, request_id: str):
        print(f"Invoking remote agent at {self.endpoint} for action '{action}' with request_id '{request_id}'")
        # 模擬一個 streaming 回應
        class MockStreamingResponse:
            def __init__(self):
                self.streaming = True
                self.result = {"status": "completed", "summary": "mocked_summary"}

            async def __aiter__(self):
                for i in range(3):
                    yield {"type": "progress_update", "data": f"Step {i+1} complete"}
                    await asyncio.sleep(0.1)

        return MockStreamingResponse()

class MockAgentCardResolver:
    async def resolve(self, endpoint: str) -> Dict:
        # 模擬解析 AgentCard
        print(f"Resolving agent card for {endpoint}")
        return {
            "skills": [
                {"id": "detect_anomalies"},
                {"id": "scan_vulnerabilities"}
            ]
        }

# --- 核心實現 ---

class SREExternalAgentConnector:
    """
    連接外部 A2A 代理，用於 SRE 任務委託（如異常檢測或安全掃描）
    """

    def __init__(self, external_endpoints: List[str] = None):
        self.remote_agents: Dict[str, MockRemoteA2aAgent] = {}
        self.card_resolver = MockAgentCardResolver()
        self.external_endpoints = external_endpoints or [
            "https://ml-anomaly-detector.example.com",
            "https://security-scanner.example.com"
        ]
        self._init_agents()

    def _init_agents(self):
        """初始化遠端代理連接"""
        for endpoint in self.external_endpoints:
            # 從 URL 中提取一個唯一的代理 ID
            agent_id = endpoint.split("://")[1].split(".")[0]
            self.remote_agents[agent_id] = MockRemoteA2aAgent(
                endpoint=endpoint,
                auth_config={
                    "type": "oauth2",
                    "client_id": "sre-assistant-client",
                    "client_secret": os.getenv("A2A_CLIENT_SECRET"),
                    "auto_refresh": True,
                },
                streaming_config={
                    "enabled": True,
                    "protocol": "grpc_stream",
                }
            )

    async def invoke_remote_agent(self, agent_id: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """非同步調用遠端代理"""
        if agent_id not in self.remote_agents:
            raise ValueError(f"Unknown agent: {agent_id}")

        agent = self.remote_agents[agent_id]
        card = await self.card_resolver.resolve(agent.endpoint)

        supported_actions = [skill['id'] for skill in card.get("skills", [])]
        if action not in supported_actions:
            raise ValueError(f"Action '{action}' not supported by agent '{agent_id}'")

        request_id = str(uuid.uuid4())
        response = await agent.invoke(
            action=action,
            parameters=parameters,
            request_id=request_id
        )

        if response.streaming:
            streaming_results = []
            async for chunk in response:
                print(f"Streaming chunk from {agent_id}: {chunk}")
                streaming_results.append(chunk)

            return self._merge_streaming_results(streaming_results, response.result)

        return response.result

    def _merge_streaming_results(self, streaming_results: List, final_result: Dict) -> Dict:
        """合併 streaming 結果和最終結果"""
        return {
            "final_result": final_result,
            "streaming_data": streaming_results,
            "total_chunks": len(streaming_results)
        }

    async def detect_anomalies(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """調用外部 ML 異常檢測代理"""
        return await self.invoke_remote_agent(
            agent_id="ml-anomaly-detector",
            action="detect_anomalies",
            parameters=metrics_data
        )

# --- 示例使用 ---
async def main():
    print("Initializing SREExternalAgentConnector...")
    connector = SREExternalAgentConnector()
    print("\nInvoking anomaly detection agent...")
    result = await connector.detect_anomalies({"cpu_usage": 95, "time_range": "5m"})
    print("\nAnomaly detection result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
