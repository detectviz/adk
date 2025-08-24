# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
import os

from dotenv import load_dotenv
from fastapi.openapi.models import OAuth2
from fastapi.openapi.models import OAuthFlowAuthorizationCode
from fastapi.openapi.models import OAuthFlows
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.auth.auth_credential import AuthCredential
from google.adk.auth.auth_credential import AuthCredentialTypes
from google.adk.auth.auth_credential import OAuth2Auth
from google.adk.auth.auth_tool import AuthConfig
from google.adk.tools.authenticated_function_tool import AuthenticatedFunctionTool
from google.adk.tools.google_api_tool import CalendarToolset
from google.adk.tools.tool_context import ToolContext
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# 從 .env 檔案載入環境變數
load_dotenv()

# 存取變數
oauth_client_id = os.getenv("OAUTH_CLIENT_ID")
oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET")


SCOPES = ["https://www.googleapis.com/auth/calendar"]

calendar_toolset = CalendarToolset(
    # 您也可以將下面的自訂 `list_calendar_events` 取代為內建的
    # Google 日曆工具，方法是將 `calendar_events_list` 新增至篩選清單中
    client_id=oauth_client_id,
    client_secret=oauth_client_secret,
    tool_filter=["calendar_events_get", "calendar_events_update"],
    tool_name_prefix="google",
)


def list_calendar_events(
    start_time: str,
    end_time: str,
    limit: int,
    tool_context: ToolContext,
    credential: AuthCredential,
) -> list[dict]:
  """搜尋日曆活動。

  範例：

      flights = get_calendar_events(
          calendar_id='joedoe@gmail.com',
          start_time='2024-09-17T06:00:00',
          end_time='2024-09-17T12:00:00',
          limit=10
      )
      # 傳回 2024 年 9 月 17 日上午 6:00 至中午 12:00 之間最多 10 個日曆活動。

  參數：
      calendar_id (str): 要搜尋活動的日曆 ID。
      start_time (str): 時間範圍的開始時間 (格式為
        YYYY-MM-DDTHH:MM:SS)。
      end_time (str): 時間範圍的結束時間 (格式為 YYYY-MM-DDTHH:MM:SS)。
      limit (int): 要傳回的結果數上限。

  傳回：
      list[dict]: 符合搜尋條件的活動清單。
  """

  creds = Credentials(
      token=credential.oauth2.access_token,
      refresh_token=credential.oauth2.refresh_token,
  )

  service = build("calendar", "v3", credentials=creds)
  events_result = (
      service.events()
      .list(
          calendarId="primary",
          timeMin=start_time + "Z" if start_time else None,
          timeMax=end_time + "Z" if end_time else None,
          maxResults=limit,
          singleEvents=True,
          orderBy="startTime",
      )
      .execute()
  )
  events = events_result.get("items", [])
  return events


def update_time(callback_context: CallbackContext):
  # 取得目前日期時間
  now = datetime.now()
  formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
  callback_context.state["_time"] = formatted_time


root_agent = Agent(
    model="gemini-2.0-flash",
    name="calendar_agent",
    instruction="""
      您是一位樂於助人的個人日曆助理。
      使用提供的工具搜尋日曆活動 (如果使用者未指定，則使用 10 作為限制)，並更新它們。
      如果使用者未指定，請使用 "primary" 作為 calendarId。

      情境1：
      使用者想要查詢日曆活動。
      使用 list_calendar_events 搜尋日曆活動。


      情境2：
      使用者想知道其中一個列出的日曆活動的詳細資訊。
      使用 google_calendar_events_get 取得日曆活動的詳細資訊。


      目前使用者：
      <User>
      {userInfo?}
      </User>

      目前時間：{_time}
""",
    tools=[
        AuthenticatedFunctionTool(
            func=list_calendar_events,
            auth_config=AuthConfig(
                auth_scheme=OAuth2(
                    flows=OAuthFlows(
                        authorizationCode=OAuthFlowAuthorizationCode(
                            authorizationUrl=(
                                "https://accounts.google.com/o/oauth2/auth"
                            ),
                            tokenUrl="https://oauth2.googleapis.com/token",
                            scopes={
                                "https://www.googleapis.com/auth/calendar": "",
                            },
                        )
                    )
                ),
                raw_auth_credential=AuthCredential(
                    auth_type=AuthCredentialTypes.OAUTH2,
                    oauth2=OAuth2Auth(
                        client_id=oauth_client_id,
                        client_secret=oauth_client_secret,
                    ),
                ),
            ),
        ),
        calendar_toolset,
    ],
    before_agent_callback=update_time,
)
