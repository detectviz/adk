# Google ADK Samples 繁體中文化文檔

- 進度：❌ 未翻譯 ✅ 已翻譯 ⚠️ 翻譯有問題，需人工校對
- [翻譯規範](#翻譯規範)：請你將目錄下的所有檔案進行完整的繁體中文化處理，翻譯完成後標記 ✅，遇到問題請先跳過，標記 ⚠️，最後再進行人工校對。


## [Agent 範例](adk-samples-agents)： 

```bash
├── ✅ README.md
├── ✅ a2a_mcp
├── ✅ a2a_telemetry
├── ❌ a2a-mcp-without-framework
├── ✅ academic-research/
├── ❌ adk_cloud_run
├── ❌ adk_expense_reimbursement
├── ❌ adk_facts
├── ❌ ag2
├── ❌ airbnb_planner_multiagent
├── ❌ analytics
├── ❌ any_agent_adversarial_multiagent
├── ✅ auto-insurance-agent/
├── ❌ azureaifoundry_sdk
├── ❌ beeai-chat
├── ❌ birthday_planner_adk
├── ✅ brand-search-optimization/
├── ✅ camel/
├── ❌ content_planner
├── ❌ crewai
├── ❌ customer-service
├── ✅ data-science/
├── ❌ dice_agent_grpc/
├── ❌ dice_agent_rest/
├── ✅ financial-advisor/
├── ✅ fomc-research
├── ✅ gemini-fullstack
├── ❌ github-agent
├── ❌ google-adk-workflows
├── ❌ headless_agent_auth
├── ❌ helloworld
├── ❌ image-scoring
├── ❌ langgraph
├── ❌ llama_index_file_chat
├── ❌ llm-auditor
├── ✅ machine-learning-engineering
├── ❌ marketing-agency
├── ❌ marvin
├── ❌ mindsdb
├── ❌ number_guessing_game
├── ❌ personal-expense-assistant-adk
├── ❌ personalized-shopping
├── ❌ purchasing-concierge-intro-a2a
├── ❌ qa-test-planner-agent
├── ❌ RAG
├── ❌ semantickernel
├── ✅ software-bug-assistant
├── ❌ sre-bot
├── ❌ travel_planner_agent
├── ❌ travel-concierge
└── ❌ veo_video_gen
```

## 翻譯規範

1. **程式碼註解**：將原本的英文註解翻譯成繁體中文，並在必要時補充更清楚的中文解釋，特別是對於函式用途、主要邏輯和重要變數的說明。

2. **補充說明**：翻譯過程中，如果發現任何程式碼缺少足夠的說明，請主動添加繁體中文註解，以幫助使用者更好地理解範例的用法和內部邏輯。

3. **提示詞內容**：將文字提示（prompts）、說明檔案中的指令或描述，全部翻譯成繁體中文。

4. **專有名詞處理**：遇到專有名詞或框架名稱時，請保留英文。例如：
    - 「Multi Agent」要翻譯為「多代理 (Multi Agent)」 
    - 「Context Manager」要翻譯為「上下文管理 (Context Manager)」

5. **禁止翻譯的內容**：
    - **URL 連結**：所有 http://、https:// 開頭的連結必須完整保留，不得翻譯。        
    - **程式碼本體**：程式邏輯、函式名稱、變數名稱、import、class、語法結構一律保留英文，僅翻譯註解與自然語言。
    - **檔案/目錄名稱**：保留原始英文名稱。

6. **翻譯後的品質檢查**：完成翻譯後，再次逐檔檢查，確認所有文字、註解與提示詞內容皆已繁體中文化，避免殘留英文敘述（但遵守禁止翻譯的規則）。