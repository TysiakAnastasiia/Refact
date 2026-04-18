import pytest

from src.dto import IssueBookDTO, RegisterUserDTO, ReturnBookDTO
from src.repositories.book_repository import BookRepository
from src.repositories.user_repository import UserRepository
from src.services.library_service import (
    BookAlreadyBorrowedError,
    BookNotBorrowedByUserError,
    BookNotFoundError,
    EmailAlreadyRegisteredError,
    LibraryService,
    UserNotFoundError,
)


@pytest.fixture
def service() -> LibraryService:
    book_repo = BookRepository()
    user_repo = UserRepository()
    return LibraryService(book_repo=book_repo, user_repo=user_repo)


@pytest.fixture
def service_with_data(service: LibraryService):
    service.add_book("Кобзар", "Тарас Шевченко", "978-966-000-001")
    service.add_book("Тіні забутих предків", "Михайло Коцюбинський", "978-966-000-002")
    service.register_user(RegisterUserDTO(name="Іван Франко", email="ivan@example.com"))
    return service


class TestRegisterUser:

    def test_register_user_success(self, service: LibraryService) -> None:
        dto = RegisterUserDTO(name="Леся Українка", email="lesya@example.com")
        user = service.register_user(dto)

        assert user.user_id == 1
        assert user.name == "Леся Українка"
        assert user.email == "lesya@example.com"
        assert user.borrowed_book_ids == []

    def test_register_user_duplicate_email_raises(self, service: LibraryService) -> None:
        dto = RegisterUserDTO(name="Перший", email="same@example.com")
        service.register_user(dto)

        with pytest.raises(EmailAlreadyRegisteredError):
            service.register_user(RegisterUserDTO(name="Другий", email="same@example.com"))

    def test_register_user_empty_name_raises(self, service: LibraryService) -> None:
        with pytest.raises(ValueError):
            service.register_user(RegisterUserDTO(name="  ", email="ok@example.com"))


class TestIssueBook:

    def test_issue_book_success(self, service_with_data: LibraryService) -> None:
        book = service_with_data.issue_book(IssueBookDTO(book_id=1, user_id=1))

        assert book.is_available is False
        assert book.borrowed_by == 1

        user = service_with_data._user_repo.get_by_id(1)
        assert 1 in user.borrowed_book_ids

    def test_issue_already_borrowed_book_raises(self, service_with_data: LibraryService) -> None:
        service_with_data.issue_book(IssueBookDTO(book_id=1, user_id=1))

        service_with_data.register_user(RegisterUserDTO(name="Другий", email="other@example.com"))

        with pytest.raises(BookAlreadyBorrowedError):
            service_with_data.issue_book(IssueBookDTO(book_id=1, user_id=2))

    def test_issue_book_nonexistent_book_raises(self, service_with_data: LibraryService) -> None:
        with pytest.raises(BookNotFoundError):
            service_with_data.issue_book(IssueBookDTO(book_id=999, user_id=1))

    def test_issue_book_nonexistent_user_raises(self, service_with_data: LibraryService) -> None:
        with pytest.raises(UserNotFoundError):
            service_with_data.issue_book(IssueBookDTO(book_id=1, user_id=999))


class TestReturnBook:

    def test_return_book_success(self, service_with_data: LibraryService) -> None:
        service_with_data.issue_book(IssueBookDTO(book_id=1, user_id=1))
        book = service_with_data.return_book(ReturnBookDTO(book_id=1, user_id=1))

        assert book.is_available is True
        assert book.borrowed_by is None

        user = service_with_data._user_repo.get_by_id(1)
        assert 1 not in user.borrowed_book_ids

    def test_return_book_not_borrowed_by_user_raises(
        self, service_with_data: LibraryService
    ) -> None:
        service_with_data.register_user(RegisterUserDTO(name="Другий", email="other@example.com"))
        service_with_data.issue_book(IssueBookDTO(book_id=1, user_id=1))

        with pytest.raises(BookNotBorrowedByUserError):
            service_with_data.return_book(ReturnBookDTO(book_id=1, user_id=2))

    def test_return_available_book_raises(self, service_with_data: LibraryService) -> None:
        with pytest.raises(BookNotBorrowedByUserError):
            service_with_data.return_book(ReturnBookDTO(book_id=1, user_id=1))


class TestFindBook:

    def test_find_book_by_title_success(self, service_with_data: LibraryService) -> None:
        results = service_with_data.find_book_by_title("Кобз")
        assert len(results) == 1
        assert results[0].title == "Кобзар"

    def test_find_book_by_author_success(self, service_with_data: LibraryService) -> None:
        results = service_with_data.find_book_by_author("Шевченко")
        assert len(results) == 1
        assert results[0].author == "Тарас Шевченко"

    def test_find_book_not_found_returns_empty(self, service_with_data: LibraryService) -> None:
        results = service_with_data.find_book_by_title("Гаррі Поттер")
        assert results == []

    def test_find_book_empty_query_raises(self, service_with_data: LibraryService) -> None:
        with pytest.raises(ValueError):
            service_with_data.find_book_by_title("   ")
