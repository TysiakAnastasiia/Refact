# Habit Tracker API

REST API для відстеження щоденних звичок з підрахунком стріків. Побудовано на **FastAPI + PostgreSQL**.

---

## Запуск через Docker

```bash
cp .env.example .env

docker-compose up --build

# API доступне за адресою: http://localhost:8000
# Документація Swagger:    http://localhost:8000/docs
```

### Запуск тестів у Docker

```bash
docker-compose --profile test run test
```

---

## Локальний запуск (без Docker)

```bash
python -m venv venv
Windows: venv\Scripts\activate

pip install -r requirements.txt -r requirements-test.txt

# Налаштуйте DATABASE_URL в .env або експортуйте напряму:
export DATABASE_URL=postgresql://habit_user:habit_pass@localhost:5432/habit_db

uvicorn app.main:app --reload
```

---

## Змінні середовища

| Змінна              | Опис                          | За замовчуванням               |
| ------------------- | ----------------------------- | ------------------------------ |
| `DATABASE_URL`      | Повний URL бази PostgreSQL    | `postgresql://...@db:5432/...` |
| `POSTGRES_USER`     | Ім'я користувача PostgreSQL   | `habit_user`                   |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL             | `habit_pass`                   |
| `POSTGRES_DB`       | Назва бази даних              | `habit_db`                     |
| `APP_PORT`          | Порт, на якому слухає додаток | `8000`                         |

---

## Основні ендпоінти

| Метод  | URL                     | Опис                              |
| ------ | ----------------------- | --------------------------------- |
| GET    | `/`                     | Health check                      |
| POST   | `/habits`               | Створити нову звичку              |
| GET    | `/habits`               | Список усіх звичок                |
| GET    | `/habits/{id}`          | Отримати звичку за ID             |
| DELETE | `/habits/{id}`          | Видалити звичку                   |
| POST   | `/habits/{id}/checkin`  | Відмітити виконання за сьогодні   |
| GET    | `/habits/{id}/checkins` | Всі відмітки звички               |
| GET    | `/habits/{id}/stats`    | Статистика: стрік, загальна к-сть |

### Приклади запитів

```bash
# Створити звичку
curl -X POST http://localhost:8000/habits \
  -H "Content-Type: application/json" \
  -d '{"name": "Read 30 min", "description": "Before sleep", "color": "#10b981"}'

# Відмітити виконання
curl -X POST http://localhost:8000/habits/1/checkin

# Отримати статистику
curl http://localhost:8000/habits/1/stats
```

---

## Тести

```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

Очікуваний результат: **20+ тестів**, покриття **>85%**.

Тести охоплюють:

- CRUD операції над звичками
- Check-in логіку (дублікати → 409)
- Підрахунок стріків (поточний та найдовший)
- Edge cases (не існуючі ресурси → 404)

---

## Перевірка роботи

Відкрийте браузер: **http://localhost:8000/docs** — інтерактивна Swagger UI документація.

---

## Структура проєкту

```
habit-tracker/
├── app/
│   ├── main.py        # FastAPI app, роутери
│   ├── database.py    # Підключення до БД
│   ├── models.py      # SQLAlchemy моделі
│   ├── schemas.py     # Pydantic схеми
│   └── crud.py        # Бізнес-логіка, підрахунок стріків
├── tests/
│   └── test_api.py    # 20+ тестів
├── .github/
│   └── workflows/
│       └── ci.yml     # GitHub Actions CI/CD
├── Dockerfile
├── Dockerfile.test
├── docker-compose.yaml
├── requirements.txt
├── requirements-test.txt
└── .env.example
```
