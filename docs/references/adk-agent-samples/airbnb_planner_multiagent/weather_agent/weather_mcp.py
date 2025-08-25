import json

from typing import Any

import httpx

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim
from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server
mcp = FastMCP('weather')

# --- Configuration & Constants ---
BASE_URL = 'https://api.weather.gov'
USER_AGENT = 'weather-agent'
REQUEST_TIMEOUT = 20.0
GEOCODE_TIMEOUT = 10.0  # Timeout for geocoding requests

# --- Shared HTTP Client ---
http_client = httpx.AsyncClient(
    base_url=BASE_URL,
    headers={'User-Agent': USER_AGENT, 'Accept': 'application/geo+json'},
    timeout=REQUEST_TIMEOUT,
    follow_redirects=True,
)

# --- Geocoding Setup ---
# Initialize the geocoder (Nominatim requires a unique user_agent)
geolocator = Nominatim(user_agent=USER_AGENT)


async def get_weather_response(endpoint: str) -> dict[str, Any] | None:
    """使用具有錯誤處理的共享客戶端向 NWS API 發出請求。

    Args:
        endpoint: 要請求的端點。

    Returns:
        來自 NWS API 的回應，如果發生錯誤則為 None。
    """
    try:
        response = await http_client.get(endpoint)
        response.raise_for_status()  # 對於 4xx/5xx 回應引發 HTTPStatusError
        return response.json()
    except httpx.HTTPStatusError:
        # 特定的 HTTP 錯誤（例如 404 Not Found、500 Server Error）
        return None
    except httpx.TimeoutException:
        # 請求逾時
        return None
    except httpx.RequestError:
        # 其他請求錯誤（連線、DNS 等）
        return None
    except json.JSONDecodeError:
        # 回應不是有效的 JSON
        return None
    except Exception:
        # 任何其他未預期的錯誤
        return None


def format_alert(feature: dict[str, Any]) -> str:
    """將警報功能格式化為可讀字串。"""
    props = feature.get('properties', {})  # 更安全的存取
    # 使用 .get() 搭配預設值以增強穩健性
    return f"""
            事件：{props.get('event', '未知事件')}
            地區：{props.get('areaDesc', '不適用')}
            嚴重性：{props.get('severity', '不適用')}
            確定性：{props.get('certainty', '不適用')}
            緊急性：{props.get('urgency', '不適用')}
            生效時間：{props.get('effective', '不適用')}
            到期時間：{props.get('expires', '不適用')}
            描述：{props.get('description', '未提供描述。').strip()}
            指示：{props.get('instruction', '未提供指示。').strip()}
            """


def format_forecast_period(period: dict[str, Any]) -> str:
    """將單一預報時段格式化為可讀字串。"""
    return f"""
           {period.get('name', '未知時段')}:
             溫度：{period.get('temperature', '不適用')}°{period.get('temperatureUnit', 'F')}
             風速：{period.get('windSpeed', '不適用')} {period.get('windDirection', '不適用')}
             短期預報：{period.get('shortForecast', '不適用')}
             詳細預報：{period.get('detailedForecast', '未提供詳細預報。').strip()}
           """


# --- MCP Tools ---


@mcp.tool()
async def get_alerts(state: str) -> str:
    """取得特定美國州別的有效天氣警報。

    Args:
        state: 兩個字母的美國州別代碼（例如：CA、NY、TX）。不區分大小寫。
    """
    # 輸入驗證和正規化
    if not isinstance(state, str) or len(state) != 2 or not state.isalpha():
        return '無效輸入。請提供兩個字母的美國州別代碼（例如：CA）。'
    state_code = state.upper()

    endpoint = f'/alerts/active/area/{state_code}'
    data = await get_weather_response(endpoint)

    if data is None:
        # 請求期間發生錯誤
        return f'無法擷取 {state_code} 的天氣警報。'

    features = data.get('features')
    if not features:  # 處理 null 和空列表
        return f'找不到 {state_code} 的有效天氣警報。'

    alerts = [format_alert(feature) for feature in features]
    return '\n---\n'.join(alerts)


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """使用緯度和經度取得特定地點的天氣預報。

    Args:
        latitude: 地點的緯度（例如：34.05）。
        longitude: 地點的經度（例如：-118.25）。
    """
    # 輸入驗證
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return '提供的緯度或經度無效。緯度必須介於 -90 和 90 之間，經度必須介於 -180 和 180 之間。'

    # NWS API 要求緯度、經度格式最多 4 位小數
    point_endpoint = f'/points/{latitude:.4f},{longitude:.4f}'
    points_data = await get_weather_response(point_endpoint)

    if points_data is None or 'properties' not in points_data:
        return f'無法擷取 {latitude:.4f},{longitude:.4f} 的 NWS 網格點資訊。'

    # 從網格點資料中擷取預報 URL
    forecast_url = points_data['properties'].get('forecast')

    if not forecast_url:
        return f'找不到 {latitude:.4f},{longitude:.4f} 的 NWS 預報端點。'

    # 向特定的預報 URL 發出請求
    forecast_data = None
    try:
        response = await http_client.get(forecast_url)
        response.raise_for_status()
        forecast_data = response.json()
    except httpx.HTTPStatusError:
        pass  # 錯誤在下方透過傳回 None 處理
    except httpx.RequestError:
        pass  # 錯誤在下方透過傳回 None 處理
    except json.JSONDecodeError:
        pass  # 錯誤在下方透過傳回 None 處理
    except Exception:
        pass  # 錯誤在下方透過傳回 None 處理

    if forecast_data is None or 'properties' not in forecast_data:
        return '無法從 NWS 擷取詳細的預報資料。'

    periods = forecast_data['properties'].get('periods')
    if not periods:
        return '找不到此地點的 NWS 預報時段。'

    # 格式化前 5 個時段
    forecasts = [format_forecast_period(period) for period in periods[:5]]

    return '\n---\n'.join(forecasts)


# --- 新功能：get_forecast_by_city 工具 ---
@mcp.tool()
async def get_forecast_by_city(city: str, state: str) -> str:
    """透過先尋找特定美國城市和州的座標來取得其天氣預報。

    Args:
        city: 城市名稱（例如："Los Angeles"、"New York"）。
        state: 兩個字母的美國州別代碼（例如：CA、NY）。不區分大小寫。
    """
    # --- 輸入驗證 ---
    if not city or not isinstance(city, str):
        return '提供的城市名稱無效。'
    if (
        not state
        or not isinstance(state, str)
        or len(state) != 2
        or not state.isalpha()
    ):
        return '無效的州別代碼。請提供兩個字母的美國州別縮寫（例如：CA）。'

    city_name = city.strip()
    state_code = state.strip().upper()
    # 建構一個可能產生美國結果的查詢
    query = f'{city_name}, {state_code}, USA'

    # --- 地理編碼 ---
    location = None
    try:
        # 同步地理編碼呼叫
        location = geolocator.geocode(query, timeout=GEOCODE_TIMEOUT)

    except GeocoderTimedOut:
        return f"無法取得 '{city_name}, {state_code}' 的座標：地點服務逾時。"
    except GeocoderServiceError:
        return f"無法取得 '{city_name}, {state_code}' 的座標：地點服務傳回錯誤。"
    except Exception:
        # 捕捉地理編碼期間任何其他未預期的錯誤
        return f"尋找 '{city_name}, {state_code}' 的座標時發生未預期的錯誤。"

    # --- 處理地理編碼結果 ---
    if location is None:
        return f"找不到 '{city_name}, {state_code}' 的座標。請檢查拼寫或嘗試附近的城市。"

    latitude = location.latitude
    longitude = location.longitude

    # --- 使用取得的座標重複使用現有的預報邏輯 ---
    return await get_forecast(latitude, longitude)


# --- Server Execution & Shutdown ---
async def shutdown_event():
    """優雅地關閉 httpx 客戶端。"""
    await http_client.aclose()


if __name__ == '__main__':
    mcp.run(transport='stdio')
