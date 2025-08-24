# ADK 中的雙向串流 (即時)

!!! info

    這是一個實驗性功能。目前僅在 Python 中可用。

!!! info

    這與伺服器端串流或權杖級串流不同。本節適用於雙向串流 (即時)。
    
ADK 中的雙向串流 (即時) 為 AI 代理程式增加了 [Gemini Live API](https://ai.google.dev/gemini-api/docs/live) 的低延遲雙向語音和視訊互動能力。

透過雙向串流 (即時) 模式，您可以為終端使用者提供自然、類似人類的語音對話體驗，包括使用者能夠用聲音指令中斷代理程式的回應。具有串流功能的代理程式可以處理文字、音訊和視訊輸入，並且可以提供文字和音訊輸出。

<div class="video-grid">
  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/Tu7-voU7nnw?si=RKs7EWKjx0bL96i5" title="購物禮賓員" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>

  <div class="video-item">
    <div class="video-container">
      <iframe src="https://www.youtube-nocookie.com/embed/LwHPYyw7u6U?si=xxIEhnKBapzQA6VV" title="購物禮賓員" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
    </div>
  </div>
</div>

<div class="grid cards" markdown>

-   :material-console-line: **快速入門 (雙向串流)**

    ---

    在本快速入門中，您將建立一個簡單的代理程式，並在 ADK 中使用串流來實作低延遲和雙向的語音和視訊通訊。

    - [快速入門 (雙向串流)](get-started-streaming-quickstart-streaming.md)

-   :material-console-line: **自訂音訊串流應用程式範例**

    ---

    本文概述了使用 ADK 串流和 FastAPI 建構的自訂非同步 Web 應用程式的伺服器和客戶端程式碼，該應用程式可透過伺服器發送事件 (SSE) 和 WebSocket 實現即時、雙向的音訊和文字通訊。

    - [自訂音訊串流應用程式範例 (SSE)](streaming-custom-streaming.md)
    - [自訂音訊串流應用程式範例 (WebSocket)](streaming-custom-streaming-ws.md)

-   :material-console-line: **雙向串流開發指南系列**

    ---

    一系列文章，深入探討使用 ADK 進行雙向串流開發。您可以學習基本概念和使用案例、核心 API 以及端到端應用程式設計。

    - [雙向串流開發指南系列：第 1 部分 - 簡介](streaming-dev-guide-part1.md)

-   :material-console-line: **串流工具**

    ---

    串流工具允許工具 (函式) 將中間結果串流回代理程式，代理程式可以對這些中間結果做出回應。例如，我們可以使用串流工具來監控股價的變化，並讓代理程式對其做出反應。另一個例子是，我們可以讓代理程式監控視訊串流，當視訊串流發生變化時，代理程式可以報告這些變化。

    - [串流工具](streaming-streaming-tools.md)

-   :material-console-line: **自訂音訊串流應用程式範例**

    ---

    本文概述了使用 ADK 串流和 FastAPI 建構的自訂非同步 Web 應用程式的伺服器和客戶端程式碼，該應用程式可透過伺服器發送事件 (SSE) 和 WebSocket 實現即時、雙向的音訊和文字通訊。

    - [串流設定](streaming-configuration.md)

-   :material-console-line: **部落格文章：Google ADK + Vertex AI Live API**

    ---

    本文展示了如何在 ADK 中使用雙向串流 (即時) 進行即時音訊/視訊串流。它提供了一個使用 LiveRequestQueue 建構自訂、互動式 AI 代理程式的 Python 伺服器範例。

    - [部落格文章：Google ADK + Vertex AI Live API](https://medium.com/google-cloud/google-adk-vertex-ai-live-api-125238982d5e)

</div>
