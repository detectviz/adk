import asyncio
from dotenv import load_dotenv
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .helpers import is_pending_auth_event, get_function_call_id, get_function_call_auth_config, get_user_input
from .tools_and_agent import root_agent

load_dotenv()

agent = root_agent

async def async_main():
  """
  主非同步函式，協調代理互動和驗證流程。
  """
  # --- 步驟 1：服務初始化 ---
  # 使用記憶體內服務進行會話和產物儲存（適用於示範/測試）。
  session_service = InMemorySessionService()
  artifacts_service = InMemoryArtifactService()

  # 建立一個新的使用者會話以維護對話狀態。
  session = session_service.create_session(
      state={},  # 用於會話特定資料的選用狀態字典
      app_name='my_app', # 應用程式識別碼
      user_id='user' # 使用者識別碼
  )

  # --- 步驟 2：初始使用者查詢 ---
  # 定義使用者的初始請求。
  query = '顯示我的使用者資訊'
  print(f"使用者: {query}")

  # 將查詢格式化為 ADK Runner 預期的 Content 結構。
  content = types.Content(role='user', parts=[types.Part(text=query)])

  # 初始化 ADK Runner
  runner = Runner(
      app_name='my_app',
      agent=agent,
      artifact_service=artifacts_service,
      session_service=session_service,
  )

  # --- 步驟 3：傳送查詢並處理潛在的驗證請求 ---
  print("\n正在使用初始查詢執行代理...")
  events_async = runner.run_async(
      session_id=session.id, user_id='user', new_message=content
  )

  # 用於儲存驗證請求發生時的詳細資訊的變數。
  auth_request_event_id, auth_config = None, None

  # 迭代第一次執行產生的事件。
  async for event in events_async:
    # 檢查此事件是否為特定的 'adk_request_credential' 函式呼叫。
    if is_pending_auth_event(event):
      print("--> 代理需要驗證。")
      auth_request_event_id = get_function_call_id(event)
      auth_config = get_function_call_auth_config(event)
      # 找到並處理驗證請求後，退出此迴圈。
      # 我們需要在此暫停執行以取得使用者的驗證輸入。
      break


  # 如果處理完所有事件後未偵測到驗證請求，則退出。
  if not auth_request_event_id or not auth_config:
      print("\n此查詢不需要驗證或處理已完成。")
      return # 退出主函式

  # --- 步驟 4：手動驗證步驟（模擬 OAuth 2.0 流程）---
  # 本節模擬 OAuth 2.0 流程的使用者互動部分。
  # 在真實的 Web 應用程式中，這將涉及瀏覽器重新導向。

  # 定義重新導向 URI。這*必須*與為您的應用程式註冊的
  # OAuth 提供者處的其中一個 URI 相符。在使用者核准請求後，提供者會將使用者
  # 送回此處。
  redirect_uri = 'http://localhost:8000/dev-ui' # 本地開發範例

  # 建構使用者必須造訪的授權 URL。
  # 這通常包括提供者的授權端點 URL、
  # 用戶端 ID、請求的範圍、回應類型（例如 'code'）和重新導向 URI。
  # 在此，我們從 ADK 提供的 AuthConfig 中擷取基礎授權 URI
  # 並附加 redirect_uri。
  # 注意：穩健的實作會使用 urlencode 並可能新增 state、scope 等。
  auth_request_uri = (
      auth_config.exchanged_auth_credential.oauth2.auth_uri
      + f'&redirect_uri={redirect_uri}' # 簡單串接；請確保查詢參數格式正確
  )

  print("\n--- 需要使用者操作 ---")
  # 提示使用者造訪授權 URL、登入、授予權限，
  # 然後貼上他們被重新導向回的*完整* URL（其中包含授權碼）。
  auth_response_uri = await get_user_input(
      f'1. 請在瀏覽器中開啟此 URL 以登入：\n   {auth_request_uri}\n\n'
      f'2. 成功登入和授權後，您的瀏覽器將被重新導向。\n'
      f'   請從瀏覽器的網址列複製*整個* URL。\n\n'
      f'3. 在此處貼上複製的 URL 並按 Enter：\n\n> '
  )

  # --- 步驟 5：為代理準備驗證回應 ---
  # 使用從使用者收集的資訊更新 AuthConfig 物件。
  # ADK 框架需要完整的 回應 URI（包含授權碼）
  # 和原始的重新導向 URI，以在內部完成 OAuth 權杖交換過程。
  auth_config.exchanged_auth_credential.oauth2.auth_response_uri = auth_response_uri
  auth_config.exchanged_auth_credential.oauth2.redirect_uri = redirect_uri

  # 建構一個 FunctionResponse Content 物件以傳回給代理/執行器。
  # 此回應明確地針對先前由其 ID 識別的 'adk_request_credential' 函式呼叫。
  auth_content = types.Content(
      role='user',
      parts=[
          types.Part(
              function_response=types.FunctionResponse(
                  # 至關重要，使用儲存的 ID 將此回應連結到原始請求。
                  id=auth_request_event_id,
                  # 我們正在回應的函式呼叫的特殊名稱。
                  name='adk_request_credential',
                  # 包含所有必要驗證詳細資訊的酬載。
                  response=auth_config.model_dump(),
              )
          )
      ],
  )

  # --- 步驟 6：使用驗證繼續執行 ---
  print("\n正在將驗證詳細資訊提交回代理...")
  # 再次執行代理，這次提供 `auth_content` (FunctionResponse)。
  # ADK Runner 會攔截此訊息，處理 'adk_request_credential' 回應
  # （執行權杖交換、儲存憑證），然後允許代理
  # 重試需要驗證的原始工具呼叫，現在使用
  # 嵌入的有效存取權杖成功執行。
  events_async = runner.run_async(
      session_id=session.id,
      user_id='user',
      new_message=auth_content, # 提供準備好的驗證回應
  )

  # 在驗證完成後處理並印出代理的最終事件。
  # 此串流現在包含工具的實際結果（例如，使用者資訊）。
  print("\n--- 驗證後的代理回應 ---")
  async for event in events_async:
    print(event)


if __name__ == '__main__':
  asyncio.run(async_main())
