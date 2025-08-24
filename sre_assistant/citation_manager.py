# sre_assistant/citation_manager.py
# 說明：此檔案定義了 SRE Assistant 的引用格式化系統。
# SRECitationFormatter 負責將來自不同來源（如文件、設定檔、日誌、知識庫）的
# 原始引用資料，轉換為標準化、人類可讀的引用格式。

from typing import List, Dict, Any

class SRECitationFormatter:
    """
    一個靈活的引用格式化工具，可根據來源類型生成不同的引用樣式。
    旨在提供清晰、一致且可追溯的資訊來源標示。
    """

    def format_citations(self, sources: List[Dict[str, Any]]) -> str:
        """
        將一個來源字典列表格式化為一個完整的、帶有標題和編號的引用字串。

        Args:
            sources: 一個字典列表，每個字典代表一個引用來源。
                     每個字典應包含一個 'type' 鍵。

        Returns:
            一個格式化好的引用字串。如果沒有來源，則返回空字串。
        """
        if not sources:
            return ""

        formatted_list = []
        for i, source in enumerate(sources, 1):
            formatter = self._get_formatter(source.get("type", "generic"))
            formatted_list.append(f"{i}. {formatter(source)}")

        return "References:\n" + "\n".join(formatted_list)

    def _get_formatter(self, source_type: str):
        """根據來源類型返回對應的格式化函式。"""
        formatters = {
            "document": self._format_document,
            "config": self._format_config,
            "log": self._format_log,
            "kb": self._format_kb,
            "generic": self._format_generic,
        }
        return formatters.get(source_type, self._format_generic)

    def _format_document(self, source: Dict[str, Any]) -> str:
        """
        格式化文件來源。
        預期輸入: {'type': 'document', 'title': '...', 'section': '...', 'url': '...'}
        """
        title = source.get('title', 'N/A')
        section = source.get('section')
        url = source.get('url')

        citation = f"[Document] Title: {title}"
        if section:
            citation += f", Section: {section}"
        if url:
            citation += f" (Source: {url})"
        return citation

    def _format_config(self, source: Dict[str, Any]) -> str:
        """
        格式化設定檔來源。
        預期輸入: {'type': 'config', 'file_path': '...', 'key': '...'}
        """
        file_path = source.get('file_path', 'N/A')
        key = source.get('key', 'N/A')
        return f"[Config] File: {file_path}, Key: {key}"

    def _format_log(self, source: Dict[str, Any]) -> str:
        """
        格式化日誌來源。
        預期輸入: {'type': 'log', 'source_name': '...', 'timestamp': '...'}
        """
        source_name = source.get('source_name', 'N/A')
        timestamp = source.get('timestamp', 'N/A')
        return f"[Log] Source: {source_name}, Timestamp: {timestamp}"

    def _format_kb(self, source: Dict[str, Any]) -> str:
        """
        格式化知識庫文章來源。
        預期輸入: {'type': 'kb', 'article_id': '...', 'title': '...'}
        """
        article_id = source.get('article_id', 'N/A')
        title = source.get('title', 'N/A')
        return f"[Knowledge Base] Article: {article_id}, Title: {title}"

    def _format_generic(self, source: Dict[str, Any]) -> str:
        """
        格式化通用或未知來源。
        """
        description = source.get('description', 'No description provided.')
        return f"[Generic Source] {description}"

# --- 範例使用 ---
if __name__ == '__main__':
    formatter = SRECitationFormatter()

    sample_sources = [
        {'type': 'document', 'title': 'SRE Handbook', 'section': 'Chapter 5: Eliminating Toil', 'url': 'https://sre.google/sre-book/eliminating-toil/'},
        {'type': 'config', 'file_path': '/etc/prometheus/prometheus.yml', 'key': 'global.scrape_interval'},
        {'type': 'log', 'source_name': 'prod-api-server-xyz', 'timestamp': '2025-08-24T12:30:00Z'},
        {'type': 'kb', 'article_id': 'KB12345', 'title': 'How to restart the Foobar service'},
        {'type': 'monitoring_tool', 'description': 'Grafana Dashboard "API Server Health"'},
        {'type': 'document', 'title': 'Incident Management Playbook'},
    ]

    formatted_string = formatter.format_citations(sample_sources)
    print(formatted_string)

    # 預期輸出:
    # References:
    # 1. [Document] Title: SRE Handbook, Section: Chapter 5: Eliminating Toil (Source: https://sre.google/sre-book/eliminating-toil/)
    # 2. [Config] File: /etc/prometheus/prometheus.yml, Key: global.scrape_interval
    # 3. [Log] Source: prod-api-server-xyz, Timestamp: 2025-08-24T12:30:00Z
    # 4. [Knowledge Base] Article: KB12345, Title: How to restart the Foobar service
    # 5. [Generic Source] No description provided.
    # 6. [Document] Title: Incident Management Playbook
