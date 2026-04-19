from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db, engine
from app import models, schemas, crud


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Habit Tracker API",
    description="Track your daily habits and streaks",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Habit Tracker is running"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


# ── Habits ────────────────────────────────────────────────────────────────────

@app.post("/habits", response_model=schemas.HabitOut, status_code=201, tags=["Habits"])
def create_habit(habit: schemas.HabitCreate, db: Session = Depends(get_db)):
    return crud.create_habit(db, habit)


@app.get("/habits", response_model=List[schemas.HabitOut], tags=["Habits"])
def list_habits(db: Session = Depends(get_db)):
    return crud.get_habits(db)


@app.get("/habits/{habit_id}", response_model=schemas.HabitOut, tags=["Habits"])
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = crud.get_habit(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return habit


@app.delete("/habits/{habit_id}", status_code=204, tags=["Habits"])
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    if not crud.delete_habit(db, habit_id):
        raise HTTPException(status_code=404, detail="Habit not found")


# ── Check-ins ─────────────────────────────────────────────────────────────────

@app.post("/habits/{habit_id}/checkin", response_model=schemas.CheckInOut, status_code=201, tags=["Check-ins"])
def checkin(habit_id: int, db: Session = Depends(get_db)):
    habit = crud.get_habit(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    today = date.today()
    if crud.already_checked_in(db, habit_id, today):
        raise HTTPException(status_code=409, detail="Already checked in today")
    return crud.create_checkin(db, habit_id)


@app.get("/habits/{habit_id}/checkins", response_model=List[schemas.CheckInOut], tags=["Check-ins"])
def get_checkins(habit_id: int, db: Session = Depends(get_db)):
    return crud.get_checkins(db, habit_id)


# ── Stats ─────────────────────────────────────────────────────────────────────

@app.get("/habits/{habit_id}/stats", response_model=schemas.HabitStats, tags=["Stats"])
def get_stats(habit_id: int, db: Session = Depends(get_db)):
    habit = crud.get_habit(db, habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    return crud.compute_stats(db, habit_id)
