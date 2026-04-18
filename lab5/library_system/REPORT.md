# Пояснювальний звіт

---

## 1. Реалізовані бізнес-сценарії

Для системи управління бібліотекою було реалізовано 4 фундаментальних бізнес-сценарії:

### Сценарій 1: Реєстрація користувача

Новий читач надає ім'я та email. Система перевіряє, що обидва поля не порожні та що email ще не зареєстрований. У разі успіху створюється запис `User` і зберігається в `UserRepository`. При повторному email кидається `EmailAlreadyRegisteredError`.

### Сценарій 2: Видача книги

Бібліотекар ініціює видачу книги (за `book_id`) конкретному читачу (за `user_id`). Сервіс перевіряє існування книги, існування користувача та доступність книги (`is_available == True`). Після успішної видачі `book.is_available` стає `False`, `book.borrowed_by` = `user_id`, а `user_id` книги додається до `user.borrowed_book_ids`.

### Сценарій 3: Повернення книги

Читач повертає книгу. Сервіс перевіряє, що книга існує, що користувач існує, і що книга дійсно позичена саме цим читачем (`book.borrowed_by == user_id`). Після повернення `book.is_available` стає `True`, `book.borrowed_by` — `None`.

### Сценарій 4: Пошук книги

Пошук здійснюється за частковим збігом назви (`find_book_by_title`) або імені автора (`find_book_by_author`) без урахування регістру. Повертається список відповідних книг або порожній список.

---

## 2. Структура коду та шарова архітектура

Проєкт організовано за шаблоном **Controller → Service → Repository**:

```
src/
├── controllers/   — точка входу, обробка CLI-команд, форматування виводу
├── services/      — вся бізнес-логіка, перевірки правил, кидання винятків
├── repositories/  — збереження та отримання даних (in-memory словники)
├── models/        — доменні об'єкти (Book, User) через @dataclass
└── dto/           — об'єкти передачі даних між шарами
```

**Принцип розділення відповідальностей:**

- `LibraryController` — не знає про правила бізнесу; лише викликає сервіс і форматує повідомлення.
- `LibraryService` — єдине місце, де живе логіка. Залежить від репозиторіїв через ін'єкцію залежностей (конструктор).
- `BookRepository` / `UserRepository` — знають лише про зберігання та пошук; не знають про бізнес-правила.

Така структура дозволяє легко замінити in-memory сховище на базу даних, не змінюючи сервіс.

---

## 3. Тести та покриття

Написано **14 юніт-тестів** у файлі `tests/test_library_service.py`, організованих у 4 класи:

| Клас               | Тест                      | Тип        |
| ------------------ | ------------------------- | ---------- |
| `TestRegisterUser` | Успішна реєстрація        | позитивний |
| `TestRegisterUser` | Дублікат email            | негативний |
| `TestRegisterUser` | Порожнє ім'я              | негативний |
| `TestIssueBook`    | Успішна видача            | позитивний |
| `TestIssueBook`    | Вже позичена книга        | негативний |
| `TestIssueBook`    | Книга не існує            | негативний |
| `TestIssueBook`    | Користувач не існує       | негативний |
| `TestReturnBook`   | Успішне повернення        | позитивний |
| `TestReturnBook`   | Книга позичена іншим      | негативний |
| `TestReturnBook`   | Книга не позичена взагалі | негативний |
| `TestFindBook`     | Пошук за назвою           | позитивний |
| `TestFindBook`     | Пошук за автором          | позитивний |
| `TestFindBook`     | Книга не знайдена         | позитивний |
| `TestFindBook`     | Порожній запит            | негативний |

**Результат:** `14 passed in 0.11s` — усі тести пройшли успішно.

---

## 4. Рефакторинг та запахи коду

### Виявлені проблеми (до рефакторингу)

- **Unused imports** — `dataclasses.field` у `book.py` та `typing.Optional` у `library_service.py` були імпортовані, але не використовувалися.
- **Відсутність DTO** — без DTO параметри передавались напряму як рядки/числа, що ускладнює рефакторинг методів сервісу.

### Виправлення

- Видалено невикористані імпорти (перевірено `flake8`).
- Введено `RegisterUserDTO`, `IssueBookDTO`, `ReturnBookDTO` для типобезпечної передачі даних між шарами.
- Кастомні класи винятків (`BookNotFoundError`, `UserNotFoundError` тощо) замість загальних `Exception`.

### Результат flake8

```
$ python -m flake8 src/ tests/ --max-line-length=100
(немає виводу — 0 попереджень)
```

---

## 5. Лог тестів

```
============================== test session starts ==============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- C:\Users\tysia\AppData\Local\Python\pythoncore-3.14-64\python.exe
cachedir: .pytest_cache
rootdir: C:\ME\UNI\Refactoring\Refact\lab5\library_system
configfile: pytest.ini
plugins: anyio-4.12.1
collected 14 items

tests/test_library_service.py::TestRegisterUser::test_register_user_success PASSED [  7%]
tests/test_library_service.py::TestRegisterUser::test_register_user_duplicate_email_raises PASSED [ 14%]
tests/test_library_service.py::TestRegisterUser::test_register_user_empty_name_raises PASSED [ 21%]
tests/test_library_service.py::TestIssueBook::test_issue_book_success PASSED [ 28%]
tests/test_library_service.py::TestIssueBook::test_issue_already_borrowed_book_raises PASSED [ 35%]
tests/test_library_service.py::TestIssueBook::test_issue_book_nonexistent_book_raises PASSED [ 42%]
tests/test_library_service.py::TestIssueBook::test_issue_book_nonexistent_user_raises PASSED [ 50%]
tests/test_library_service.py::TestReturnBook::test_return_book_success PASSED [ 57%]
tests/test_library_service.py::TestReturnBook::test_return_book_not_borrowed_by_user_raises PASSED [ 64%]
tests/test_library_service.py::TestReturnBook::test_return_available_book_raises PASSED [ 71%]
tests/test_library_service.py::TestFindBook::test_find_book_by_title_success PASSED [ 78%]
tests/test_library_service.py::TestFindBook::test_find_book_by_author_success PASSED [ 85%]
tests/test_library_service.py::TestFindBook::test_find_book_not_found_returns_empty PASSED [ 92%]
tests/test_library_service.py::TestFindBook::test_find_book_empty_query_raises PASSED [100%]

============================== 14 passed in 0.16s ===============================
```
