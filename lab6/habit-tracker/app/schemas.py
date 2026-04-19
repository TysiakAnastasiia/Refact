from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import Optional


class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    color: Optional[str] = Field(default="#6366f1")


class HabitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    color: str


class CheckInOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    habit_id: int
    date: date


class HabitStats(BaseModel):
    habit_id: int
    total_checkins: int
    current_streak: int
    longest_streak: int
    last_checkin: Optional[date]
