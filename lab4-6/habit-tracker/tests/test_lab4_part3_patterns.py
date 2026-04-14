"""
Lab 4 – Part 3: Design pattern verification.
Tests Singleton, Factory, Observer, Decorator patterns explicitly.
"""
import pytest
from datetime import date

from src.models.habit_log import Reward, RewardType, HabitLog, LogStatus
from src.models.user import User
from src.models.habit import DailyHabit, WeeklyHabit
from src.patterns.decorator import BonusRewardDecorator, MultiplierRewardDecorator
from src.patterns.factory import ConcreteHabitFactory
from src.patterns.observer import NotificationService, AnalyticsService, Observable
from src.repositories.repositories import HabitRepository, UserRepository, HabitLogRepository


@pytest.fixture(autouse=True)
def reset_repos():
    HabitRepository().clear()
    UserRepository().clear()
    HabitLogRepository().clear()
    yield
    HabitRepository().clear()
    UserRepository().clear()
    HabitLogRepository().clear()


# ══════════════════════════════════════════════════════════════════════════════
# SINGLETON TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_habit_repo_singleton_same_instance():
    """HabitRepository must return the exact same object every time."""
    r1 = HabitRepository()
    r2 = HabitRepository()
    assert r1 is r2


def test_user_repo_singleton_same_instance():
    r1 = UserRepository()
    r2 = UserRepository()
    assert r1 is r2


def test_singleton_shared_state():
    """Changes in one reference are visible in another – proves shared state."""
    r1 = HabitRepository()
    r2 = HabitRepository()
    user = User(name="Test", email="t@t.com")
    habit = DailyHabit("H", "", user_id=user.id)
    r1.save(habit)
    assert r2.find_by_id(habit.id) is habit


# ══════════════════════════════════════════════════════════════════════════════
# FACTORY TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_factory_creates_daily_habit():
    factory = ConcreteHabitFactory()
    user = User(name="X", email="x@x.com")
    habit = factory.create_habit("Run", "", user.id, habit_type="daily")
    assert habit.habit_type == "daily"


def test_factory_creates_weekly_habit():
    factory = ConcreteHabitFactory()
    user = User(name="X", email="x@x.com")
    habit = factory.create_habit("Gym", "", user.id, habit_type="weekly", weekdays=[0, 4])
    assert habit.habit_type == "weekly"


def test_factory_creates_custom_habit():
    factory = ConcreteHabitFactory()
    user = User(name="X", email="x@x.com")
    habit = factory.create_habit(
        "Event", "", user.id, habit_type="custom", dates=[date(2025, 1, 1)]
    )
    assert habit.habit_type == "custom"
    assert habit.is_due(date(2025, 1, 1))
    assert not habit.is_due(date(2025, 1, 2))


def test_factory_unknown_type_raises():
    factory = ConcreteHabitFactory()
    user = User(name="X", email="x@x.com")
    with pytest.raises(ValueError, match="Unknown habit type"):
        factory.create_habit("X", "", user.id, habit_type="monthly")


def test_factory_custom_without_dates_raises():
    factory = ConcreteHabitFactory()
    user = User(name="X", email="x@x.com")
    with pytest.raises(ValueError, match="non-empty 'dates'"):
        factory.create_habit("X", "", user.id, habit_type="custom", dates=[])


# ══════════════════════════════════════════════════════════════════════════════
# OBSERVER TESTS
# ══════════════════════════════════════════════════════════════════════════════

def _make_log(habit_id="h1", user_id="u1") -> HabitLog:
    return HabitLog(
        habit_id=habit_id,
        user_id=user_id,
        log_date=date.today(),
        status=LogStatus.COMPLETED,
    )


def test_observer_notification_service_receives_update():
    ns = NotificationService()
    log = _make_log()
    ns.update(log)
    assert ns.last_message() is not None
    assert log.habit_id in ns.last_message()


def test_observer_analytics_counts_completed():
    analytics = AnalyticsService()
    log = _make_log(habit_id="abc")
    analytics.update(log)
    analytics.update(log)
    assert analytics.get_count("abc") == 2


def test_observer_not_called_after_removal():
    """Removing an observer means it no longer receives events."""

    class Subject(Observable):
        def trigger(self, log):
            self.notify_observers(log)

    subject = Subject()
    ns = NotificationService()
    subject.add_observer(ns)
    subject.remove_observer(ns)

    subject.trigger(_make_log())
    assert ns.last_message() is None  # no update was received


def test_multiple_observers_all_notified():
    """All registered observers are notified."""

    class Subject(Observable):
        def trigger(self, log):
            self.notify_observers(log)

    subject = Subject()
    ns1 = NotificationService()
    ns2 = NotificationService()
    subject.add_observer(ns1)
    subject.add_observer(ns2)

    subject.trigger(_make_log())
    assert ns1.last_message() is not None
    assert ns2.last_message() is not None


# ══════════════════════════════════════════════════════════════════════════════
# DECORATOR TESTS
# ══════════════════════════════════════════════════════════════════════════════

def test_base_reward_value():
    r = Reward(reward_type=RewardType.POINTS, value=10.0)
    assert r.get_value() == 10.0


def test_bonus_decorator_adds_flat_bonus():
    base = Reward(reward_type=RewardType.POINTS, value=10.0)
    decorated = BonusRewardDecorator(base, bonus=5.0)
    assert decorated.get_value() == 15.0


def test_multiplier_decorator_scales_value():
    base = Reward(reward_type=RewardType.POINTS, value=10.0)
    decorated = MultiplierRewardDecorator(base, multiplier=3.0)
    assert decorated.get_value() == 30.0


def test_chained_decorators():
    """Bonus then multiplier – order matters and stacks correctly."""
    base = Reward(reward_type=RewardType.POINTS, value=10.0)
    with_bonus = BonusRewardDecorator(base, bonus=5.0)       # 10 + 5 = 15
    doubled = MultiplierRewardDecorator(with_bonus, multiplier=2.0)  # 15 * 2 = 30
    assert doubled.get_value() == 30.0
