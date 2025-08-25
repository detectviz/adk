import asyncio

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.tools import VertexAiSearchTool

# 請替換為您實際的 Vertex AI Search Datastore ID
# 格式：projects/<PROJECT_ID>/locations/<LOCATION>/collections/default_collection/dataStores/<DATASTORE_ID>
# 例如："projects/12345/locations/us-central1/collections/default_collection/dataStores/my-datastore-123"
YOUR_DATASTORE_ID = "請在此處替換為您的資料儲存庫 ID"

# 常數
APP_NAME_VSEARCH = "vertex_search_app"
USER_ID_VSEARCH = "user_vsearch_1"
SESSION_ID_VSEARCH = "session_vsearch_1"
AGENT_NAME_VSEARCH = "doc_qa_agent"
GEMINI_2_FLASH = "gemini-2.0-flash"

# 工具實例化
# 您必須在此處提供您的資料儲存庫 ID。
vertex_search_tool = VertexAiSearchTool(data_store_id=YOUR_DATASTORE_ID)

# 代理定義
doc_qa_agent = LlmAgent(
    name=AGENT_NAME_VSEARCH,
    model=GEMINI_2_FLASH, # 需要 Gemini 模型
    tools=[vertex_search_tool],
    instruction=f"""您是一位有幫助的助理，根據在文件儲存庫中找到的資訊回答問題：{YOUR_DATASTORE_ID}。
    在回答之前，請使用搜尋工具尋找相關資訊。
    如果答案不在文件中，請說明找不到資訊。
    """,
    description="使用特定的 Vertex AI Search 資料儲存庫回答問題。",
)

# 會話和執行器設定
session_service_vsearch = InMemorySessionService()
runner_vsearch = Runner(
    agent=doc_qa_agent, app_name=APP_NAME_VSEARCH, session_service=session_service_vsearch
)
session_vsearch = session_service_vsearch.create_session(
    app_name=APP_NAME_VSEARCH, user_id=USER_ID_VSEARCH, session_id=SESSION_ID_VSEARCH
)

# 代理互動函式
async def call_vsearch_agent_async(query):
    print("\n--- 正在執行 Vertex AI Search 代理 ---")
    print(f"查詢：{query}")
    if "YOUR_DATASTORE_ID_HERE" in YOUR_DATASTORE_ID:
        print("正在跳過執行：請將 YOUR_DATASTORE_ID_HERE 替換為您實際的資料儲存庫 ID。")
        print("-" * 30)
        return

    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "未收到回應。"
    try:
        async for event in runner_vsearch.run_async(
            user_id=USER_ID_VSEARCH, session_id=SESSION_ID_VSEARCH, new_message=content
        ):
            # 與 Google 搜尋類似，結果通常嵌入在模型的回應中。
            if event.is_final_response() and event.content and event.content.parts:
                final_response_text = event.content.parts[0].text.strip()
                print(f"代理回應：{final_response_text}")
                # 您可以檢查 event.grounding_metadata 以取得來源引文
                if event.grounding_metadata:
                    print(f"  (找到包含 {len(event.grounding_metadata.grounding_attributions)} 個引文的基礎資料中繼資料)")

    except Exception as e:
        print(f"發生錯誤：{e}")
        print("請確保您的資料儲存庫 ID 正確，且服務帳戶具有權限。")
    print("-" * 30)

# --- 執行範例 ---
async def run_vsearch_example():
    # 請替換為與您的資料儲存庫內容相關的問題
    await call_vsearch_agent_async("總結關於第二季度策略文件的要點。")
    await call_vsearch_agent_async("實驗室 X 提到了哪些安全程序？")

# 執行範例
# await run_vsearch_example()

# 由於多個 await 可能導致 colab asyncio 問題，因此在本地執行
try:
    asyncio.run(run_vsearch_example())
except RuntimeError as e:
    if "cannot be called from a running event loop" in str(e):
        print("正在執行的事件迴圈中跳過執行（如 Colab/Jupyter）。請在本地執行。")
    else:
        raise e
