# 部署您的代理

當您使用 ADK 建置並測試您的代理後，下一步就是部署它，以便在生產環境中存取、查詢和使用，或與其他應用程式整合。部署會將您的代理從本機開發機器移至可擴展且可靠的環境。

![部署您的代理](../assets/deploy-agent.png)

## 部署選項

您的 ADK 代理可以根據您對生產準備或自訂靈活性的需求，部署到各種不同的環境中：

### Vertex AI 中的 Agent Engine

[Agent Engine](deploy-agent-engine.md) 是 Google Cloud 上的一個全代管自動擴展服務，專為部署、管理和擴展使用 ADK 等框架建置的 AI 代理而設計。

了解更多關於[將您的代理部署到 Vertex AI Agent Engine](deploy-agent-engine.md) 的資訊。

### Cloud Run

[Cloud Run](https://cloud.google.com/run) 是 Google Cloud 上的一個代管自動擴展運算平台，可讓您以容器式應用程式的形式執行您的代理。

了解更多關於[將您的代理部署到 Cloud Run](deploy-cloud-run.md) 的資訊。

### Google Kubernetes Engine (GKE)

[Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) 是 Google Cloud 的一個代管 Kubernetes 服務，可讓您在容器化環境中執行您的代理。如果您需要對部署有更多控制權，以及執行開放模型，GKE 是一個很好的選擇。

了解更多關於[將您的代理部署到 GKE](deploy-gke.md) 的資訊。

### 其他與容器相容的基礎架構

您可以手動將您的代理打包成容器映像檔，然後在任何支援容器映像檔的環境中執行它。例如，您可以在 Docker 或 Podman 中本機執行它。如果您偏好離線或中斷連線執行，或在與 Google Cloud 沒有連線的系統中執行，這是一個很好的選擇。

請遵循[將您的代理部署到 Cloud Run](deploy-cloud-run.md) 的說明，特別是其中描述如何使用自訂 Dockerfile 的情況。
