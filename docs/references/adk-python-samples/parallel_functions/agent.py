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

"""用於測試平行函式呼叫的範例代理。"""

import asyncio
import time
from typing import List

from google.adk import Agent
from google.adk.tools.tool_context import ToolContext


async def get_weather(city: str, tool_context: ToolContext) -> dict:
  """取得城市的目前天氣。

  Args:
    city: 要取得天氣的城市名稱。

  Returns:
    包含天氣資訊的字典。
  """
  # 模擬一些非同步處理時間（非阻塞）
  await asyncio.sleep(2)

  # 模擬天氣資料
  weather_data = {
      'New York': {'temp': 72, 'condition': 'sunny', 'humidity': 45},
      'London': {'temp': 60, 'condition': 'cloudy', 'humidity': 80},
      'Tokyo': {'temp': 68, 'condition': 'rainy', 'humidity': 90},
      'San Francisco': {'temp': 65, 'condition': 'foggy', 'humidity': 85},
      'Paris': {'temp': 58, 'condition': 'overcast', 'humidity': 70},
      'Sydney': {'temp': 75, 'condition': 'sunny', 'humidity': 60},
  }

  result = weather_data.get(
      city,
      {
          'temp': 70,
          'condition': 'unknown',
          'humidity': 50,
          'note': (
          f'沒有 {city} 的天氣資料，顯示預設值'
          ),
      },
  )

# 儲存於上下文中以測試執行緒安全
  if 'weather_requests' not in tool_context.state:
    tool_context.state['weather_requests'] = []
  tool_context.state['weather_requests'].append(
      {'city': city, 'timestamp': time.time(), 'result': result}
  )

  return {
      'city': city,
      'temperature': result['temp'],
      'condition': result['condition'],
      'humidity': result['humidity'],
      **({'note': result['note']} if 'note' in result else {}),
  }


async def get_currency_rate(
    from_currency: str, to_currency: str, tool_context: ToolContext
) -> dict:
  """取得兩種貨幣之間的匯率。

  Args:
    from_currency: 來源貨幣代碼（例如 'USD'）。
    to_currency: 目標貨幣代碼（例如 'EUR'）。

  Returns:
    包含匯率資訊的字典。
  """
  # 模擬非同步處理時間
  await asyncio.sleep(1.5)

  # 模擬匯率
  rates = {
      ('USD', 'EUR'): 0.85,
      ('USD', 'GBP'): 0.75,
      ('USD', 'JPY'): 110.0,
      ('EUR', 'USD'): 1.18,
      ('EUR', 'GBP'): 0.88,
      ('GBP', 'USD'): 1.33,
      ('GBP', 'EUR'): 1.14,
      ('JPY', 'USD'): 0.009,
  }

  rate = rates.get((from_currency, to_currency), 1.0)

  # 儲存於上下文中以測試執行緒安全
  if 'currency_requests' not in tool_context.state:
    tool_context.state['currency_requests'] = []
  tool_context.state['currency_requests'].append({
      'from': from_currency,
      'to': to_currency,
      'rate': rate,
      'timestamp': time.time(),
  })

  return {
      'from_currency': from_currency,
      'to_currency': to_currency,
      'exchange_rate': rate,
      'timestamp': time.time(),
  }


async def calculate_distance(
    city1: str, city2: str, tool_context: ToolContext
) -> dict:
  """計算兩個城市之間的距離。

  Args:
    city1: 第一個城市。
    city2: 第二個城市。

  Returns:
    包含距離資訊的字典。
  """
  # 模擬非同步處理時間（非阻塞）
  await asyncio.sleep(1)

  # 模擬距離（公里）
  city_coords = {
      'New York': (40.7128, -74.0060),
      'London': (51.5074, -0.1278),
      'Tokyo': (35.6762, 139.6503),
      'San Francisco': (37.7749, -122.4194),
      'Paris': (48.8566, 2.3522),
      'Sydney': (-33.8688, 151.2093),
  }

  # 簡單距離計算（模擬）
  if city1 in city_coords and city2 in city_coords:
    coord1 = city_coords[city1]
    coord2 = city_coords[city2]
    # 簡化距離計算
    distance = int(
        ((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2) ** 0.5
        * 111
    )  # 大約公里轉換
  else:
    distance = 5000  # 預設距離

  # 儲存於上下文中以測試執行緒安全
  if 'distance_requests' not in tool_context.state:
    tool_context.state['distance_requests'] = []
  tool_context.state['distance_requests'].append({
      'city1': city1,
      'city2': city2,
      'distance': distance,
      'timestamp': time.time(),
  })

  return {
      'city1': city1,
      'city2': city2,
      'distance_km': distance,
      'distance_miles': int(distance * 0.621371),
  }


async def get_population(cities: List[str], tool_context: ToolContext) -> dict:
  """取得多個城市的人口資訊。

  Args:
    cities: 城市名稱清單。

  Returns:
    包含每個城市人口資料的字典。
  """
  # 模擬與城市數量成正比的非同步處理時間（非阻塞）
  await asyncio.sleep(len(cities) * 0.5)

  # 模擬人口資料
  populations = {
      'New York': 8336817,
      'London': 9648110,
      'Tokyo': 13960000,
      'San Francisco': 873965,
      'Paris': 2161000,
      'Sydney': 5312163,
  }

  results = {}
  for city in cities:
    results[city] = populations.get(city, 1000000)  # 如果找不到，預設為 100 萬

  # 儲存於上下文中以測試執行緒安全
  if 'population_requests' not in tool_context.state:
    tool_context.state['population_requests'] = []
  tool_context.state['population_requests'].append(
      {'cities': cities, 'results': results, 'timestamp': time.time()}
  )

  return {
      'populations': results,
      'total_population': sum(results.values()),
      'cities_count': len(cities),
  }


root_agent = Agent(
    model='gemini-2.0-flash',
    name='parallel_function_test_agent',
    description=(
        '用於測試平行函式呼叫效能和執行緒'
        '安全的代理。'
    ),
    instruction="""
    您是一位樂於助人的助理，可以提供有關天氣、匯率、城市間距離和人口資料的資訊。您可以存取多個工具，並應有效率地使用它們。
    
    當使用者詢問有關多個城市或多種類型資料的資訊時，您應該平行呼叫多個函式以提供更快的​​回應。
    
    例如：
    - 如果被問及多個城市的天氣，請平行呼叫每個城市的 get_weather
    - 如果被問及天氣和匯率，請平行呼叫這兩個函式
    - 如果被要求比較城市，您可能需要平行取得天氣、人口和距離資料
    
    務必力求高效率，並在可能的情況下同時呼叫多個函式。
    提供資訊豐富、清晰、結構良好的回應。
  """,
    tools=[
        get_weather,
        get_currency_rate,
        calculate_distance,
        get_population,
    ],
)
