# SRE Assistant

**一個為 SRE 打造的 AI 原生智慧助理，旨在將您的專業知識轉化為一個能夠自動化診斷、自主學習並持續進化的 Assistant。**

## 核心理念

傳統監控是**工具**，SRE Assistant 是**夥伴**。致力於將 SRE 從重複的、手動的故障排除和監控配置中解放出來，讓他們能專注於更具戰略價值的系統性改進。

## 主要功能

* **對話式操作**: 直接用自然語言查詢指標、診斷故障、配置監控。  
* **自動化根因分析**: 當告警發生時，事件調查員 Agent 會自動關聯 Metrics, Logs, Traces 和變更歷史，提供包含證據鏈的根本原因假設。  
* **監控自動化配置**: 可觀測性專家 Agent 能為新上線的服務自動創建標準化的 Prometheus 監控和 Grafana 儀表板。  
* **持續學習的知識庫**: 平台會自動將成功的事件處理經驗，轉化為 Runbook 存入 RAG 知識庫，為未來的決策提供養料。

## 文檔定位

- **目標受眾**：新使用者、評估者、貢獻者、所有專案參與者
- **更新頻率**：每個版本更新
- **版本**：1.0.0
- **最後更新**：2025-08-21

## 文檔關係

```bash
[README.md] (專案入口) → AGENT.md (AI協作規範) → ARCHITECTURE.md (系統架構) → SPEC.md (技術規格) → TASKS.md (開發任務)
```

**閱讀路徑**：
- **後續閱讀**：[AGENT.md - AI協作指南](AGENT.md#ai協作原則) - 了解AI協作規範
- **深入了解**：[ARCHITECTURE.md - 系統架構](ARCHITECTURE.md#系統架構設計) - 理解系統設計
- **技術實作**：[技術實作](SPEC.md#技術棧現狀) - 獲取實作細節

---

> **智能化 SRE 平台**：基於 AI Agent 的全生命週期 SRE 解決方案

[![Current Focus: Phase 3](https://img.shields.io/badge/focus-Phase%203%20Postmortem-blue)](./ARCHITECTURE.md)
[![SSOT: contracts](https://img.shields.io/badge/SSOT-contracts-0A84FF)](./contracts)
[![Go 1.24](https://img.shields.io/badge/Go-1.24-00ADD8?logo=go)](#)
[![Python >= 3.11](https://img.shields.io/badge/Python-%3E%3D%203.11-3776AB?logo=python)](#)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-v1.11.0%20aligned-4285F4?logo=google)](https://google.github.io/adk-docs/)
[![License](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

## 快速開始

我們採用「零依賴」的啟動策略，讓您可以在任何開發環境中快速體驗平台的核心智慧。

# 1. 複製專案

```bash
git clone https://github.com/detectviz/sre-assistant.git  
cd sre-assistant
```

# 2. 一鍵啟動所有服務 (Go Core + Python ADK + 依賴項)

```bash
make up
```

啟動成功後，您可以透過 ADK Web UI (http://localhost:8000) 開始與您的 SRE Assistant 互動。


## SRE Assistant 工具整合
- 新增工具：Prometheus、Loki、Kubernetes、Alertmanager、Grafana 註記。
- 環境變數：請參考 `.env.example`。
- 測試：見 `tests/unit/`，以 `pytest` 搭配 monkeypatch 模擬 HTTP。


## 開發者指南（續）
- 設定 `.env` 可覆寫端點與允許的工具清單（`ALLOW_TOOLS`）。
- Python 單元測試：`pytest -q`
- 產生 gRPC 代碼（Go）：`./scripts/gen_proto.sh`（需安裝 `protoc` 與外掛）
- 結構化日誌：所有工具呼叫都會輸出 JSON 記錄 `tool_invoke` 事件，欄位含 `tool/outcome/duration_ms`。
