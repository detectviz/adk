# 監控與可觀測性

![監控流程](https://storage.googleapis.com/github-repo/generative-ai/sample-apps/e2e-gen-ai-app-starter-pack/monitoring_flow.png)

### 追蹤與日誌擷取

模板化的代理利用 [OpenTelemetry](https://opentelemetry.io/) 來實現全面的可觀測性，將事件發送到 Google Cloud Trace 和 Google Cloud Logging。與大型語言模型 (LLM) 的每一次互動都被儀器化，從而能夠對使用此框架建構的代理的請求流程進行詳細追蹤。

該框架利用 [CloudTraceSpanExporter](https://cloud.google.com/python/docs/reference/spanner/latest/opentelemetry-tracing) 來擷取和匯出追蹤資料。為了克服 Cloud Trace ([256 位元組屬性值限制](https://cloud.google.com/trace/docs/quotas#limits_on_spans)) 和 [Cloud Logging](https://cloud.google.com/logging/quotas) ([256KB 日誌條目大小](https://cloud.google.com/logging/quotas)) 的限制，模板化專案的 `app/utils/tracing.py` 中實作了 CloudTraceSpanExporter 的自訂擴充功能。

此擴充功能透過以下方式增強了可觀測性：

- 為每個擷取的事件建立一個對應的 Google Cloud Logging 條目。
- 當負載超過 256KB 時，自動將事件資料儲存到 Google Cloud Storage。

記錄的負載與原始追蹤相關聯，確保可以從 Cloud Trace 主控台無縫存取。

### 日誌路由器

事件透過[日誌路由器](https://cloud.google.com/logging/docs/routing/overview)轉發到 BigQuery，以進行長期儲存和分析。日誌路由器的部署是透過模板化專案中 `deployment/terraform` 的 Terraform 程式碼處理的。

### Looker Studio 儀表板

一旦資料寫入 BigQuery，就可以用來填充 [Looker Studio 儀表板](https://lookerstudio.google.com/c/reporting/46b35167-b38b-4e44-bd37-701ef4307418/page/tEnnC)。如果使用非 ADK 代理，請使用[此儀表板](https://lookerstudio.google.com/c/reporting/fa742264-4b4b-4c56-81e6-a667dd0f853f/page/tEnnC)。

這個儀表板模板提供了一個起點，可用於在擷取的資料之上建立自訂的視覺化圖表。

## 免責聲明

**注意：** 模板化的代理旨在讓您能夠在您的 Google Cloud 專案中實現*您的*使用案例的可觀測性。Google Cloud 不會記錄、監控或以其他方式存取從已部署資源產生的任何資料。有關更多詳細資訊，請參閱 [Google Cloud 服務條款](https://cloud.google.com/terms/service-terms)。
