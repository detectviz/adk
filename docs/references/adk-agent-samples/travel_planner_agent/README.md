# 旅遊規劃代理範例
> 這是一個遵循 A2A (Agent2Agent) 協定的 Python 實作。
> 它是一個符合 OpenAI 模型規格的旅遊助理，能夠為您提供旅遊規劃服務。
> 一個基於 Google 官方 a2a-python SDK 實作的旅遊助理示範。

## 入門指南

1. 使用您自己的 OpenAI API 金鑰等資訊更新 [config.json](config.json)。
> 您需要修改對應於 model_name 和 base_url 的值。

```json
{
  "model_name":"qwen3-32b", //若為空，則預設為 gpt-4o
  "api_key": "API_KEY",
  "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1" //若為空，則預設為 ChatGPT
}
```



2. 建立一個包含您的 API 金鑰的環境檔案：
> 您需要設定對應於 API_KEY 的值。

   ```bash
   echo "API_KEY=your_api_key_here" > .env
   ```


3. 啟動伺服器
    ```bash
    uv run .
    ```

4. 執行循環客戶端
    ```bash
    uv run loop_client.py
    ```
   

## 授權

本專案依據 [Apache 2.0 授權](/LICENSE) 的條款進行授權。

## 貢獻

有關貢獻指南，請參閱 [CONTRIBUTING.md](/CONTRIBUTING.md)。



## 免責聲明
重要提示：所提供的範例程式碼僅供示範之用，並說明代理對代理 (A2A) 協定的機制。在建置生產應用程式時，將任何在您直接控制之外運作的代理視為潛在不受信任的實體至關重要。

從外部代理接收的所有資料——包括但不限於其代理卡 (AgentCard)、訊息、成品和任務狀態——都應作為不受信任的輸入處理。例如，惡意代理可能會提供一個在其欄位（例如，描述、名稱、技能描述）中包含精心設計資料的代理卡。如果在使用此類資料時未經清理就用於建構大型語言模型 (LLM) 的提示，可能會使您的應用程式面臨提示注入攻擊的風險。未能在使用前正確驗證和清理此類資料可能會給您的應用程式帶來安全漏洞。

開發人員有責任實施適當的安全措施，例如輸入驗證和安全處理憑證，以保護其系統和使用者。