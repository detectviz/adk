# TASKS.md (待辦事項)

本文件追蹤 SRE Assistant 專案剩餘的開發與優化任務。

## P1 - 短期改進 (預計一週內完成)

- **[ ] SRE 量化指標**
    - [ ] 實作覆盤用的「五個為什麼 (5 Whys)」模板。
    - [參考](docs/references/google-sre-book/Appendix%20D%20-%20Example%20Postmortem.md)
- **[ ] 端到端 (E2E) 測試套件**
    - [ ] 為完整的人工介入 (Human-in-the-Loop, HITL) 審批流程建立測試。
    - [ ] 開發 API 端到端測試。
    - [ ] 建立性能基準測試套件。

## P2 - 中期優化 (預計 2-4 週內完成)

- **[ ] 可觀測性增強**
    - [ ] 整合 OpenTelemetry 以進行追蹤 (traces) 與指標 (metrics)。
    - [ ] 跨服務實現分散式追蹤。
    - [ ] 為關鍵操作定義並匯出客製化指標。
- **[ ] 部署優化**
    - [ ] 實作金絲雀 (Canary) 部署策略。
    - [ ] 新增對藍綠 (Blue-Green) 部署的支援。
    - [ ] 建立在 SLO 違規或部署失敗時的自動回滾機制。

## P3 - 長期改進

- **[ ] 基礎設施即程式碼 (Infrastructure as Code)**
    - [ ] 開發 Terraform 模組以部署代理及其依賴項。
- **[ ] 容器化**
    - [ ] 進行 Docker 映像檔優化 (例如，使用更小的基礎映像、多階段建置)。
