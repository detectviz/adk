# BeeAI 框架 A2A 聊天代理 (Agent)

此範例示範如何使用 [BeeAI 框架](https://docs.beeai.dev/introduction/welcome) 搭配代理對代理 (A2A) 通訊協定來建立一個聊天代理 (Agent)。此代理 (Agent) 可以存取網頁搜尋和天氣工具。

## 先決條件

- Python 3.10 或更高版本
- [Ollama](https://ollama.com/) 已安裝並正在執行

## 執行範例

1. 導覽至範例目錄：

    ```bash
    cd samples/python/agents/beeai-chat
    ```

2. 建立虛擬環境並安裝需求套件

    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install .
    ```

3. 將模型拉取到 ollama：

   ```bash
   ollama pull granite3.3:8b
   ```

4. 執行 A2A 代理 (Agent)：

    ```bash
    python __main__.py
    ```

5. 執行 [BeeAI 聊天客戶端](../../hosts/beeai-chat/README.md)

## 使用 Docker 執行

```sh
docker build -t beeai_chat_agent .
docker run -p 9999:9999 -e OLLAMA_API_BASE="http://host.docker.internal:11434" beeai_chat_agent
```
