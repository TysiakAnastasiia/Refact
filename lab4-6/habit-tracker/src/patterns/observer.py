from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.models.habit_log import HabitLog


#  Observer interface 

class Observer(ABC):
    """
    Observer interface. (ISP: narrow interface with a single update method)
    """

    @abstractmethod
    def update(self, habit_log: HabitLog) -> None:
        """Called when a habit is marked as done."""
        ...


#  Subject mixin 

class Observable:
    """
    Mixin that adds observer management to any class.
    (DIP: depends on Observer abstraction, not concrete classes)
    """

    def __init__(self):
        self._observers: list[Observer] = []

    def add_observer(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer) -> None:
        self._observers = [o for o in self._observers if o is not observer]

    def notify_observers(self, habit_log: HabitLog) -> None:
        for observer in self._observers:
            observer.update(habit_log)


#  Concrete observers 

class NotificationService(Observer):
    """
    Sends a notification when a habit is completed.
    Stores messages for inspection in tests.
    """

    def __init__(self):
        self.messages: list[str] = []

    def update(self, habit_log: HabitLog) -> None:
        msg = (
            f"[NOTIFICATION] Habit {habit_log.habit_id!r} marked "
            f"{habit_log.status.value} on {habit_log.log_date}"
        )
        self.messages.append(msg)

    def last_message(self) -> str | None:
        return self.messages[-1] if self.messages else None


class AnalyticsService(Observer):
    """Tracks how many times each habit has been completed."""

    def __init__(self):
        self.completion_counts: dict[str, int] = {}

    def update(self, habit_log: HabitLog) -> None:
        from src.models.habit_log import LogStatus
        if habit_log.status == LogStatus.COMPLETED:
            self.completion_counts[habit_log.habit_id] = (
                self.completion_counts.get(habit_log.habit_id, 0) + 1
            )

    def get_count(self, habit_id: str) -> int:
        return self.completion_counts.get(habit_id, 0)
