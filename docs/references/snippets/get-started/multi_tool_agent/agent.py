import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

def get_weather(city: str) -> dict:
    """擷取指定城市的目前天氣報告。

    Args:
        city (str): 要擷取天氣報告的城市名稱。

    Returns:
        dict: 狀態和結果或錯誤訊息。
    """
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "紐約天氣晴朗，溫度為攝氏 25 度（華氏 77 度）。"
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"'{city}' 的天氣資訊不可用。",
        }


def get_current_time(city: str) -> dict:
    """返回指定城市的目前時間。

    Args:
        city (str): 要擷取目前時間的城市名稱。

    Returns:
        dict: 狀態和結果或錯誤訊息。
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"抱歉，我沒有 {city} 的時區資訊。"
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'{city} 的目前時間是 {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "回答有關城市時間和天氣問題的代理。"
    ),
    instruction=(
        "您是一個樂於助人的代理，可以回答使用者關於城市時間和天氣的問題。"
    ),
    tools=[get_weather, get_current_time],
)
