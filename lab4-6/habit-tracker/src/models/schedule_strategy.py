from abc import ABC, abstractmethod
from datetime import date
from typing import List


class ScheduleStrategy(ABC):
    """Abstract strategy for habit scheduling (Strategy Pattern)."""
    
    @abstractmethod
    def is_due(self, check_date: date) -> bool:
        """Check if habit is due on the given date."""
        pass
    
    @abstractmethod
    def description(self) -> str:
        """Return description of the schedule."""
        pass


class DailyScheduleStrategy(ScheduleStrategy):
    """Strategy for daily habits."""
    
    def is_due(self, check_date: date) -> bool:
        return True  # Daily habits are always due
    
    def description(self) -> str:
        return "Daily"


class WeeklyScheduleStrategy(ScheduleStrategy):
    """Strategy for weekly habits on specific weekdays."""
    
    def __init__(self, weekdays: List[int]):
        """
        Args:
            weekdays: List of weekdays (0=Monday, 6=Sunday)
        """
        for day in weekdays:
            if not 0 <= day <= 6:
                raise ValueError("Invalid weekday")
        self.weekdays = weekdays
    
    def is_due(self, check_date: date) -> bool:
        return check_date.weekday() in self.weekdays
    
    def description(self) -> str:
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        days = [day_names[day] for day in self.weekdays]
        return f"Weekly on {', '.join(days)}"


class CustomScheduleStrategy(ScheduleStrategy):
    """Strategy for custom dates."""
    
    def __init__(self, dates: List[date]):
        self.dates = dates
    
    def is_due(self, check_date: date) -> bool:
        return check_date in self.dates
    
    def description(self) -> str:
        return f"Custom on {len(self.dates)} dates"
