import pytest
from unittest.mock import MagicMock
from agents.sre_assistant.agent import SREAssistant
from contracts.messages.sre_messages import ToolResponse

class TestSREAssistant:
    """驗證 SREAssistant 的邏輯"""

    def test_check_health_logic(self):
        """測試 check_health 方法是否能正確調用工具並整合結果"""
        # 準備
        assistant = SREAssistant()

        # 模擬 ToolRunner 的 invoke 方法
        mock_runner = MagicMock()
        assistant.runner = mock_runner

        # 設置模擬的返回值
        mock_runner.invoke.side_effect = [
            ToolResponse(success=True, status="ok", message="Disk usage is normal.", data={"usage": 10}),
            ToolResponse(success=True, status="warning", message="Memory usage is high.", data={"usage": 85})
        ]

        # 執行
        result = assistant.check_health(threshold=80)

        # 驗證
        assert "disk" in result
        assert "memory" in result
        
        assert result["disk"]["status"] == "ok"
        assert result["memory"]["status"] == "warning"
        
        assert mock_runner.invoke.call_count == 2
        
        # 驗證第一次呼叫 (check_disk)
        first_call_args = mock_runner.invoke.call_args_list[0][0]
        assert first_call_args[0] == "bridge.exec"
        assert first_call_args[1].params["category"] == "diagnostic"
        assert first_call_args[1].params["name"] == "check_disk"

        # 驗證第二次呼叫 (check_memory)
        second_call_args = mock_runner.invoke.call_args_list[1][0]
        assert second_call_args[0] == "bridge.exec"
        assert second_call_args[1].params["category"] == "diagnostic"
        assert second_call_args[1].params["name"] == "check_memory"
