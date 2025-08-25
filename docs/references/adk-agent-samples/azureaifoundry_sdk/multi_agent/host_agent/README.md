# Azure AI 路由代理 (Routing Agent)

一個使用 Azure AI Agents 進行智慧任務路由並委派給專門遠端代理 (Agent) 的多代理 (multi-agent) 系統。

## 🚀 功能

- **Azure AI Agents 整合**：由 Azure AI 提供支援的核心路由邏輯
- **多代理 (Multi-Agent) 協調**：智慧委派給天氣和住宿專家
- **網頁介面**：現代化的 Gradio 聊天介面
- **即時處理**：具有狀態更新的串流回應
- **資源管理**：自動清理和錯誤處理

## 🏗️ 架構

```
使用者請求 → Azure AI 路由代理 (Routing Agent) → 遠端專家代理 (Agent)
                      ↓
              天氣代理 (Agent) / 住宿代理 (Agent)
```

## 📋 先決條件

1. **Azure AI Foundry 專案**，並已部署模型
2. 已設定的 **Azure 驗證**（Azure CLI、服務主體或受控識別）
3. 在已設定的通訊埠上執行的**遠端代理 (Remote Agents)**
4. **Python 3.13+** 及必要的相依性

## ⚙️ 設定

### 環境變數

透過複製範例範本來建立一個 `.env` 檔案：

```bash
cp .env.example .env
```