# 使用 A2A SDK 進行追蹤

此範例專案展示了 A2A SDK 中的分散式追蹤功能，並將追蹤匯出至 Jaeger。它以一個使用 Google Agent Development Kit (ADK) 建構的代理為特色，利用 Google 搜尋工具來回應使用者查詢。

主要目標是展示如何從 A2A 伺服器和客戶端啟用和匯出追蹤，以及如何使用 Jaeger 和 Grafana 收集和視覺化這些追蹤。

## 核心功能

* **代理：** 一個簡單的對話代理，使用 Google 搜尋來回答問題。
* **追蹤：** 根據 `__main__.py` 中的設定啟用。
* **追蹤匯出：** 追蹤被發送到在 Docker 中運行的 Jaeger 後端。
* **視覺化：** 可以在 Jaeger UI 和 Grafana 中查看和分析追蹤。

## 檔案

* `__main__.py`：應用程式的主要進入點。它設定 OpenTelemetry 追蹤器、Jaeger 匯出器，並啟動 A2A 伺服器。
* `agent_executor.py`：包含代理的邏輯，包括整合 Google 搜尋工具和為追蹤特定操作建立自訂範圍。
* `docker-compose.yaml`：一個 Docker Compose 檔案，可輕鬆設定和運行 Jaeger 和 Grafana 服務。

## 先決條件

* Python 3.10+
* Docker 和 Docker Compose
* Google API 金鑰

## 設定

1. **設定環境變數：**

    ```bash
    export GOOGLE_API_KEY="您的_GOOGLE_API_金鑰"
    ```

    將 `"您的_GOOGLE_API_金鑰"` 替換為您的 api 金鑰

2. **啟動 Jaeger 和 Grafana：**

    ```bash
    docker compose up -d
    ```

    這將啟動：
    * **Jaeger：** UI 可在 `http://localhost:16686` 存取。
    * **Grafana：** UI 可在 `http://localhost:3000` 存取（預設登入：`admin`/`admin`）。

    **關於 OTLP 埠的重要說明：** Python 應用程式 (`__main__.py`) 設定為透過 OTLP grpc 將追蹤發送到 Jaeger。提供的用於 Jaeger 的 `docker-compose.yaml` 啟用了 OTLP 收集器。請確保將埠 `4317` 從主機對應到 Jaeger 容器。如果您希望在 docker-compose.yaml 中更改埠，則必須更新 `__main__.py`。

## 運行應用程式

1. 設定環境變數並運行 Docker 容器後，執行主腳本：

    ```bash
    uv run .
    ```

2. 應用程式將在埠 10020 上啟動。
    運行 CLI 或 UI 工具與代理互動。追蹤將被收集並發送到 Jaeger。

3. 要停止應用程式，您通常可以使用 `Ctrl+C`。

## 查看追蹤

### 1. Jaeger UI

* 打開您的網頁瀏覽器並導覽至 Jaeger UI：`http://localhost:16686`。
* 在左側邊欄搜尋下的「服務」下拉式選單中，選擇 `a2a-telemetry-sample`（這是在 `__main__.py` 中設定的服務名稱）。
* 點擊「尋找追蹤」按鈕。您應該會看到一個追蹤列表，每個追蹤對應與代理的一次互動。
* 點擊任何追蹤以查看其詳細的範圍層次結構、日誌和標籤。您將看到整體代理調用、對 Google 搜尋工具的呼叫以及 LLM（如果適用）處理的範圍。

### 2. Grafana UI

Grafana 可以設定為使用 Jaeger 作為資料來源，讓您可以視覺化追蹤並建立儀表板。

* **存取 Grafana：** 在瀏覽器中打開 `http://localhost:3000`。使用預設憑證登入：使用者名稱 `admin`，密碼 `admin`。首次登入時可能會提示您更改密碼。

* **新增 Jaeger 作為資料來源：**
    1. 導覽至「連線」（或在舊版 Grafana 中點擊齒輪圖示進入「設定」，然後點擊「資料來源」）。
    2. 點擊「新增新連線」或「新增資料來源」。
    3. 在可用資料來源清單中搜尋「Jaeger」並選擇它。
    4. 設定 Jaeger 資料來源設定：
        * **名稱：** 您可以保留為 `Jaeger` 或選擇自訂名稱。
        * **URL：** `http://jaeger:16686`
            *（此 URL 使用在 `docker-compose.yaml` 中定義的 Jaeger 服務名稱 `jaeger`，允許 Grafana 在 Docker 網路內連接到 Jaeger）。*
        * 除非您有特定要求，否則將其他設定保留為預設值。
    5. 點擊「儲存並測試」。您應該會看到一個確認訊息，如「資料來源正在運作」。

* **在 Grafana 中探索追蹤：**
    1. 在左側邊欄上，導覽至「探索」。
    2. 從「探索」視圖左上角的下拉式選單中，選擇您剛剛設定的 Jaeger 資料來源。
    3. 您現在可以查詢追蹤：
        * 使用「服務」下拉式選單選擇 `a2a-telemetry-sample`。
        * 如果您有追蹤 ID，可以按追蹤 ID 搜尋，或使用其他篩選器。
    4. 您還可以建立儀表板（儀表板 -> 新增儀表板 -> 新增視覺化）並使用 Jaeger 資料來源來建構追蹤資料的面板。

## 停止服務

要停止並移除 `docker-compose.yaml` 中定義的 Jaeger 和 Grafana 容器，請運行：

```bash
docker compose down
```

## 免責聲明

重要提示：所提供的範例程式碼僅供示範之用，並說明了代理對代理 (A2A) 協議的機制。在建構生產應用程式時，將任何在您直接控制之外運行的代理視為潛在不受信任的實體至關重要。

從外部代理接收的所有資料——包括但不限於其代理卡、訊息、產出和任務狀態——都應作為不受信任的輸入處理。例如，惡意代理可能提供在其欄位（例如，描述、名稱、技能描述）中包含精心製作的資料的代理卡。如果在使用此資料時未經清理就用於建構大型語言模型 (LLM) 的提示，可能會使您的應用程式面臨提示注入攻擊的風險。未能在使用前正確驗證和清理此資料，可能會給您的應用程式帶來安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護他們的系統和使用者。
