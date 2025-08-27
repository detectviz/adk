# src/sre_assistant/tool_registry.py
"""
此檔案定義了一個支援版本管理的工具註冊表 (VersionedToolRegistry)。

在一個複雜的 SRE 自動化系統中，我們使用的工具 (如與 Prometheus 或 Kubernetes
互動的工具) 會隨著時間演進，其依賴的外部系統 API 也可能發生變化。
一個簡單的註冊表無法處理這種複雜性。

此版本化的註冊表旨在解決以下問題：
- **版本控制**: 允許同一個工具的多個版本共存。
- **依賴管理**: 可以定義工具版本與其依賴的外部服務 (如 API) 版本之間的相容性。
- **環境適應性**: 能夠根據當前環境的配置（例如，Kubernetes API 版本），
  動態地選擇一個相容的工具版本來執行。
- **向後相容**: 提供回退策略（例如，如果最新版本不相容，則嘗試使用前一個版本）。

此實現參考了 `ARCHITECTURE.md` 第 5 節關於工具管理的設計原則。
"""

from typing import Dict, List, Any, Optional
from enum import Enum
from packaging import version as packaging_version
from packaging.specifiers import SpecifierSet

# --- 模擬 ADK SDK 元件 ---
# 說明：由於無法存取真實的 google.adk，我們在此創建模擬類別，
# 以便在本地環境中獨立開發和測試工具註冊表的邏輯。

class MockTool:
    """模擬的基礎工具類別，代表一個可執行的工具。"""
    def __init__(self, name="mock_tool", description="A mock tool"):
        self.name = name
        self.description = description

class ToolRegistry:
    """模擬 ADK 的基礎工具註冊表，提供基本的註冊和獲取功能。"""
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
    """模擬 ADK 的工具版本類別，封裝了工具實例及其版本資訊。"""
    def __init__(self, tool: Any, version: str, deprecated: bool = False, sunset_date: Optional[str] = None):
        self.tool = tool
        self.version = version
        self.deprecated = deprecated
        self.sunset_date = sunset_date

class ToolNotFoundError(Exception):
    """當找不到指定工具時引發的自定義異常。"""
    pass

class FallbackStrategy(Enum):
    """定義當工具版本不相容時的回退策略。"""
    USE_PREVIOUS_VERSION = "use_previous_version"
    FAIL = "fail"

# --- 模擬的 SRE 工具 ---
# 這些是具體的工具模擬，用於演示註冊表的功能。
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
    一個支援版本管理的工具註冊表。

    此類別繼承自基礎的 ToolRegistry，並增加了版本化註冊、
    相容性檢查和版本選擇等進階功能。
    """

    def __init__(self):
        """初始化版本化註冊表。"""
        super().__init__()
        self.fallback_strategy = FallbackStrategy.USE_PREVIOUS_VERSION
        # 相容性矩陣：定義工具版本與其依賴的外部服務 API 版本的相容性規則。
        # 規則格式遵循 packaging.specifiers.SpecifierSet (例如 ">=2.40.0")。
        self.compatibility_matrix = {
            "promql_query": {
                "2.1.0": {"prometheus_api": ">=2.40.0"},
                "2.0.0": {"prometheus_api": ">=2.35.0,<2.40.0"}
            },
            "k8s_rollout_restart": {
                "3.0.0": {"kubernetes_api": ">=1.25.0"},
                "2.0.0": {"kubernetes_api": "<1.25.0"}
            }
        }
        self._register_all_tools()

    def _register_all_tools(self):
        """
        註冊 SRE Assistant 的所有可用工具及其版本。
        在真實應用中，這可以透過動態掃描等方式實現。
        """
        self.register_versioned_tool(PromQLQueryTool(), "2.1.0")
        self.register_versioned_tool(PromQLQueryTool(), "2.0.0")
        self.register_versioned_tool(LogSearchTool(), "1.5.0")
        self.register_versioned_tool(K8sRolloutRestartTool(), "3.0.0")

        # 設置每個工具的默認使用版本
        self.set_default("promql_query", "2.1.0")
        self.set_default("log_search", "1.5.0")
        self.set_default("k8s_rollout_restart", "3.0.0")

    def register_versioned_tool(self, tool: Any, version: str):
        """
        註冊一個帶有明確版本的工具。

        Args:
            tool (Any): 要註冊的工具實例。
            version (str): 該工具的版本號，應遵循語義化版本 (SemVer)。
        """
        tool_version = ToolVersion(tool=tool, version=version)
        # 內部註冊時使用 "名稱@版本" 的格式作為唯一鍵。
        self.register(name=f"{tool.name}@{version}", tool_version=tool_version)

    def check_compatibility(self, tool_name: str, tool_version: str, env_versions: Dict[str, str]) -> bool:
        """
        檢查指定的工具版本是否與當前環境的服務版本相容。

        Args:
            tool_name (str): 工具的名稱 (例如 "promql_query")。
            tool_version (str): 工具的版本 (例如 "2.1.0")。
            env_versions (Dict[str, str]): 一個包含當前環境中外部服務版本的字典
                                          (例如 `{"prometheus_api": "2.41.0"}`)。

        Returns:
            bool: 如果相容則返回 True，否則返回 False。
        """
        if tool_name not in self.compatibility_matrix:
            return True  # 如果沒有定義相容性規則，則默認為相容
        rules = self.compatibility_matrix[tool_name].get(tool_version)
        if not rules:
            return False # 如果該版本沒有規則，視為不相容

        for service, required_specifier in rules.items():
            env_version_str = env_versions.get(service)
            if not env_version_str:
                return False # 環境中缺少必要的服務版本資訊
            try:
                # 使用 packaging library 進行可靠的版本比較
                spec = SpecifierSet(required_specifier)
                env_version = packaging_version.parse(env_version_str)
                if env_version not in spec:
                    return False
            except packaging_version.InvalidVersion:
                print(f"Warning: Invalid version format for {service}: {env_version_str}")
                return False
        return True

    def get_tool(self, name: str, version: str = None, env_versions: Dict[str, str] = None) -> Optional[Any]:
        """
        獲取一個工具實例，支援版本選擇和自動相容性檢查。

        Args:
            name (str): 要獲取的工具名稱。
            version (str, optional): 指定要獲取的工具版本。如果為 None，則獲取默認版本。
            env_versions (Dict[str, str], optional): 當前環境的服務版本，用於相容性檢查。

        Raises:
            ToolNotFoundError: 如果找不到指定的工具或版本。

        Returns:
            Optional[Any]: 符合條件的工具實例，如果不相容或找不到則返回 None。
        """
        if version:
            # 如果指定了版本，檢查其相容性
            if env_versions and not self.check_compatibility(name, version, env_versions):
                print(f"Warning: Tool {name}@{version} is not compatible with the environment.")
                # TODO: 在此處實現回退策略 (fallback strategy)
                return None
            tool_version_obj = self.get(f"{name}@{version}")
            if tool_version_obj:
                return tool_version_obj.tool
            else:
                raise ToolNotFoundError(f"Tool {name} with version {version} not found.")

        # 如果未指定版本，獲取默認版本
        default_version = self.get_default_version(name)
        if default_version:
            tool_version_obj = self.get(f"{name}@{default_version}")
            if tool_version_obj:
                return tool_version_obj.tool

        raise ToolNotFoundError(f"Tool {name} not found or no default version is set.")

# --- 導出註冊表單例 ---
tool_registry = VersionedToolRegistry()

# --- 示例使用 ---
if __name__ == "__main__":
    """當此檔案作為主腳本執行時，運行一個演示，展示註冊表的功能。"""
    print("--- Tool Registry Demo ---")

    # 獲取默認工具
    prom_tool = tool_registry.get_tool("promql_query")
    print(f"Default PromQL tool: {prom_tool.name if prom_tool else 'Not Found'}")

    # 檢查相容性
    env1 = {"prometheus_api": "2.41.0"}
    env2 = {"prometheus_api": "2.38.0"}
    env3 = {"other_service": "1.0.0"}

    is_compatible_v2_1_env1 = tool_registry.check_compatibility("promql_query", "2.1.0", env1)
    print(f"Is promql_query@2.1.0 compatible with env1? {is_compatible_v2_1_env1}")

    is_compatible_v2_1_env2 = tool_registry.check_compatibility("promql_query", "2.1.0", env2)
    print(f"Is promql_query@2.1.0 compatible with env2? {is_compatible_v2_1_env2}")

    is_compatible_v2_0_env2 = tool_registry.check_compatibility("promql_query", "2.0.0", env2)
    print(f"Is promql_query@2.0.0 compatible with env2? {is_compatible_v2_0_env2}")

    # 根據環境版本獲取工具
    tool_for_env1 = tool_registry.get_tool("promql_query", version="2.1.0", env_versions=env1)
    print(f"Tool for env1: {'Found' if tool_for_env1 else 'Not Found'}")

    tool_for_env2 = tool_registry.get_tool("promql_query", version="2.1.0", env_versions=env2)
    print(f"Tool for env2 (requesting incompatible v2.1.0): {'Found' if tool_for_env2 else 'Not Found'}")
