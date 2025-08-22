
# 安全性指南

## API Key 後門（開發用）
- 某些開發環境會使用 `DEV_API_KEY` 作為簡化驗證流程的後門。
- 風險：在生產環境使用將導致未授權存取。
- 要求：**生產環境必須停用**（不設定 `DEV_API_KEY` 環境變數，或設 `DISABLE_DEV_API_KEY=true`）。

## 建議
- 使用固定長度隨機 API Key，並於 DB 維護 `roles/permissions`。
- 搭配 Rate Limit、IP allowlist 與審計日誌。
