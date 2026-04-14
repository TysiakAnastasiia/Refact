"""
Lab 4 – Part 2: TDD – tests first, then implementation verifies functionality.
Covers adding habits, creating orders/logs, associating them with users,
notifying the kitchen (observer) – mapped to our domain.
"""
import pytest
from datetime import date

from src.models.habit_log import LogStatus
from src.repositories.repositories import HabitRepository, UserRepository, HabitLogRepository
from src.services.facade import HabitServiceFacade


@pytest.fixture
def facade():
    """Fresh facade with cleared singleton repos before each test."""
    HabitRepository().clear()
    UserRepository().clear()
    HabitLogRepository().clear()
    f = HabitServiceFacade()
    yield f
    HabitRepository().clear()
    UserRepository().clear()
    HabitLogRepository().clear()


# ── Test 1: Register user and retrieve ───────────────────────────────────────

def test_register_and_retrieve_user(facade):
    user = facade.register_user("Alice", "alice@example.com")
    found = facade.get_user(user.id)
    assert found is not None
    assert found.name == "Alice"


# ── Test 2: Create daily habit for existing user ──────────────────────────────

def test_create_daily_habit(facade):
    user = facade.register_user("Bob", "bob@example.com")
    habit = facade.create_habit("Meditate", "10 min", user.id, habit_type="daily")
    assert habit.title == "Meditate"
    assert habit.habit_type == "daily"


# ── Test 3: Create weekly habit with weekdays ─────────────────────────────────

def test_create_weekly_habit(facade):
    user = facade.register_user("Carol", "carol@example.com")
    habit = facade.create_habit("Yoga", "Morning yoga", user.id, habit_type="weekly", weekdays=[1, 3, 5])
    assert habit.habit_type == "weekly"


# ── Test 4: Creating habit for non-existing user raises ───────────────────────

def test_create_habit_unknown_user_raises(facade):
    with pytest.raises(ValueError, match="not found"):
        facade.create_habit("X", "", "non-existing-id", habit_type="daily")


# ── Test 5: Mark habit done creates a log entry ───────────────────────────────

def test_mark_habit_done_creates_log(facade):
    user = facade.register_user("Dan", "dan@example.com")
    habit = facade.create_habit("Drink water", "", user.id, habit_type="daily")
    log = facade.mark_habit_done(habit.id, user.id, date(2024, 1, 10))
    assert log.status == LogStatus.COMPLETED
    assert log.habit_id == habit.id


# ── Test 6: Mark habit done notifies NotificationService (Observer) ───────────

def test_mark_habit_done_notifies_observers(facade):
    user = facade.register_user("Eve", "eve@example.com")
    habit = facade.create_habit("Journal", "", user.id, habit_type="daily")
    facade.mark_habit_done(habit.id, user.id)
    assert facade.notification_service.last_message() is not None
    assert habit.id in facade.notification_service.last_message()


# ── Test 7: Analytics counts completions per habit ───────────────────────────

def test_analytics_counts_completions(facade):
    user = facade.register_user("Frank", "frank@example.com")
    habit = facade.create_habit("Push-ups", "", user.id, habit_type="daily")
    facade.mark_habit_done(habit.id, user.id, date(2024, 1, 1))
    facade.mark_habit_done(habit.id, user.id, date(2024, 1, 2))
    assert facade.analytics_service.get_count(habit.id) == 2


# ── Test 8: Reward service grants points on completion ───────────────────────

def test_reward_service_grants_points(facade):
    user = facade.register_user("Gina", "gina@example.com")
    habit = facade.create_habit("Walk", "", user.id, habit_type="daily")
    facade.mark_habit_done(habit.id, user.id)
    assert facade.reward_service.get_points(user.id) > 0


# ── Test 9: Streak computed correctly ────────────────────────────────────────

def test_streak_consecutive_days(facade):
    user = facade.register_user("Hank", "hank@example.com")
    habit = facade.create_habit("Cold shower", "", user.id, habit_type="daily")
    for day in [1, 2, 3]:
        facade.mark_habit_done(habit.id, user.id, date(2024, 5, day))
    assert facade.get_streak(habit.id) == 3


# ── Test 10: Streak resets on gap ────────────────────────────────────────────

def test_streak_resets_on_gap(facade):
    user = facade.register_user("Iris", "iris@example.com")
    habit = facade.create_habit("Study", "", user.id, habit_type="daily")
    facade.mark_habit_done(habit.id, user.id, date(2024, 5, 1))
    facade.mark_habit_done(habit.id, user.id, date(2024, 5, 3))  # gap on 2nd
    assert facade.get_streak(habit.id) == 1


# ── Test 11: get_user_stats returns correct summary ───────────────────────────

def test_get_user_stats(facade):
    user = facade.register_user("Jake", "jake@example.com")
    h1 = facade.create_habit("Read", "", user.id, habit_type="daily")
    h2 = facade.create_habit("Run", "", user.id, habit_type="daily")
    facade.mark_habit_done(h1.id, user.id, date(2024, 6, 1))
    facade.mark_habit_done(h2.id, user.id, date(2024, 6, 1))
    stats = facade.get_user_stats(user.id)
    assert stats["total_habits"] == 2
    assert stats["total_completions"] == 2
    assert stats["total_points"] > 0


# ── Test 12: Marking unknown habit raises ────────────────────────────────────

def test_mark_unknown_habit_raises(facade):
    user = facade.register_user("Kate", "kate@example.com")
    with pytest.raises(ValueError, match="not found"):
        facade.mark_habit_done("no-such-id", user.id)


# ── Test 13: Delete habit removes it from repository ────────────────────────

def test_delete_habit(facade):
    user = facade.register_user("Leo", "leo@example.com")
    habit = facade.create_habit("Floss", "", user.id, habit_type="daily")
    facade.delete_habit(habit.id)
    assert facade.get_habit(habit.id) is None


# ── Test 14: Empty menu (no habits) returns empty list ────────────────────────

def test_get_habits_empty_for_new_user(facade):
    user = facade.register_user("Mia", "mia@example.com")
    assert facade.get_user_habits(user.id) == []
