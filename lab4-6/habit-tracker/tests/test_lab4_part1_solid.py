"""
Lab 4 – Part 1: SOLID design, basic object creation and interactions.
Covers ≥ 10 unit tests verifying model creation and basic interactions.
"""
import pytest
from datetime import date

from src.models.user import User
from src.models.habit import DailyHabit, WeeklyHabit
from src.models.habit_log import HabitLog, LogStatus, Reward, RewardType
from src.models.schedule_strategy import (
    DailyScheduleStrategy,
    WeeklyScheduleStrategy,
    CustomScheduleStrategy,
)
from src.repositories.repositories import HabitRepository, UserRepository, HabitLogRepository


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_repos():
    """Reset singleton stores before every test to ensure isolation."""
    HabitRepository().clear()
    UserRepository().clear()
    HabitLogRepository().clear()
    yield
    HabitRepository().clear()
    UserRepository().clear()
    HabitLogRepository().clear()


@pytest.fixture
def user():
    return User(name="Alice", email="alice@example.com")


@pytest.fixture
def daily_habit(user):
    return DailyHabit(title="Morning run", description="Run 5 km", user_id=user.id)


# ── Test 1: User creation ─────────────────────────────────────────────────────

def test_user_creation_stores_fields():
    u = User(name="Bob", email="bob@example.com")
    assert u.name == "Bob"
    assert u.email == "bob@example.com"
    assert u.id  # auto-generated UUID


# ── Test 2: User validation – empty name ─────────────────────────────────────

def test_user_creation_raises_on_empty_name():
    with pytest.raises(ValueError, match="name cannot be empty"):
        User(name="", email="x@x.com")


# ── Test 3: User validation – invalid email ───────────────────────────────────

def test_user_creation_raises_on_invalid_email():
    with pytest.raises(ValueError, match="Invalid email"):
        User(name="Eve", email="not-an-email")


# ── Test 4: DailyHabit creation ───────────────────────────────────────────────

def test_daily_habit_creation(user):
    h = DailyHabit(title="Read", description="Read 30 min", user_id=user.id)
    assert h.title == "Read"
    assert h.habit_type == "daily"
    assert h.user_id == user.id


# ── Test 5: DailyHabit is_due always True ────────────────────────────────────

def test_daily_habit_is_due_any_date(daily_habit):
    assert daily_habit.is_due(date(2024, 1, 1))
    assert daily_habit.is_due(date(2025, 12, 31))


# ── Test 6: WeeklyHabit – due on correct days ────────────────────────────────

def test_weekly_habit_due_on_correct_weekday(user):
    # Monday=0, Wednesday=2
    h = WeeklyHabit(title="Gym", description="", user_id=user.id, weekdays=[0, 2])
    monday = date(2024, 4, 15)    # 2024-04-15 is Monday
    tuesday = date(2024, 4, 16)   # Tuesday
    wednesday = date(2024, 4, 17) # Wednesday
    assert h.is_due(monday)
    assert not h.is_due(tuesday)
    assert h.is_due(wednesday)


# ── Test 7: CustomScheduleStrategy ───────────────────────────────────────────

def test_custom_schedule_strategy_specific_dates():
    target = date(2024, 6, 15)
    strategy = CustomScheduleStrategy([target])
    assert strategy.is_due(target)
    assert not strategy.is_due(date(2024, 6, 16))


# ── Test 8: WeeklyScheduleStrategy – invalid weekday ─────────────────────────

def test_weekly_schedule_strategy_invalid_weekday():
    with pytest.raises(ValueError, match="Invalid weekday"):
        WeeklyScheduleStrategy([7])  # 7 is out of range


# ── Test 9: HabitLog creation ─────────────────────────────────────────────────

def test_habit_log_creation(daily_habit, user):
    log = HabitLog(
        habit_id=daily_habit.id,
        user_id=user.id,
        log_date=date.today(),
        status=LogStatus.COMPLETED,
    )
    assert log.habit_id == daily_habit.id
    assert log.status == LogStatus.COMPLETED


# ── Test 10: Habit saved and retrieved from repository ───────────────────────

def test_habit_saved_and_retrieved(daily_habit):
    repo = HabitRepository()
    repo.save(daily_habit)
    found = repo.find_by_id(daily_habit.id)
    assert found is daily_habit


# ── Test 11: Repository find_by_user returns only that user's habits ──────────

def test_repository_find_by_user(user):
    repo = HabitRepository()
    other = User(name="Other", email="other@x.com")
    h1 = DailyHabit("H1", "", user_id=user.id)
    h2 = DailyHabit("H2", "", user_id=other.id)
    repo.save(h1)
    repo.save(h2)
    results = repo.find_by_user(user.id)
    assert h1 in results
    assert h2 not in results


# ── Test 12: Reward creation and get_value ────────────────────────────────────

def test_reward_creation():
    r = Reward(reward_type=RewardType.POINTS, value=50.0, description="Test reward")
    assert r.get_value() == 50.0


# ── Test 13: Habit title cannot be empty ─────────────────────────────────────

def test_habit_empty_title_raises(user):
    with pytest.raises(ValueError, match="title cannot be empty"):
        DailyHabit(title="", description="", user_id=user.id)


# ── Test 14: Repository delete removes habit ─────────────────────────────────

def test_repository_delete(daily_habit):
    repo = HabitRepository()
    repo.save(daily_habit)
    repo.delete(daily_habit.id)
    assert repo.find_by_id(daily_habit.id) is None


# ── Test 15: find_all returns all saved habits ────────────────────────────────

def test_repository_find_all(user):
    repo = HabitRepository()
    h1 = DailyHabit("A", "", user_id=user.id)
    h2 = DailyHabit("B", "", user_id=user.id)
    repo.save(h1)
    repo.save(h2)
    all_habits = repo.find_all()
    assert h1 in all_habits
    assert h2 in all_habits
