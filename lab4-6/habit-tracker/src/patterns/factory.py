from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from src.models.habit import Habit, DailyHabit, WeeklyHabit
from src.models.schedule_strategy import CustomScheduleStrategy


class HabitFactory(ABC):
    """
    Abstract Factory interface for creating Habit objects.
    (OCP: new habit types require a new factory, not changes to existing ones)
    """

    @abstractmethod
    def create_habit(self, title: str, description: str, user_id: str, **kwargs) -> Habit:
        ...


class ConcreteHabitFactory(HabitFactory):
    """
    Creates habits based on a `habit_type` string.
    Supported types: 'daily', 'weekly', 'custom'
    """

    def create_habit(self, title: str, description: str, user_id: str, **kwargs) -> Habit:
        habit_type: str = kwargs.get("habit_type", "daily").lower()

        if habit_type == "daily":
            return DailyHabit(title=title, description=description, user_id=user_id)

        elif habit_type == "weekly":
            weekdays: list[int] = kwargs.get("weekdays", [0, 2, 4])  # Mon, Wed, Fri default
            return WeeklyHabit(
                title=title, description=description, user_id=user_id, weekdays=weekdays
            )

        elif habit_type == "custom":
            dates: list[date] = kwargs.get("dates", [])
            if not dates:
                raise ValueError("'custom' habit type requires a non-empty 'dates' list")
            from src.models.habit import Habit
            # Inline lightweight custom habit
            strategy = CustomScheduleStrategy(dates)

            class _CustomHabit(Habit):
                @property
                def habit_type(self) -> str:
                    return "custom"

            return _CustomHabit(
                title=title,
                description=description,
                schedule_strategy=strategy,
                user_id=user_id,
            )

        else:
            raise ValueError(f"Unknown habit type: {habit_type!r}")
