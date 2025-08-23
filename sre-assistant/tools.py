# sre-assistant/tools.py
# 說明：此檔案定義了版本化的工具註冊表，用於管理 SRE Assistant 的所有工具。
# 它支援工具的版本控制、相容性檢查和按類別獲取工具。
# 參考 ARCHITECTURE.md 第 5 節。

from typing import Dict, List, Any, Optional
from enum import Enum

# --- 模擬 ADK SDK 元件 ---
# 說明：由於無法訪問真實的 google.adk，我們在此創建模擬類別。

class MockTool:
    """模擬基礎工具類別"""
    def __init__(self, name="mock_tool", description="A mock tool"):
        self.name = name
        self.description = description

class ToolRegistry:
    """模擬 ADK 的基礎工具註冊表"""
    def __init__(self):
        self._registry: Dict[str, Any] = {}
        self._defaults: Dict[str, str] = {}

    def register(self, name: str, tool_version: Any):
        self._registry[name] = tool_version
        print(f"Registered tool: {name}")

    def get(self, name: str) -> Optional[Any]:
        return self._registry.get(name)

    def has_default(self, name: str) -> bool:
        return name in self._defaults

    def set_default(self, name: str, version: str):
        self._defaults[name] = version
        print(f"Set default version for {name} to {version}")

    def get_default_version(self, name: str) -> Optional[str]:
        return self._defaults.get(name)

class ToolVersion:
    """模擬 ADK 的工具版本類別"""
    def __init__(self, tool: Any, version: str, deprecated: bool = False, sunset_date: Optional[str] = None):
        self.tool = tool
        self.version = version
        self.deprecated = deprecated
        self.sunset_date = sunset_date

class ToolNotFoundError(Exception):
    pass

class FallbackStrategy(Enum):
    USE_PREVIOUS_VERSION = "use_previous_version"
    FAIL = "fail"

# --- 模擬的工具 ---
# 由於子代理中的工具檔案可能不存在或不完整，我們先定義模擬工具。
class PromQLQueryTool(MockTool):
    def __init__(self):
        super().__init__(name="promql_query", description="Queries Prometheus")

class LogSearchTool(MockTool):
    def __init__(self):
        super().__init__(name="log_search", description="Searches logs")

class K8sRolloutRestartTool(MockTool):
    def __init__(self):
        super().__init__(name="k8s_rollout_restart", description="Restarts a k8s deployment")

# --- 核心實現 ---

class VersionedToolRegistry(ToolRegistry):
    """
    支援版本管理的工具註冊表。

    Features:
    - 註冊帶有版本的工具。
    - 根據版本獲取工具。
    - 實現版本相容性檢查 (check_compatibility)。
    - 支援版本回退策略。
    """

    def __init__(self):
        super().__init__()
        self.fallback_strategy = FallbackStrategy.USE_PREVIOUS_VERSION
        # 相容性矩陣，定義工具版本與其依賴的外部服務（如 Prometheus API）的相容性
        self.compatibility_matrix = {
            "promql_query": {
                "2.1.0": {"prometheus_api": ">=2.40.0"},
                "2.0.0": {"prometheus_api": ">=2.35.0, <2.40.0"}
            },
            "k8s_rollout_restart": {
                "3.0.0": {"kubernetes_api": ">=1.25.0"},
                "2.0.0": {"kubernetes_api": "<1.25.0"}
            }
        }
        self._register_all_tools()

    def _register_all_tools(self):
        """註冊 SRE Assistant 的所有工具及其版本"""
        self.register_versioned_tool(PromQLQueryTool(), "2.1.0")
        self.register_versioned_tool(PromQLQueryTool(), "2.0.0") # 舊版本
        self.register_versioned_tool(LogSearchTool(), "1.5.0")
        self.register_versioned_tool(K8sRolloutRestartTool(), "3.0.0")

        # 設置默認版本
        self.set_default("promql_query", "2.1.0")
        self.set_default("log_search", "1.5.0")
        self.set_default("k8s_rollout_restart", "3.0.0")

    def register_versioned_tool(self, tool: Any, version: str):
        """註冊一個帶有版本的工具"""
        tool_version = ToolVersion(
            tool=tool,
            version=version
        )
        # 註冊時使用 "名稱@版本" 的格式
        self.register(name=f"{tool.name}@{version}", tool_version=tool_version)

    def check_compatibility(self, tool_name: str, tool_version: str, env_versions: Dict[str, str]) -> bool:
        """
        **技術債務實現**
        檢查給定工具版本是否與當前環境的服務版本相容。

        Args:
            tool_name: 工具的名稱 (e.g., "promql_query")。
            tool_version: 工具的版本 (e.g., "2.1.0")。
            env_versions: 一個包含環境中服務版本的字典 (e.g., {"prometheus_api": "2.41.0"})。

        Returns:
            如果相容則返回 True，否則返回 False。
        """
        if tool_name not in self.compatibility_matrix:
            return True # 如果沒有定義相容性規則，則默認為相容

        rules = self.compatibility_matrix[tool_name].get(tool_version)
        if not rules:
            return False # 如果該版本沒有規則，視為不相容

        # 簡易的版本比較邏輯 (實際應用中應使用如 'packaging' 函式庫)
        for service, required_version in rules.items():
            env_version = env_versions.get(service)
            if not env_version:
                return False # 環境中缺少必要的服務版本資訊

            # 這裡只做簡單的字符串比較，一個完整的實現需要解析 '>=', '<' 等符號
            # 例如: ">=2.40.0"
            if '>=' in required_version:
                if not (env_version >= required_version.replace('>=', '')):
                    return False
            elif '<' in required_version:
                 if not (env_version < required_version.replace('<', '')):
                    return False
            # ...可以擴展更多比較符號

        return True

    def get_tool(self, name: str, version: str = None, env_versions: Dict[str, str] = None) -> Optional[Any]:
        """
        獲取工具，支援版本選擇和相容性檢查。
        """
        if version:
            # 如果指定了版本，檢查其相容性
            if env_versions and not self.check_compatibility(name, version, env_versions):
                print(f"Warning: Tool {name}@{version} is not compatible with the environment.")
                # 可以在此處實現降級邏輯或直接失敗
                return None

            tool_version_obj = self.get(f"{name}@{version}")
            if tool_version_obj:
                return tool_version_obj.tool
            else:
                raise ToolNotFoundError(f"Tool {name} with version {version} not found.")

        # 如果未指定版本，獲取默認版本
        default_version = self.get_default_version(name)
        if default_version:
            return self.get(f"{name}@{default_version}").tool

        raise ToolNotFoundError(f"Tool {name} not found or no default version is set.")

# --- 導出註冊表實例 ---
tool_registry = VersionedToolRegistry()

# --- 示例使用 ---
if __name__ == "__main__":
    print("--- Tool Registry Demo ---")

    # 獲取默認工具
    prom_tool = tool_registry.get_tool("promql_query")
    print(f"Default PromQL tool: {prom_tool.name if prom_tool else 'Not Found'}")

    # 檢查相容性
    env1 = {"prometheus_api": "2.41.0"} # 與 v2.1.0 相容
    env2 = {"prometheus_api": "2.38.0"} # 與 v2.1.0 不相容，但與 v2.0.0 相容
    env3 = {"other_service": "1.0.0"}  # 缺少 prometheus_api 版本

    is_compatible_v2_1_env1 = tool_registry.check_compatibility("promql_query", "2.1.0", env1)
    print(f"Is promql_query@2.1.0 compatible with env1? {is_compatible_v2_1_env1}") # True

    is_compatible_v2_1_env2 = tool_registry.check_compatibility("promql_query", "2.1.0", env2)
    print(f"Is promql_query@2.1.0 compatible with env2? {is_compatible_v2_1_env2}") # False

    is_compatible_v2_0_env2 = tool_registry.check_compatibility("promql_query", "2.0.0", env2)
    print(f"Is promql_query@2.0.0 compatible with env2? {is_compatible_v2_0_env2}") # True

    # 根據環境版本獲取工具
    tool_for_env1 = tool_registry.get_tool("promql_query", version="2.1.0", env_versions=env1)
    print(f"Tool for env1: {'Found' if tool_for_env1 else 'Not Found'}")

    tool_for_env2 = tool_registry.get_tool("promql_query", version="2.1.0", env_versions=env2)
    print(f"Tool for env2 (requesting incompatible v2.1.0): {'Found' if tool_for_env2 else 'Not Found'}")
