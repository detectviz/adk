# 多模態即時代理

此模式展示了一個由 Google Gemini 驅動的即時對話代理。該代理處理音訊、視訊和文字互動，同時利用工具呼叫功能來增強回應。

![live_api_diagram](https://storage.googleapis.com/github-repo/generative-ai/sample-apps/e2e-gen-ai-app-starter-pack/live_api_diagram.png)

**主要元件：**

- **Python 後端** (在 `app/` 資料夾中)：一個使用 [FastAPI](https://fastapi.tiangolo.com/) 和 [google-genai](https://googleapis.github.io/python-genai/) 建構的生產就緒伺服器，具有以下特點：

  - 透過 WebSockets 在前端和 Gemini 模型之間進行**即時雙向通訊**
  - **整合工具呼叫**，帶有一個天氣資訊工具，用於展示外部資料檢索
  - 具有重試邏輯和自動重新連線功能的**生產級可靠性**
  - **部署靈活性**，支援 AI Studio 和 Vertex AI 端點
  - 用於收集使用者互動的**回饋記錄端點**

- **React 前端** (在 `frontend/` 資料夾中)：擴展了 [多模態即時 API Web 主控台](https://github.com/google-gemini/multimodal-live-api-web-console)，並增加了**自訂 URL** 和**回饋收集**等功能。

![live api demo](https://storage.googleapis.com/github-repo/generative-ai/sample-apps/e2e-gen-ai-app-starter-pack/live_api_pattern_demo.gif)

後端和前端都運行後，點擊前端 UI 中的播放按鈕以建立與後端的連線。現在您可以與多模態即時代理互動了！您可以嘗試問一些問題，例如「舊金山的天氣怎麼樣？」，來看看代理如何使用其天氣資訊工具。

## 多模態即時 API 的額外資源

探索這些資源以了解更多關於多模態即時 API 的資訊，並查看其使用範例：

- [Project Pastra](https://github.com/heiko-hotz/gemini-multimodal-live-dev-guide/tree/main)：Gemini 多模態即時 API 的綜合開發者指南。
- [Google Cloud 多模態即時 API 示範和範例](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/multimodal-live-api)：利用 Vertex AI 中的多模態即時 API 的程式碼範例和示範應用程式集合。
- [Gemini 2 Cookbook](https://github.com/google-gemini/cookbook/tree/main/gemini-2)：使用 Gemini 2 的實用範例和教學。
- [多模態即時 API Web 主控台](https://github.com/google-gemini/multimodal-live-api-web-console)：用於測試和實驗 Gemini 多模態即時 API 的互動式 React 網頁介面。

## 目前狀態與未來工作

此模式正在積極開發中。計劃未來增強的主要領域包括：

*   **可觀測性：** 實施全面的監控和追蹤功能。
*   **負載測試：** 整合負載測試功能。
