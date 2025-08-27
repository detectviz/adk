# AGENT.md - SRE Assistant 使用指南

本文件為 AI 代理提供操作此程式碼庫的具體、可執行的指南。人類使用者請參閱 `README.md`。

## 專案概覽

SRE Assistant 是一個智慧型網站可靠性工程 (SRE) 代理，旨在自動化事件回應、執行根本原因分析，並透過與 Grafana 的深度整合來優化系統可靠性。

- **詳細功能規格**: 請參閱 [SPEC.md](SPEC.md)
- **系統架構**: 請參閱 [ARCHITECTURE.md](ARCHITECTURE.md)
- **實施路線圖**: 請參閱 [ROADMAP.md](ROADMAP.md)

---

## 開發環境設置

使用 Docker Compose 快速啟動本地開發環境，其中包含所有必要的依賴項（例如 PostgreSQL, Grafana, Loki 等）。

```bash
# 克隆程式碼庫
git clone https://github.com/your-org/sre-assistant
cd sre-assistant

# 啟動開發環境
docker-compose up -d
```

---

## 測試指令

本專案的測試套件對於確保程式碼品質至關重要。在提交任何變更之前，請務必運行相關測試。

```bash
# 運行所有單元測試和整合測試
pytest
```

- **測試策略與指南**: 詳細的測試方法請參閱 [TESTING.md](docs/TESTING.md)。
- **CI/CD**: 持續整合流程定義於 `.github/workflows/` 目錄中，會在每次提交時自動運行測試。

---

## 疑難排解 (Troubleshooting)
當你在開發或測試過程中遇到錯誤（例如，執行階段錯誤、測試失敗），請遵循以下步驟解決問題：
1. **查閱架構文件**: 首先，仔細閱讀 `ARCHITECTURE.md`，確保你的變更符合專案的設計原則和 ADK 最佳實踐。
2. **參考開發文檔**: 其次，查閱 `docs/README.md` 或 `docs/TESTING.md` 等相關文件，尋找常見問題的解決方案或設定指南。

---

## 部署

### 生產環境部署 (Kubernetes)

建議使用 Helm 來部署 SRE Assistant 到生產環境的 Kubernetes 集群。

```bash
helm repo add sre-assistant https://charts.sre-assistant.io
helm install sre-assistant sre-assistant/sre-assistant \
  --set grafana.enabled=true \
  --set auth.provider=oauth2 \
  --set memory.backend=weaviate
```

- **詳細部署指南**: 更多關於部署和配置的選項，請參閱 [ARCHITECTURE.md](ARCHITECTURE.md) 中的部署章節。

---

## 程式碼風格與規範

為保持程式碼庫的一致性和可讀性，請遵循以下規範：

- **Python**:
    - 使用 [Black](https://github.com/psf/black) 進行程式碼格式化。
    - 遵循 PEP 8 編碼風格。
    - 使用類型提示 (Type Hinting)。
- **提交訊息**:
    - 遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範。

---

## 安全性注意事項

- **認證與授權**: 系統採用 OAuth 2.0 / OIDC 進行身份驗證，並整合 Grafana 的 RBAC 進行授權。
- **秘密管理**: 所有敏感資訊（如 API 金鑰）都應透過 HashiCorp Vault 或 Google Secret Manager 進行管理。
- **詳細安全架構**: 完整的安全設計，請參閱 [ARCHITECTURE.md](ARCHITECTURE.md) 中的安全架構章節。

---

## 技術棧與核心依賴

- **核心框架**: Google Agent Development Kit (ADK)
- **後端**: Python 3.11+
- **前端**: Grafana Plugin SDK, TypeScript, React
- **可觀測性**: Grafana LGTM Stack (Loki, Grafana, Tempo, Mimir)
- **數據庫**: PostgreSQL (結構化數據), Weaviate (向量數據)