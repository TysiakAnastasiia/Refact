from sqlalchemy.orm import Session
from datetime import date, timedelta
from app import models, schemas


# ── Habits ────────────────────────────────────────────────────────────────────

def create_habit(db: Session, habit: schemas.HabitCreate) -> models.Habit:
    db_habit = models.Habit(**habit.model_dump())
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


def get_habits(db: Session):
    return db.query(models.Habit).all()


def get_habit(db: Session, habit_id: int):
    return db.query(models.Habit).filter(models.Habit.id == habit_id).first()


def delete_habit(db: Session, habit_id: int) -> bool:
    habit = get_habit(db, habit_id)
    if not habit:
        return False
    db.delete(habit)
    db.commit()
    return True


# ── Check-ins ─────────────────────────────────────────────────────────────────

def already_checked_in(db: Session, habit_id: int, day: date) -> bool:
    return (
        db.query(models.CheckIn)
        .filter(models.CheckIn.habit_id == habit_id, models.CheckIn.date == day)
        .first()
        is not None
    )


def create_checkin(db: Session, habit_id: int) -> models.CheckIn:
    checkin = models.CheckIn(habit_id=habit_id, date=date.today())
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin


def get_checkins(db: Session, habit_id: int):
    return (
        db.query(models.CheckIn)
        .filter(models.CheckIn.habit_id == habit_id)
        .order_by(models.CheckIn.date.desc())
        .all()
    )


# ── Stats ─────────────────────────────────────────────────────────────────────

def compute_stats(db: Session, habit_id: int) -> schemas.HabitStats:
    checkins = (
        db.query(models.CheckIn)
        .filter(models.CheckIn.habit_id == habit_id)
        .order_by(models.CheckIn.date.desc())
        .all()
    )

    total = len(checkins)
    last_checkin = checkins[0].date if checkins else None

    dates = sorted({c.date for c in checkins}, reverse=True)

    current_streak = _calc_current_streak(dates)
    longest_streak = _calc_longest_streak(dates)

    return schemas.HabitStats(
        habit_id=habit_id,
        total_checkins=total,
        current_streak=current_streak,
        longest_streak=longest_streak,
        last_checkin=last_checkin,
    )


def _calc_current_streak(dates: list[date]) -> int:
    if not dates:
        return 0
    streak = 0
    cursor = date.today()
    for d in dates:
        if d == cursor or d == cursor - timedelta(days=1):
            streak += 1
            cursor = d - timedelta(days=1)
        else:
            break
    return streak


def _calc_longest_streak(dates: list[date]) -> int:
    if not dates:
        return 0
    sorted_dates = sorted(dates)
    longest = current = 1
    for i in range(1, len(sorted_dates)):
        if sorted_dates[i] - sorted_dates[i - 1] == timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest
