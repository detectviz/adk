# ADK 代理 (Agent)

此範例使用代理開發套件 (Agent Development Kit, ADK) 建立一個使用 A2A 進行通訊的簡單趣聞產生器。

## 先決條件

- Python 3.10 或更高版本
- 存取 LLM 和 API 金鑰

## 執行範例

1. 導覽至範例目錄：

    ```bash
    cd samples/python/agents/adk_facts
    ```

2. 安裝需求套件

    ```bash
    pip install -r requirements.txt
    ```

3. 建立一個包含您的 Gemini API 金鑰的 `.env` 檔案：

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

4. 執行 A2A 代理 (Agent)：

    ```bash
    uvicorn agent:a2a_app --host localhost --port 8001
    ```

5. 執行 ADK 網頁伺服器

    ```bash
    # 在另一個終端機中，執行 adk 網頁伺服器
    adk web samples/python/agents/
    ```

  在網頁使用者介面中，選取 `adk_facts` 代理 (Agent)。

## 部署至 Google Cloud Run

```sh
gcloud run deploy sample-a2a-agent \
    --port=8080 \
    --source=. \
    --allow-unauthenticated \
    --region="us-central1" \
    --project=$GOOGLE_CLOUD_PROJECT \
    --set-env-vars=GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_REGION=$GOOGLE_CLOUD_REGION,GOOGLE_GENAI_USE_VERTEXAI=true
```
