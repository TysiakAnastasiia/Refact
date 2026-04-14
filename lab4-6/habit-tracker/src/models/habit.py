from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import uuid

from src.models.schedule_strategy import ScheduleStrategy, DailyScheduleStrategy, WeeklyScheduleStrategy


class Habit(ABC):
    """
    Abstract base class for a habit. (SRP: describes a habit and delegates schedule logic)
    Subclasses must implement `habit_type`.
    """

    def __init__(
        self,
        title: str,
        description: str,
        schedule_strategy: ScheduleStrategy,
        user_id: str,
        habit_id: Optional[str] = None,
    ):
        if not title or not title.strip():
            raise ValueError("Habit title cannot be empty")
        self.id: str = habit_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.schedule_strategy = schedule_strategy
        self.user_id = user_id

    def is_due(self, check_date: date) -> bool:
        """Delegates schedule check to the strategy. (DIP: depends on abstraction)"""
        return self.schedule_strategy.is_due(check_date)

    @property
    @abstractmethod
    def habit_type(self) -> str:
        """Return a string identifier for the habit type."""
        ...

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(id={self.id!r}, title={self.title!r}, "
            f"schedule={self.schedule_strategy.description()!r})"
        )


class DailyHabit(Habit):
    """A habit that should be performed every day."""

    def __init__(self, title: str, description: str, user_id: str, habit_id: Optional[str] = None):
        super().__init__(title, description, DailyScheduleStrategy(), user_id, habit_id)

    @property
    def habit_type(self) -> str:
        return "daily"


class WeeklyHabit(Habit):
    """A habit that should be performed on specific days of the week."""

    def __init__(
        self,
        title: str,
        description: str,
        user_id: str,
        weekdays: list[int],
        habit_id: Optional[str] = None,
    ):
        super().__init__(title, description, WeeklyScheduleStrategy(weekdays), user_id, habit_id)

    @property
    def habit_type(self) -> str:
        return "weekly"
