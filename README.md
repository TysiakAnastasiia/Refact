# Лабораторні роботи — Рефакторинг коду

---

## Лаб 1 — Аналіз коду: виявлення проблемних місць

**Проект:** Tennis Score (Python)  
**Файл:** `tennis.py`

### Опис проекту

Програма симулює підрахунок рахунку в тенісі. Містить три класи — `TennisGameDefactored1`, `TennisGameDefactored2`, `TennisGameDefactored3` — кожен з яких реалізує одну й ту саму логіку по-різному. Кожен клас має два методи:
- `won_point(playerName)` — нараховує очко гравцю
- `score()` — повертає поточний рахунок у текстовому форматі (наприклад, `"Thirty-Fifteen"`, `"Deuce"`, `"Advantage player1"`)

### Крок 1 — Ознайомлення з кодом

Код складається з ~120 рядків і трьох класів. Всі три класи роблять одне й те саме, але написані по-різному — від відносно читабельного (Defactored1) до майже нечитабельного (Defactored2). Структура кожного класу однакова: конструктор, `won_point`, `score`.

### Крок 2 — Статичний аналіз коду
### Крок 3 — Виявлені проблеми та їх шкідливі наслідки

#### 1. Дублювання коду (Code Duplication)

**Де:** Усі три класи — `TennisGameDefactored1`, `TennisGameDefactored2`, `TennisGameDefactored3`.

**Що саме:** Метод `won_point` практично ідентичний у всіх трьох класах. Логіка підрахунку рахунку (Love/Fifteen/Thirty/Forty/Deuce/Advantage/Win) повторюється тричі, просто написана по-різному.

```python
# Defactored1
def won_point(self, playerName):
    if playerName == self.player1Name:
        self.p1points += 1
    else:
        self.p2points += 1

# Defactored3 — те саме, але інші назви змінних
def won_point(self, n):
    if n == self.p1N:
        self.p1 += 1
    else:
        self.p2 += 1
```

**Шкідливий наслідок:** Якщо потрібно виправити баг або змінити логіку — треба змінювати код у трьох місцях одночасно. Легко забути про одне з місць і отримати непослідовну поведінку. Це класичне порушення принципу DRY (Don't Repeat Yourself).

---

#### 2. Магічні числа (Magic Numbers)

**Де:** По всьому коду у всіх трьох класах.

**Що саме:** Числа `0`, `1`, `2`, `3`, `4` використовуються без жодного пояснення що вони означають.

```python
# Defactored1 — що означає 4? чому саме 4?
elif (self.p1points >= 4 or self.p2points >= 4):

# Defactored2 — що означає 3?
if (self.p1points == self.p2points and self.p1points > 3):
    result = "Deuce"
```

**Шкідливий наслідок:** Розробник який читає код вперше не розуміє звідки взялись ці числа. У тенісі 4 очки означають що гравець може виграти, а 3 — це поріг для Deuce. Без контексту це незрозуміло. Також якщо правила зміняться — треба шукати всі магічні числа по всьому коду.

---

#### 3. Надмірна складність (Excessive Complexity)

**Де:** Метод `score()` у `TennisGameDefactored2`.

**Що саме:** Метод містить понад 10 окремих `if`-блоків які йдуть один за одним, а не у вигляді `if/elif/else`. Це означає що Python перевіряє кожну умову окремо, навіть якщо попередня вже спрацювала.

```python
# Defactored2 — фрагмент, всього таких блоків 10+
if (self.p1points == self.p2points and self.p1points < 4):
    ...
if (self.p1points == self.p2points and self.p1points > 3):
    ...
if (self.p1points > 0 and self.p2points == 0):
    ...
if (self.p2points > 0 and self.p1points == 0):
    ...
# і так далі...
```

**Шкідливий наслідок:** Висока цикломатична складність (Cyclomatic Complexity) — метрика яка показує кількість незалежних шляхів виконання коду. Чим вона вища, тим важче тестувати і розуміти код. Такий код легко зламати при редагуванні — одна зміна може непомітно вплинути на інші гілки.

---

#### 4. Погані назви змінних і методів (Poor Naming)

**Де:** `TennisGameDefactored3` та `TennisGameDefactored2`.

**Що саме:**
- `p1N`, `p2N` — незрозумілі скорочення замість `player1_name`, `player2_name`
- `p1`, `p2` — замість `p1_points`, `p2_points`
- `P1Score()`, `P2Score()` — назви методів з великої літери, що порушує PEP8 (методи мають бути `snake_case`)

```python
# Defactored3 — що таке p1N і p2N?
def __init__(self, player1Name, player2Name):
    self.p1N = player1Name
    self.p2N = player2Name
    self.p1 = 0
    self.p2 = 0
```

**Шкідливий наслідок:** Код важче читати і розуміти. Новий розробник витрачає додатковий час на розшифровку скорочень. Порушення PEP8 ускладнює співпрацю в команді де всі дотримуються стандарту.

---

#### 5. Порушення принципу єдиної відповідальності (Single Responsibility Principle)

**Де:** `TennisGameDefactored2`.

**Що саме:** Клас містить методи `SetP1Score` і `SetP2Score` які використовуються виключно для налаштування стану в тестах. Клас гри не повинен знати про те як його тестують.

```python
# Defactored2 — ці методи не мають відношення до логіки гри
def SetP1Score(self, number):
    for i in range(number):
        self.P1Score()

def SetP2Score(self, number):
    for i in range(number):
        self.P2Score()
```

**Шкідливий наслідок:** Клас бере на себе більше відповідальності ніж потрібно. Якщо змінити спосіб тестування — доведеться змінювати і сам клас гри. Це порушення SRP з принципів SOLID.

---

### Крок 4 — Модульні тести

Написано 13 модульних тестів у файлі `tennis_tests.py` з використанням `pytest`. Тести покривають:

| № | Тест | Що перевіряє |
|---|---|---|
| 1 | `test_initial_score_is_love_all` | Початковий рахунок 0:0 = Love-All |
| 2 | `test_tied_scores_before_deuce` | Нічиї 1:1, 2:2, 3:3 |
| 3 | `test_deuce_when_both_above_three` | Deuce при 4:4, 5:5, 10:10 |
| 4 | `test_advantage_player1` | Advantage при 4:3 |
| 5 | `test_advantage_player2` | Advantage при 3:4 |
| 6 | `test_win_player1_before_deuce` | Перемога 4:0, 4:1, 4:2 |
| 7 | `test_win_player2_before_deuce` | Перемога 0:4, 1:4, 2:4 |
| 8 | `test_win_after_deuce_player1` | Перемога після Deuce 6:4 |
| 9 | `test_win_after_deuce_player2` | Перемога після Deuce 4:6 |
| 10 | `test_regular_scores` | Звичайні рахунки (Thirty-Fifteen тощо) |
| 11 | `test_custom_player_names_in_advantage_and_win` | Кастомні імена у рядку рахунку |
| 12 | `test_won_point_increments_correct_player` | Коректність нарахування очок |
| 13 | `test_long_game_multiple_deuce` | Тривала гра з кількома Deuce/Advantage |

### Файли

- `tennis.py` — оригінальний код (збережено без змін)
- `Refactored.py` — рефакторований клас з детальними коментарями
- `tennis_tests.py` — нові модульні тести (pytest, 13 тестів)
- `tennis_unittest.py` — оригінальні тести

---

## Лаб 2 — Рефакторинг коду

**Проект:** Tennis Score (Python) — продовження Лаб 1  
**Файл:** `Refactored.py`

### Опис

На основі аналізу з Лаб 1 виконано повний рефакторинг. Три дублюючі класи замінено одним чистим класом `TennisGame`. Всі зміни задокументовані коментарями безпосередньо у коді — оригінальні рядки закоментовані (не видалені) з поясненням причини зміни.

### Застосовані методи рефакторингу

#### Extract Method — Виділення методів

Великий метод `score()` розбито на дрібніші допоміжні методи. Кожен метод має одну чітку відповідальність:

```python
def _is_tied(self) -> bool:
    return self.p1_points == self.p2_points

def _score_name(self, points: int) -> str:
    return SCORE_NAMES[points]  # замість повторюваних словників по всьому коду
```

#### Replace Magic Numbers with Constants — Заміна магічних чисел

```python
# Було: розкидані по коду числа без пояснення
if self.p1points >= 4 or self.p2points >= 4:

# Стало: іменовані константи на початку файлу
SCORE_NAMES = ["Love", "Fifteen", "Thirty", "Forty"]
WIN_DIFF = 2
DEUCE_THRESHOLD = 3
```

#### Remove Duplication — Усунення дублювання

Три класи з ідентичною логікою замінено одним. `won_point` існує в єдиному екземплярі.

#### Rename — Перейменування

| Було | Стало | Причина |
|---|---|---|
| `p1N`, `p2N` | `player1_name`, `player2_name` | Зрозумілі назви |
| `p1`, `p2` | `p1_points`, `p2_points` | Зрозумілі назви |
| `P1Score()` | прибрано | Порушення PEP8, дублювало `won_point` |
| `SetP1Score()` | прибрано | Не належить до відповідальності класу |
| `player1Name` | `player1_name` | PEP8: snake_case для атрибутів |

### Результат тестування

Усі 13 тестів пройшли успішно до і після рефакторингу — поведінка програми не змінилась, лише якість коду.

### Файли

- `Refactored.py` — фінальний рефакторований клас з коментарями
- `tennis_tests.py` — модульні тести (pytest, 13 тестів)
