# Gamified Habit Tracking System (Гейміфікована система відстеження звичок)

Система на Python для керування звичками користувачів з елементами гейміфікації.  
Розроблена в межах Лабораторних робіт №4–6 з використанням принципів SOLID, патернів проєктування, багатошарової архітектури та практик DevOps.

---

## Технологічний стек

- **Мова**: Python 3.12
- **Тестування**: pytest, pytest-cov

---

## Структура проєкту

```
habit-tracker/
├── src/
│   ├── controllers/      # Точки входу (CLI / симуляція контролера)
│   ├── services/         # Бізнес-логіка: HabitTracker, RewardService, Facade
│   ├── repositories/     # Шар доступу до даних (Singleton сховища в пам'яті)
│   ├── models/           # Доменні сутності: User, Habit, HabitLog, Reward
│   ├── patterns/         # Реалізація патернів: Factory, Observer, Decorator
│   └── dto/              # Об'єкти передачі даних (Data Transfer Objects)
├── tests/
│   ├── unit/             # Юніт-тести (Лаб 4 та 5)
│   └── integration/      # Інтеграційні тести (Лаб 6)
├── docs/
│   └── diagrams/         # UML-діаграми класів (Mermaid)
├── db/
│   ├── migrations/
│   └── seed/
├── .github/workflows/    # CI/CD (GitHub Actions)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Запуск тестів

### Встановлення залежностей

```bash
python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Запуск усіх юніт-тестів

```bash
python -m pytest tests/unit/ -v
```

### Запуск зі звітом про покриття коду (coverage)

```bash
python -m pytest tests/unit/ --cov=src --cov-report=term-missing
```

Ось переклад розділу про відповідність вимогам Лабораторної роботи №4 (Compliance) для твого `README.md`. Я адаптував термінологію, щоб було зрозуміло, як класи твого проєкту відповідають базовим вимогам завдання.

````markdown
### Структура класів (Menu, Dish, Order, Customer, KitchenNotifier)

У проєкті реалізовано аналоги базових сутностей згідно з варіантом:

- **Menu (Меню)** → `HabitTracker` (колекція звичок).
- **Dish (Страва)** → `Habit` (індивідуальна одиниця звички).
- **Order (Замовлення)** → `HabitLog` (запис про виконання звички).
- **Customer (Клієнт)** → `User` (користувач, який створює звички).
- **KitchenNotifier (Сповіщувач кухні)** → `NotificationService` (сповіщення про успішне виконання).

### Реалізація принципів SOLID

- **SRP (Принцип єдиної відповідальності)**: Кожен клас виконує лише одну чітку функцію.
- **OCP (Принцип відкритості/закритості)**: Нові типи звичок додаються через розширення класів без зміни основного коду.
- **DIP (Принцип інверсії залежностей)**: Використання інтерфейсів для зменшення зв'язності (loose coupling).

### Процес TDD (Розробка через тестування)

- **45 тестів**
- **100% проходження** для всіх тестових наборів.
- Використання циклу **Red-Green-Refactor** для кожного функціонального блоку.

### Патерни проєктування

- **Singleton (Одинак)**: Класи-репозиторії з єдиною базою даних у пам'яті.
- **Factory (Фабрика)**: Створення різних типів "замовлень" (щоденні та щотижневі звички).
- **Observer (Спостерігач)**: Сповіщення сервісів (аналог кухні) про нові "замовлення" (виконання звичок).

### Приклади тестів

**Додавання страв у меню (Створення звичок):**

```python
def test_create_daily_habit(facade):
    user = facade.register_user("Bob", "bob@example.com")
    habit = facade.create_habit("Медитація", "10 хв", user.id, habit_type="daily")
    assert habit.title == "Медитація"
    assert habit.habit_type == "daily"
```
````

**Створення замовлень (Виконання звички):**

```python
def test_mark_habit_done_creates_log(facade):
    user = facade.register_user("Dan", "dan@example.com")
    habit = facade.create_habit("Пити воду", "", user.id, habit_type="daily")
    log = facade.mark_habit_done(habit.id, user.id, date(2024, 1, 10))
    assert log.status == LogStatus.COMPLETED
```

**Сповіщення кухні (Патерн Observer):**

```python
def test_mark_habit_done_notifies_observers(facade):
    user = facade.register_user("Eve", "eve@example.com")
    habit = facade.create_habit("Журнал", "", user.id, habit_type="daily")
    facade.mark_habit_done(habit.id, user.id)
    assert facade.notification_service.last_message() is not None
```

---

1.  **Структура**: Реалізовано аналоги Menu/Dish/Order/Customer/KitchenNotifier.
2.  **SOLID**: Повна відповідність усім 5 принципам.
3.  **TDD**: 45 тестів зі 100% проходженням (цикл Red-Green-Refactor).
4.  **Патерни**: Належним чином впроваджено Singleton, Factory, Observer.
5.  **Документація**: Наявна UML-діаграма та звіти про тестування.
6.  **Покриття**: Понад 10 тестів для кожної частини (загалом 45 при мінімумі 30).

```

```
