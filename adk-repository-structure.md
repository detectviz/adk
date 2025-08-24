# ADK 官方建議目錄結構 Repository Structure

``` bash
├── my_adk_project/
│   ├── __init__.py
│   ├── agent.py                  # 組合根代理程式 (例如 SequentialAgent)
│   ├── memory.py                 # 配置長期記憶體後端
│   ├── artifacts.py              # 透過 ArtifactLoader 載入文件以進行檢索增強生成 (RAG)
│   ├── prompts.py                # 根代理程式的全球系統指令和提示範本。包含代理程式的「大腦」及其工作流程
│   ├── tools.py                  # 所有代理程式共用的可重複使用工具
│   ├── utils/                    # 代理程式之間共用的通用公用程式
│   │   ├── __init__.py
│   │   └── helper_functions.py   # 不綁定特定代理程式的公用程式函數 (格式、驗證等)
│   ├── sub_agents/               # 子代理程式目錄 (獨立的專門代理程式)
│   │   ├── __init__.py
│   │   ├── sub_agent_1/           # 第一個子代理程式
│   │   │   ├── __init__.py
│   │   │   ├── agent.py          # 使用 LLMAgent 或 ToolCallingAgent 定義 `sub_agent_1` 邏輯
│   │   │   ├── prompts.py        # `sub_agent_1` 專屬的提示
│   │   │   └── tools.py          # 僅由 `sub_agent_1` 使用的工具
│   │   ├── sub_agent_2/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── prompts.py
│   │   │   └── tools.py
│   │   └── sub_agent_n/
│   │       ├── __init__.py
│   │       ├── agent.py
│   │       ├── prompts.py
│   │       └── tools.py 
│   ├── data/                     # 可選的輸入人工因素 (文件、配置等)
│   │   ├── doc1.md
│   │   └── schema.json           # 可選的輸入人工因素 (文件、配置等)
│   ├── deployment/               # 用於 Cloud Build/Agent Engine/Cloud Run 的指令碼、配置
│   │   ├── deploy.py             # AdkApp 設定和部署邏輯
│   │   ├── Dockerfile            # 用於 Cloud Run 部署 (可選)
│   │   └── cloudbuild.yaml       # Cloud Build 步驟 (套件建置 + 部署)
│   ├── eval/                     # 用於 Cloud Build/Agent Engine/Cloud Run 的指令碼、配置
│   │   └── evaluation.py         # 用於評估的指令碼、配置
│   ├── tests/                    # 單元測試和整合測試
│   │   └── test_agent.py         
│   ├── pyproject.toml            # Poetry 配置和依賴項
│   └── README.md                 # 專案說明

```
