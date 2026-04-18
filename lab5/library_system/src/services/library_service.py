from typing import List

from src.dto import IssueBookDTO, RegisterUserDTO, ReturnBookDTO
from src.models.book import Book
from src.models.user import User
from src.repositories.book_repository import BookRepository
from src.repositories.user_repository import UserRepository


class BookNotFoundError(Exception):
    """Виняток: книга не знайдена."""


class UserNotFoundError(Exception):
    """Виняток: користувач не знайдений."""


class BookAlreadyBorrowedError(Exception):
    """Виняток: книга вже позичена."""


class BookNotBorrowedByUserError(Exception):
    """Виняток: книга не була позичена цим користувачем."""


class EmailAlreadyRegisteredError(Exception):
    """Виняток: email вже зареєстрований."""


class LibraryService:
    """
    Сервісний шар бібліотечної системи.

    Реалізує такі бізнес-сценарії:
    - Реєстрація користувача
    - Видача книги (issueBook)
    - Повернення книги (returnBook)
    - Пошук книги за назвою або автором
    """

    def __init__(
        self,
        book_repo: BookRepository,
        user_repo: UserRepository,
    ) -> None:
        self._book_repo = book_repo
        self._user_repo = user_repo

    # Сценарій 1: Реєстрація користувача

    def register_user(self, dto: RegisterUserDTO) -> User:
        """
        Реєструє нового користувача в системі.

        Бізнес-правила:
        - Email повинен бути унікальним.
        - Ім'я та email не можуть бути порожніми.

        Raises:
            ValueError: якщо ім'я або email порожні.
            EmailAlreadyRegisteredError: якщо email вже використовується.
        """
        if not dto.name or not dto.name.strip():
            raise ValueError("Ім'я користувача не може бути порожнім.")
        if not dto.email or not dto.email.strip():
            raise ValueError("Email не може бути порожнім.")

        existing = self._user_repo.get_by_email(dto.email)
        if existing is not None:
            raise EmailAlreadyRegisteredError(
                f"Email '{dto.email}' вже зареєстрований."
            )

        return self._user_repo.add(name=dto.name.strip(), email=dto.email.strip())

    # Сценарій 2: Видача книги

    def issue_book(self, dto: IssueBookDTO) -> Book:
        """
        Видає книгу зареєстрованому користувачу.

        Бізнес-правила:
        - Книга повинна існувати.
        - Користувач повинен існувати.
        - Книга повинна бути доступною (не позиченою).

        Raises:
            BookNotFoundError: книга не знайдена.
            UserNotFoundError: користувач не знайдений.
            BookAlreadyBorrowedError: книга вже позичена.
        """
        book = self._book_repo.get_by_id(dto.book_id)
        if book is None:
            raise BookNotFoundError(f"Книга з id={dto.book_id} не знайдена.")

        user = self._user_repo.get_by_id(dto.user_id)
        if user is None:
            raise UserNotFoundError(f"Користувач з id={dto.user_id} не знайдений.")

        if not book.is_available:
            raise BookAlreadyBorrowedError(
                f"Книга '{book.title}' вже позичена користувачем id={book.borrowed_by}."
            )

        book.is_available = False
        book.borrowed_by = dto.user_id
        self._book_repo.save(book)

        user.borrowed_book_ids.append(dto.book_id)
        self._user_repo.save(user)

        return book

    # Сценарій 3: Повернення книги

    def return_book(self, dto: ReturnBookDTO) -> Book:
        """
        Приймає повернення книги від користувача.

        Бізнес-правила:
        - Книга повинна існувати.
        - Користувач повинен існувати.
        - Книга повинна бути позичена саме цим користувачем.

        Raises:
            BookNotFoundError: книга не знайдена.
            UserNotFoundError: користувач не знайдений.
            BookNotBorrowedByUserError: книга не була позичена цим користувачем.
        """
        book = self._book_repo.get_by_id(dto.book_id)
        if book is None:
            raise BookNotFoundError(f"Книга з id={dto.book_id} не знайдена.")

        user = self._user_repo.get_by_id(dto.user_id)
        if user is None:
            raise UserNotFoundError(f"Користувач з id={dto.user_id} не знайдений.")

        if book.is_available or book.borrowed_by != dto.user_id:
            raise BookNotBorrowedByUserError(
                f"Книга '{book.title}' не була позичена користувачем id={dto.user_id}."
            )

        book.is_available = True
        book.borrowed_by = None
        self._book_repo.save(book)

        if dto.book_id in user.borrowed_book_ids:
            user.borrowed_book_ids.remove(dto.book_id)
        self._user_repo.save(user)

        return book

    # Сценарій 4: Пошук книги

    def find_book_by_title(self, title: str) -> List[Book]:
        """
        Шукає книги за частковим збігом назви (без урахування регістру).

        Raises:
            ValueError: якщо пошуковий рядок порожній.
        """
        if not title or not title.strip():
            raise ValueError("Пошуковий запит не може бути порожнім.")
        return self._book_repo.find_by_title(title.strip())

    def find_book_by_author(self, author: str) -> List[Book]:
        """
        Шукає книги за частковим збігом імені автора (без урахування регістру).

        Raises:
            ValueError: якщо пошуковий рядок порожній.
        """
        if not author or not author.strip():
            raise ValueError("Ім'я автора не може бути порожнім.")
        return self._book_repo.find_by_author(author.strip())

    def get_all_books(self) -> List[Book]:
        """Повертає всі книги бібліотеки."""
        return self._book_repo.get_all()

    def add_book(self, title: str, author: str, isbn: str) -> Book:
        """Додає нову книгу до фонду бібліотеки."""
        if not title.strip() or not author.strip() or not isbn.strip():
            raise ValueError("Назва, автор та ISBN не можуть бути порожніми.")
        return self._book_repo.add(title=title.strip(), author=author.strip(), isbn=isbn.strip())
