from abc import ABC, abstractmethod
from datetime import date


class ScheduleStrategy(ABC):
    """
    Strategy interface for determining when a habit should be performed.
    (OCP: new schedule types added without modifying Habit class)
    """

    @abstractmethod
    def is_due(self, check_date: date) -> bool:
        """Return True if the habit is due on the given date."""
        ...

    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the schedule."""
        ...


class DailyScheduleStrategy(ScheduleStrategy):
    """Habit is due every day."""

    def is_due(self, check_date: date) -> bool:
        return True

    def description(self) -> str:
        return "daily"


class WeeklyScheduleStrategy(ScheduleStrategy):
    """
    Habit is due on specific days of the week.
    weekdays: list of integers 0=Monday … 6=Sunday
    """

    def __init__(self, weekdays: list[int]):
        if not weekdays:
            raise ValueError("weekdays list cannot be empty")
        invalid = [d for d in weekdays if d not in range(7)]
        if invalid:
            raise ValueError(f"Invalid weekday values: {invalid}")
        self._weekdays = weekdays

    def is_due(self, check_date: date) -> bool:
        return check_date.weekday() in self._weekdays

    def description(self) -> str:
        names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        days = ", ".join(names[d] for d in sorted(self._weekdays))
        return f"weekly on {days}"


class CustomScheduleStrategy(ScheduleStrategy):
    """Habit is due on an explicitly provided list of dates."""

    def __init__(self, dates: list[date]):
        self._dates = set(dates)

    def is_due(self, check_date: date) -> bool:
        return check_date in self._dates

    def description(self) -> str:
        return f"custom ({len(self._dates)} date(s))"
