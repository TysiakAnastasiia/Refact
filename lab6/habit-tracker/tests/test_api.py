import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

from app.main import app
from app.database import get_db, Base
from app import crud

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Health ────────────────────────────────────────────────────────────────────

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200


# ── Habit CRUD ────────────────────────────────────────────────────────────────

def test_create_habit(client):
    r = client.post("/habits", json={"name": "Exercise", "description": "30 min daily"})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Exercise"
    assert "id" in data


def test_list_habits_empty(client):
    r = client.get("/habits")
    assert r.status_code == 200
    assert r.json() == []


def test_list_habits(client):
    client.post("/habits", json={"name": "Read"})
    client.post("/habits", json={"name": "Meditate"})
    r = client.get("/habits")
    assert len(r.json()) == 2


def test_get_habit(client):
    created = client.post("/habits", json={"name": "Sleep 8h"}).json()
    r = client.get(f"/habits/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Sleep 8h"


def test_get_habit_not_found(client):
    r = client.get("/habits/9999")
    assert r.status_code == 404


def test_delete_habit(client):
    created = client.post("/habits", json={"name": "Walk"}).json()
    r = client.delete(f"/habits/{created['id']}")
    assert r.status_code == 204
    r2 = client.get(f"/habits/{created['id']}")
    assert r2.status_code == 404


def test_create_habit_empty_name(client):
    r = client.post("/habits", json={"name": ""})
    assert r.status_code == 422


def test_habit_default_color(client):
    r = client.post("/habits", json={"name": "Morning run"})
    assert r.json()["color"] == "#6366f1"


def test_habit_custom_color(client):
    r = client.post("/habits", json={"name": "Yoga", "color": "#10b981"})
    assert r.json()["color"] == "#10b981"


# ── Check-ins ─────────────────────────────────────────────────────────────────

def test_checkin(client):
    habit = client.post("/habits", json={"name": "Code"}).json()
    r = client.post(f"/habits/{habit['id']}/checkin")
    assert r.status_code == 201
    assert r.json()["habit_id"] == habit["id"]


def test_checkin_duplicate(client):
    habit = client.post("/habits", json={"name": "Code"}).json()
    client.post(f"/habits/{habit['id']}/checkin")
    r = client.post(f"/habits/{habit['id']}/checkin")
    assert r.status_code == 409


def test_checkin_unknown_habit(client):
    r = client.post("/habits/9999/checkin")
    assert r.status_code == 404


def test_get_checkins(client):
    habit = client.post("/habits", json={"name": "Journal"}).json()
    client.post(f"/habits/{habit['id']}/checkin")
    r = client.get(f"/habits/{habit['id']}/checkins")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_checkins_empty(client):
    habit = client.post("/habits", json={"name": "Read"}).json()
    r = client.get(f"/habits/{habit['id']}/checkins")
    assert r.json() == []


# ── Stats ─────────────────────────────────────────────────────────────────────

def test_stats_empty(client):
    habit = client.post("/habits", json={"name": "Yoga"}).json()
    r = client.get(f"/habits/{habit['id']}/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total_checkins"] == 0
    assert data["current_streak"] == 0
    assert data["longest_streak"] == 0
    assert data["last_checkin"] is None


def test_stats_after_checkin(client):
    habit = client.post("/habits", json={"name": "Yoga"}).json()
    client.post(f"/habits/{habit['id']}/checkin")
    r = client.get(f"/habits/{habit['id']}/stats")
    data = r.json()
    assert data["total_checkins"] == 1
    assert data["current_streak"] == 1
    assert data["longest_streak"] == 1


def test_stats_not_found(client):
    r = client.get("/habits/9999/stats")
    assert r.status_code == 404


# ── Streak unit tests ─────────────────────────────────────────────────────────

def test_streak_consecutive():
    today = date.today()
    dates = [today, today - timedelta(1), today - timedelta(2)]
    assert crud._calc_current_streak(dates) == 3


def test_streak_broken():
    today = date.today()
    dates = [today, today - timedelta(3)]
    assert crud._calc_current_streak(dates) == 1


def test_streak_empty():
    assert crud._calc_current_streak([]) == 0


def test_longest_streak():
    d = date(2024, 1, 1)
    dates = [d + timedelta(i) for i in range(5)]
    assert crud._calc_longest_streak(dates) == 5


def test_longest_streak_with_gap():
    d = date(2024, 1, 1)
    dates = [d + timedelta(i) for i in range(3)] + [d + timedelta(10 + i) for i in range(7)]
    assert crud._calc_longest_streak(dates) == 7


def test_longest_streak_empty():
    assert crud._calc_longest_streak([]) == 0
