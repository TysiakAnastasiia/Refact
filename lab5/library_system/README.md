# Бібліотечна система — Лабораторна робота 5

## Опис

Проєкт реалізує систему управління бібліотекою на Python з дотриманням архітектурного шаблону **Controller → Service → Repository**. Реалізовано 4 ключові бізнес-сценарії та 14 юніт-тестів.

---

## Структура проєкту

```
library_system/
├── src/
│   ├── controllers/
│   │   └── library_controller.py   # CLI-контролер, точка входу
│   ├── services/
│   │   └── library_service.py      # Вся бізнес-логіка
│   ├── repositories/
│   │   ├── book_repository.py      # Робота з даними книг
│   │   └── user_repository.py      # Робота з даними користувачів
│   ├── models/
│   │   ├── book.py                 # Модель книги
│   │   └── user.py                 # Модель користувача
│   └── dto/
│       └── __init__.py             # DTO об'єкти для передачі даних
├── tests/
│   └── test_library_service.py     # 14 юніт-тестів
├── main.py                         # Демонстраційний запуск
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Бізнес-сценарії

### 1. Реєстрація користувача (`register_user`)

Новий читач реєструється в системі, надавши ім'я та унікальний email.  
**Правила:** email не може повторюватися; ім'я та email не можуть бути порожніми.

### 2. Видача книги (`issue_book`)

Бібліотекар видає доступну книгу зареєстрованому користувачу.  
**Правила:** книга і користувач повинні існувати; книга повинна бути доступною (не позиченою).

### 3. Повернення книги (`return_book`)

Читач повертає раніше позичену книгу.  
**Правила:** книга повинна бути позичена саме цим користувачем.

### 4. Пошук книги (`find_book_by_title` / `find_book_by_author`)

Пошук книг за частковим збігом назви або автора (без урахування регістру).  
**Правила:** пошуковий рядок не може бути порожнім.

---

## Встановлення залежностей

```bash
pip install -r requirements.txt
```

Вміст `requirements.txt`:

```
pytest>=7.0
pytest-cov>=4.0
flake8>=6.0
```

---

## Запуск тестів

```bash
# Запустити всі тести з детальним виводом
python -m pytest tests/ -v

# Запустити тести з покриттям коду
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

### Очікуваний результат

```
============================= test session starts ==============================
tests/test_library_service.py::TestRegisterUser::test_register_user_success PASSED
tests/test_library_service.py::TestRegisterUser::test_register_user_duplicate_email_raises PASSED
tests/test_library_service.py::TestRegisterUser::test_register_user_empty_name_raises PASSED
tests/test_library_service.py::TestIssueBook::test_issue_book_success PASSED
tests/test_library_service.py::TestIssueBook::test_issue_already_borrowed_book_raises PASSED
tests/test_library_service.py::TestIssueBook::test_issue_book_nonexistent_book_raises PASSED
tests/test_library_service.py::TestIssueBook::test_issue_book_nonexistent_user_raises PASSED
tests/test_library_service.py::TestReturnBook::test_return_book_success PASSED
tests/test_library_service.py::TestReturnBook::test_return_book_not_borrowed_by_user_raises PASSED
tests/test_library_service.py::TestReturnBook::test_return_available_book_raises PASSED
tests/test_library_service.py::TestFindBook::test_find_book_by_title_success PASSED
tests/test_library_service.py::TestFindBook::test_find_book_by_author_success PASSED
tests/test_library_service.py::TestFindBook::test_find_book_not_found_returns_empty PASSED
tests/test_library_service.py::TestFindBook::test_find_book_empty_query_raises PASSED
============================== 14 passed in 0.11s ==============================
```

---

## Запуск програми

```bash
python main.py
```

---

## Перевірка якості коду (flake8)

```bash
python -m flake8 src/ tests/ --max-line-length=100
```

Очікуваний результат: **0 попереджень**.

---

## Запуск тестів з покриттям

```bash
python -m pytest tests/ --cov=src --cov-report=term-missing -v
```
