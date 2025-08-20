import pytest
from core import ToolBridge

class TestToolExecution:
    """驗證 Tool 能被正確執行"""
    
    def test_shell_tool_execution(self):
        """測試 Shell 腳本執行"""
        bridge = ToolBridge()
        
        # 執行診斷工具
        result = bridge.execute("diagnostic", "check_disk", "80")
        
        assert result is not None
        assert result['status'] in ['ok', 'warning']
        assert 'data' in result
    
    def test_tool_discovery(self):
        """測試工具發現機制"""
        bridge = ToolBridge()
        tools = bridge.discover_tools()
        
        assert 'diagnostic' in tools
        assert 'check_disk' in tools['diagnostic']
        assert 'check_memory' in tools['diagnostic']