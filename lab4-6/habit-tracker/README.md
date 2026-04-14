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

## Лабораторна робота №4 – Патерни проєктування та SOLID

### Застосовані патерни

| Патерн             | Клас(и)                                                                     | Призначення                                              |
| ------------------ | --------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Singleton**      | `HabitRepository`, `UserRepository`, `HabitLogRepository`                   | Єдине спільне сховище даних у пам'яті                    |
| **Factory Method** | `ConcreteHabitFactory`                                                      | Створення `DailyHabit`, `WeeklyHabit`, `CustomHabit`     |
| **Observer**       | `HabitTracker` → `NotificationService`, `AnalyticsService`, `RewardService` | Слабкопов'язані сповіщення про події                     |
| **Strategy**       | `DailyScheduleStrategy`, `WeeklyScheduleStrategy`, `CustomScheduleStrategy` | Змінна логіка планування (розкладу)                      |
| **Decorator**      | `BonusRewardDecorator`, `MultiplierRewardDecorator`                         | Динамічне розширення логіки нарахування нагород          |
| **Facade**         | `HabitServiceFacade`                                                        | Єдина точка входу, що приховує складність підсистем      |
| **Repository**     | `IHabitRepository` тощо                                                     | Відділення бізнес-логіки від механізмів зберігання даних |

### Відповідність принципам SOLID

| Принцип | Як реалізовано                                                                                  |
| ------- | ----------------------------------------------------------------------------------------------- |
| **SRP** | `User` лише зберігає дані; `HabitTracker` лише відстежує; `RewardService` лише нараховує бонуси |
| **OCP** | Нові типи звичок або стратегії розкладу додаються без зміни наявних класів                      |
| **LSP** | `DailyHabit` та `WeeklyHabit` є повністю взаємозамінними як типи `Habit`                        |
| **ISP** | `Observer` надає лише метод `update()`; `ScheduleStrategy` — лише `is_due()`                    |
| **DIP** | `HabitTracker` залежить від інтерфейсу `IHabitRepository`, а не від конкретних реалізацій       |

---

## Бізнес-сценарії

1. **Створення звички**: Користувач реєструється → Facade викликає Factory → Звичка зберігається в Repository.
2. **Відмітка про виконання**: Команда викликає `HabitTracker` → Створюється `HabitLog` → Сповіщаються спостерігачі (Observers).
3. **Отримання нагород**: `RewardService` (Observer) нараховує бали за кожне виконання.
4. **Відстеження серій (streaks)**: `HabitTracker` обчислює серію послідовних днів виконання на основі логів.
5. **Перегляд статистики**: Facade агрегує дані про звички, виконання та бали користувача.
