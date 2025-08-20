from sre_adk import Agent, tool
import json

class DiagnosticExpert(Agent):
    """診斷專家 - 使用 Shell 腳本工具"""
    
    name = "診斷專家"
    description = "執行系統健康檢查"
    
    @tool("檢查磁碟使用率")
    async def check_disk(self, threshold: int = 80) -> dict:
        """
        檢查所有磁碟的使用率
        """
        # 調用 Go Core 執行 Shell 腳本
        result = await self.execute_tool(
            category="diagnostic",
            name="check_disk",
            args=[str(threshold)]
        )
        
        # 解析結果並添加智能分析
        if result['status'] == 'warning':
            # 分析哪些磁碟需要關注
            critical_disks = [
                d for d in result['data'] 
                if d['usage'] > threshold
            ]
            
            return {
                "diagnosis": "磁碟空間告警",
                "severity": "medium",
                "details": f"發現 {len(critical_disks)} 個磁碟超過閾值",
                "recommendations": [
                    "清理日誌文件",
                    "檢查臨時文件",
                    "考慮擴容"
                ],
                "raw_data": result['data']
            }
        
        return {
            "diagnosis": "磁碟空間正常",
            "severity": "low",
            "details": "所有磁碟使用率在正常範圍",
            "raw_data": result['data']
        }
    
    @tool("系統健康檢查")
    async def health_check(self) -> dict:
        """
        執行完整的系統健康檢查
        """
        # 並行執行多個檢查
        disk_result = await self.check_disk()
        memory_result = await self.check_memory()
        
        # 綜合分析
        overall_status = "healthy"
        issues = []
        
        if disk_result['severity'] != 'low':
            overall_status = "warning"
            issues.append("磁碟空間")
            
        if memory_result['severity'] != 'low':
            overall_status = "warning"
            issues.append("記憶體")
        
        return {
            "overall_status": overall_status,
            "issues": issues,
            "disk": disk_result,
            "memory": memory_result
        }