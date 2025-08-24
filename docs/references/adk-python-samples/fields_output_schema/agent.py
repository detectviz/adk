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

from google.adk import Agent
from pydantic import BaseModel


class WeahterData(BaseModel):
  temperature: str
  humidity: str
  wind_speed: str


root_agent = Agent(
    name='root_agent',
    model='gemini-2.0-flash',
    instruction="""\
根據您擁有的資料回答使用者的問題。

如果您沒有資料，可以直接說不知道。

以下是您擁有的聖荷西 (San Jose) 資料

*   溫度 (temperature): 26 C
*   濕度 (humidity): 20%
*   風速 (wind_speed): 29 mph

以下是您擁有的庫比蒂諾 (Cupertino) 資料

*   溫度 (temperature): 16 C
*   濕度 (humidity): 10%
*   風速 (wind_speed): 13 mph

""",
    output_schema=WeahterData,
    output_key='weather_data',
)
