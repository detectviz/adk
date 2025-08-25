from google.adk.auth import AuthConfig
from google.adk.events import Event
import asyncio

# --- 輔助函式 ---
async def get_user_input(prompt: str) -> str:
  """
  在主控台中非同步提示使用者輸入。

  使用 asyncio 的事件迴圈和 run_in_executor，以避免在等待同步的 `input()`
  時阻塞主非同步執行緒。

  Args:
    prompt: 要向使用者顯示的訊息。

  Returns:
    使用者輸入的字串。
  """
  loop = asyncio.get_event_loop()
  # 在由執行器管理的獨立執行緒中執行阻塞的 `input()` 函式。
  return await loop.run_in_executor(None, input, prompt)


def is_pending_auth_event(event: Event) -> bool:
  """
  檢查一個 ADK 事件是否代表使用者驗證憑證的請求。

  當工具需要先前未滿足的驗證時，ADK 框架會發出一個特定的函式呼叫
  ('adk_request_credential')。

  Args:
    event: 要檢查的 ADK 事件物件。

  Returns:
    如果事件是 'adk_request_credential' 函式呼叫，則為 True，否則為 False。
  """
  # 安全地檢查巢狀屬性以避免在事件結構不完整時發生錯誤。
  return (
      event.content
      and event.content.parts
      and event.content.parts[0] # 假設函式呼叫在第一個部分
      and event.content.parts[0].function_call
      # 表示來自 ADK 框架的驗證請求的特定函式名稱。
      and event.content.parts[0].function_call.name == 'adk_request_credential'
  )


def get_function_call_id(event: Event) -> str:
  """
  從 ADK 事件中提取函式呼叫的唯一 ID。

  此 ID 對於將函式*回應*關聯回代理為請求驗證憑證而發起的
  特定函式*呼叫*至關重要。

  Args:
    event: 包含函式呼叫的 ADK 事件物件。

  Returns:
    函式呼叫的唯一識別碼字串。

  Raises:
    ValueError: 如果在事件結構中找不到函式呼叫 ID。
                （下方已更正錯字 `contents` 為 `content`）
  """
  # 遍覽事件結構以尋找函式呼叫 ID。
  if (
      event
      and event.content
      and event.content.parts
      and event.content.parts[0] # 使用 content，而非 contents
      and event.content.parts[0].function_call
      and event.content.parts[0].function_call.id
  ):
    return event.content.parts[0].function_call.id
  # 如果缺少 ID，則引發錯誤，表示事件格式不符預期。
  raise ValueError(f'無法從事件 {event} 中取得函式呼叫 ID')


def get_function_call_auth_config(event: Event) -> AuthConfig:
  """
  從 'adk_request_credential' 事件中提取驗證設定詳細資訊。

  用戶端應使用此 AuthConfig 來取得必要的驗證詳細資訊（如 OAuth 授權碼和狀態）
  並將其傳回 ADK 以繼續 OAuth 權杖交換。

  Args:
    event: 包含 'adk_request_credential' 呼叫的 ADK 事件物件。

  Returns:
    一個 AuthConfig 物件，其中填入了函式呼叫參數中的詳細資訊。

  Raises:
    ValueError: 如果在事件中找不到 'auth_config' 參數。
                （下方已更正錯字 `contents` 為 `content`）
  """
  if (
      event
      and event.content
      and event.content.parts
      and event.content.parts[0] # 使用 content，而非 contents
      and event.content.parts[0].function_call
      and event.content.parts[0].function_call.args
      and event.content.parts[0].function_call.args.get('auth_config')
  ):
    # 使用參數中提供的字典重建 AuthConfig 物件。
    # ** 運算子將字典解包為建構函式的關鍵字參數。
    return AuthConfig(
          **event.content.parts[0].function_call.args.get('auth_config')
      )
  raise ValueError(f'無法從事件 {event} 中取得驗證設定')
