from datetime import date
from typing import Optional

from src.models.habit import Habit
from src.models.habit_log import HabitLog
from src.models.user import User
from src.patterns.factory import ConcreteHabitFactory
from src.patterns.observer import NotificationService, AnalyticsService
from src.repositories.repositories import HabitRepository, UserRepository, HabitLogRepository
from src.services.habit_tracker import HabitTracker
from src.services.reward_service import RewardService


class HabitServiceFacade:
    """
    Facade that exposes a simplified API to the outside world.
    Hides wiring of factories, repositories, observers, and tracker.
    (Facade pattern — single point of entry; OCP — internals can change freely)
    """

    def __init__(self):
        self._habit_repo = HabitRepository()
        self._user_repo = UserRepository()
        self._log_repo = HabitLogRepository()

        self._factory = ConcreteHabitFactory()

        self._tracker = HabitTracker(self._habit_repo, self._log_repo)

        self.notification_service = NotificationService()
        self.analytics_service = AnalyticsService()
        self.reward_service = RewardService()

        self._tracker.add_observer(self.notification_service)
        self._tracker.add_observer(self.analytics_service)
        self._tracker.add_observer(self.reward_service)

    #  User management 

    def register_user(self, name: str, email: str) -> User:
        user = User(name=name, email=email)
        self._user_repo.save(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._user_repo.find_by_id(user_id)

    #  Habit management 

    def create_habit(self, title: str, description: str, user_id: str, **kwargs) -> Habit:
        """Creates a habit using the Factory and persists it."""
        if self._user_repo.find_by_id(user_id) is None:
            raise ValueError(f"User {user_id!r} not found")
        habit = self._factory.create_habit(title, description, user_id, **kwargs)
        self._habit_repo.save(habit)
        return habit

    def get_habit(self, habit_id: str) -> Optional[Habit]:
        return self._habit_repo.find_by_id(habit_id)

    def get_user_habits(self, user_id: str) -> list[Habit]:
        return self._habit_repo.find_by_user(user_id)

    def delete_habit(self, habit_id: str) -> None:
        self._habit_repo.delete(habit_id)

    #  Tracking 

    def mark_habit_done(self, habit_id: str, user_id: str, log_date: date | None = None) -> HabitLog:
        return self._tracker.mark_habit_done(habit_id, user_id, log_date)

    def get_streak(self, habit_id: str) -> int:
        return self._tracker.get_streak(habit_id)

    #  Stats 

    def get_user_stats(self, user_id: str) -> dict:
        habits = self._habit_repo.find_by_user(user_id)
        logs = self._log_repo.find_by_user(user_id)
        return {
            "user_id": user_id,
            "total_habits": len(habits),
            "total_completions": len(logs),
            "total_points": self.reward_service.get_points(user_id),
        }
