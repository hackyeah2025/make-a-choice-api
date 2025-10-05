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
    options: list[Option]


class EventResponse(BaseModel):
    title: str
    text: str
    options: List[str]
