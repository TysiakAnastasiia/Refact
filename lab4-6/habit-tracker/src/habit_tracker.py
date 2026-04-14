from datetime import date

from src.models.habit import Habit
from src.models.habit_log import HabitLog, LogStatus
from src.patterns.observer import Observable, Observer
from src.repositories.repositories import HabitRepository, HabitLogRepository


class HabitTracker(Observable):
    """
    Core domain service that tracks habit completions and notifies observers.
    (SRP: only responsible for tracking; notifications delegated to observers)
    (DIP: depends on repository interfaces, not concrete storage)
    """

    def __init__(
        self,
        habit_repo: HabitRepository,
        log_repo: HabitLogRepository,
    ):
        super().__init__()
        self._habit_repo = habit_repo
        self._log_repo = log_repo

    def mark_habit_done(self, habit_id: str, user_id: str, log_date: date | None = None) -> HabitLog:
        """
        Mark a habit as completed, persist the log, and notify all observers.
        Raises ValueError if the habit is not found.
        """
        log_date = log_date or date.today()
        habit = self._habit_repo.find_by_id(habit_id)
        if habit is None:
            raise ValueError(f"Habit {habit_id!r} not found")

        habit_log = HabitLog(
            habit_id=habit_id,
            user_id=user_id,
            log_date=log_date,
            status=LogStatus.COMPLETED,
        )
        self._log_repo.save(habit_log)
        self.notify_observers(habit_log)
        return habit_log

    def get_streak(self, habit_id: str) -> int:
        """Return the current consecutive-day streak for a habit."""
        logs = self._log_repo.find_by_habit(habit_id)
        completed_dates = sorted(
            {l.log_date for l in logs if l.status == LogStatus.COMPLETED},
            reverse=True,
        )
        if not completed_dates:
            return 0

        streak = 1
        for i in range(1, len(completed_dates)):
            delta = (completed_dates[i - 1] - completed_dates[i]).days
            if delta == 1:
                streak += 1
            else:
                break
        return streak
