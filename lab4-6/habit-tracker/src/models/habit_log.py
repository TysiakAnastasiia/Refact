from dataclasses import dataclass, field
from datetime import date
from enum import Enum
import uuid


class LogStatus(str, Enum):
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass
class HabitLog:
    """
    Records a single completion (or skip) of a habit on a given date.
    (SRP: only stores the log fact)
    """
    habit_id: str
    user_id: str
    log_date: date
    status: LogStatus
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __repr__(self):
        return (
            f"HabitLog(habit={self.habit_id!r}, date={self.log_date}, status={self.status.value!r})"
        )


class RewardType(str, Enum):
    POINTS = "points"
    BADGE = "badge"
    STREAK_BONUS = "streak_bonus"


@dataclass
class Reward:
    """
    Represents a reward earned by the user.
    (SRP: only stores reward data; behaviour added via Decorator pattern)
    """
    reward_type: RewardType
    value: float
    description: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def get_value(self) -> float:
        """Return the effective reward value (overridden by decorators)."""
        return self.value

    def __repr__(self):
        return f"Reward(type={self.reward_type.value!r}, value={self.get_value()})"
