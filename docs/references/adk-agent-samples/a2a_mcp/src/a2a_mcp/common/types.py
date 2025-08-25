# type: ignore

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ServerConfig(BaseModel):
    """伺服器組態。"""

    host: str
    port: int
    transport: str
    url: str


class PlannerTask(BaseModel):
    """代表由規劃器產生的單一任務。"""

    id: int = Field(description='任務的序列 ID。')
    description: str = Field(
        description='要執行之任務的清晰描述。'
    )
    status: (
        Any
        | Literal[
            'input_required',
            'completed',
            'error',
            'pending',
            'incomplete',
            'todo',
            'not_started',
        ]
        | None
    ) = Field(description='任務的狀態', default='input_required')


class TripInfo(BaseModel):
    """行程資訊。"""

    total_budget: str | None = Field(description='旅程總預算')
    origin: str | None = Field(description='旅程出發地')
    destination: str | None = Field(description='旅程目的地')
    type: str | None = Field(description='旅程類型，商務或休閒')
    start_date: str | None = Field(description='旅程開始日期')
    end_date: str | None = Field(description='旅程結束日期')
    travel_class: str | None = Field(
        description='旅行艙等，頭等、商務或經濟艙'
    )
    accommodation_type: str | None = Field(
        description='豪華飯店、經濟型飯店、AirBnB 等'
    )
    room_type: str | None = Field(description='套房、單人房、雙人房等')
    is_car_rental_required: str | None = Field(
        description='旅程中是否需要租車。'
    )
    type_of_car: str | None = Field(
        description='汽車類型，SUV、轎車、卡車等'
    )
    no_of_travellers: str | None = Field(
        description='旅程中的總旅客人數'
    )

    checkin_date: str | None = Field(description='飯店入住日期')
    checkout_date: str | None = Field(description='飯店退房日期')
    car_rental_start_date: str | None = Field(
        description='租車開始日期'
    )
    car_rental_end_date: str | None = Field(description='租車結束日期')

    @model_validator(mode='before')
    @classmethod
    def set_dependent_var(cls, values):
        """Pydantic 相依設定器。"""
        if isinstance(values, dict) and 'start_date' in values:
            values['checkin_date'] = values['start_date']

        if isinstance(values, dict) and 'end_date' in values:
            values['checkout_date'] = values['end_date']

        if isinstance(values, dict) and 'start_date' in values:
            values['car_rental_start_date'] = values['start_date']

        if isinstance(values, dict) and 'end_date' in values:
            values['car_rental_end_date'] = values['end_date']
        return values


class TaskList(BaseModel):
    """規劃器代理的輸出結構。"""

    original_query: str | None = Field(
        description='用於上下文的原始使用者查詢。'
    )

    trip_info: TripInfo | None = Field(description='行程資訊')

    tasks: list[PlannerTask] = Field(
        description='要循序執行的任務清單。'
    )


class AgentResponse(BaseModel):
    """代理的輸出結構。"""

    content: str | dict = Field(description='回應的內容。')
    is_task_complete: bool = Field(description='任務是否完成。')
    require_user_input: bool = Field(
        description='代理是否需要使用者輸入。'
    )
