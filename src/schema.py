from enum import Enum
from typing import List

from pydantic import BaseModel


class Consequence(BaseModel):
    impacted: str
    value: int | str


class Option(BaseModel):
    consequences: list[Consequence]


class Stats(BaseModel):
    age: int

    health: int
    relations: int
    happiness: int
    money: int

    income: int
    expenses: int
    savings: int
    ZUS: int

    education: str
    job_experience: int

    job: str
    job_name: str

    has_serious_health_issues: bool

    relationship: str
    children: int


class EventCreate(BaseModel):
    category: str
    options: list[Option]
    stats: Stats


class CoreEventCreate(BaseModel):
    prompt: str
    stats: Stats
    extra_field: str | None = None
    options: list[Option]


class EventResponse(BaseModel):
    title: str
    text: str
    options: List[str]


class EventResponseExtraField(EventResponse):
    extra_field: str

    @staticmethod
    def from_event_response(event_response: EventResponse, extra_field: str = ""):
        return EventResponseExtraField(
            title=event_response.title,
            text=event_response.text,
            options=event_response.options,
            extra_field=extra_field,
        )


class StateElement(BaseModel):
    stats: Stats
    event: dict  # Event object
    choice: dict  # Option object


class SummaryCreate(BaseModel):
    stats: Stats
    history: List[StateElement]
    is_retired: bool
