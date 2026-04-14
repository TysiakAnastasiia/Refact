from abc import ABC, abstractmethod
from typing import Optional
import threading

from src.models.habit import Habit
from src.models.habit_log import HabitLog
from src.models.user import User


#  Abstract repository interfaces (DIP) 

class IHabitRepository(ABC):
    @abstractmethod
    def save(self, habit: Habit) -> None: ...
    @abstractmethod
    def find_by_id(self, habit_id: str) -> Optional[Habit]: ...
    @abstractmethod
    def find_all(self) -> list[Habit]: ...
    @abstractmethod
    def find_by_user(self, user_id: str) -> list[Habit]: ...
    @abstractmethod
    def delete(self, habit_id: str) -> None: ...


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]: ...
    @abstractmethod
    def find_all(self) -> list[User]: ...


class IHabitLogRepository(ABC):
    @abstractmethod
    def save(self, log: HabitLog) -> None: ...
    @abstractmethod
    def find_by_habit(self, habit_id: str) -> list[HabitLog]: ...
    @abstractmethod
    def find_by_user(self, user_id: str) -> list[HabitLog]: ...


#  Thread-safe singleton store 

_instances: dict = {}
_lock = threading.Lock()


def _singleton(cls):
    """Return the single instance of cls, creating it on first call."""
    with _lock:
        if cls not in _instances:
            obj = object.__new__(cls)
            obj._initialized = False
            _instances[cls] = obj
    return _instances[cls]


#  In-memory implementations 

class HabitRepository(IHabitRepository):
    """Singleton in-memory Habit repository."""

    def __new__(cls):
        return _singleton(cls)

    def __init__(self):
        if not self._initialized:
            self._store: dict[str, Habit] = {}
            self._initialized = True

    def clear(self) -> None:
        self._store.clear()

    def save(self, habit: Habit) -> None:
        self._store[habit.id] = habit

    def find_by_id(self, habit_id: str) -> Optional[Habit]:
        return self._store.get(habit_id)

    def find_all(self) -> list[Habit]:
        return list(self._store.values())

    def find_by_user(self, user_id: str) -> list[Habit]:
        return [h for h in self._store.values() if h.user_id == user_id]

    def delete(self, habit_id: str) -> None:
        self._store.pop(habit_id, None)


class UserRepository(IUserRepository):
    """Singleton in-memory User repository."""

    def __new__(cls):
        return _singleton(cls)

    def __init__(self):
        if not self._initialized:
            self._store: dict[str, User] = {}
            self._initialized = True

    def clear(self) -> None:
        self._store.clear()

    def save(self, user: User) -> None:
        self._store[user.id] = user

    def find_by_id(self, user_id: str) -> Optional[User]:
        return self._store.get(user_id)

    def find_all(self) -> list[User]:
        return list(self._store.values())


class HabitLogRepository(IHabitLogRepository):
    """Singleton in-memory HabitLog repository."""

    def __new__(cls):
        return _singleton(cls)

    def __init__(self):
        if not self._initialized:
            self._logs: list[HabitLog] = []
            self._initialized = True

    def clear(self) -> None:
        self._logs.clear()

    def save(self, log: HabitLog) -> None:
        self._logs.append(log)

    def find_by_habit(self, habit_id: str) -> list[HabitLog]:
        return [lg for lg in self._logs if lg.habit_id == habit_id]

    def find_by_user(self, user_id: str) -> list[HabitLog]:
        return [lg for lg in self._logs if lg.user_id == user_id]
