from src.dto import IssueBookDTO, RegisterUserDTO, ReturnBookDTO
from src.services.library_service import (
    BookAlreadyBorrowedError,
    BookNotBorrowedByUserError,
    BookNotFoundError,
    EmailAlreadyRegisteredError,
    LibraryService,
    UserNotFoundError,
)


class LibraryController:
    """
    Контролер обробляє введення користувача та викликає сервіси.
    Не містить бізнес-логіки — лише координує виклики та форматує виведення.
    """

    def __init__(self, service: LibraryService) -> None:
        self._service = service

    def cmd_register_user(self, name: str, email: str) -> None:
        try:
            user = self._service.register_user(RegisterUserDTO(name=name, email=email))
            print(f"Користувача зареєстровано: {user}")
        except (ValueError, EmailAlreadyRegisteredError) as exc:
            print(f"Помилка реєстрації: {exc}")

    def cmd_issue_book(self, book_id: int, user_id: int) -> None:
        try:
            book = self._service.issue_book(IssueBookDTO(book_id=book_id, user_id=user_id))
            print(f"Книгу видано: {book}")
        except (BookNotFoundError, UserNotFoundError, BookAlreadyBorrowedError) as exc:
            print(f"Помилка видачі: {exc}")

    def cmd_return_book(self, book_id: int, user_id: int) -> None:
        try:
            book = self._service.return_book(ReturnBookDTO(book_id=book_id, user_id=user_id))
            print(f"Книгу повернено: {book}")
        except (BookNotFoundError, UserNotFoundError, BookNotBorrowedByUserError) as exc:
            print(f"Помилка повернення: {exc}")

    def cmd_find_by_title(self, title: str) -> None:
        """Команда CLI: пошук книги за назвою."""
        try:
            books = self._service.find_book_by_title(title)
            if books:
                print(f"Знайдено {len(books)} книг(и):")
                for book in books:
                    print(f"   {book}")
            else:
                print(f"Книг із назвою '{title}' не знайдено.")
        except ValueError as exc:
            print(f"Помилка пошуку: {exc}")

    def cmd_list_books(self) -> None:
        """Команда CLI: перелік усіх книг."""
        books = self._service.get_all_books()
        if not books:
            print("Бібліотека порожня.")
            return
        print(f"Усього книг: {len(books)}")
        for book in books:
            print(f"   {book}")
