from src.controllers.library_controller import LibraryController
from src.repositories.book_repository import BookRepository
from src.repositories.user_repository import UserRepository
from src.services.library_service import LibraryService


def main() -> None:
    book_repo = BookRepository()
    user_repo = UserRepository()
    service = LibraryService(book_repo=book_repo, user_repo=user_repo)
    controller = LibraryController(service=service)

    service.add_book("Кобзар", "Тарас Шевченко", "978-966-000-001")
    service.add_book("Тіні забутих предків", "Михайло Коцюбинський", "978-966-000-002")
    service.add_book("Лісова пісня", "Леся Українка", "978-966-000-003")

    print("БІБЛІОТЕЧНА СИСТЕМА")

    controller.cmd_list_books()
    print()

    controller.cmd_register_user("Іван Петренко", "ivan@example.com")
    controller.cmd_register_user("", "bad@example.com")           # помилка
    controller.cmd_register_user("Іван Петренко", "ivan@example.com")  # дублікат
    print()

    controller.cmd_issue_book(book_id=1, user_id=1)
    controller.cmd_issue_book(book_id=1, user_id=1)   # вже позичена
    controller.cmd_issue_book(book_id=99, user_id=1)  # не існує
    print()

    controller.cmd_find_by_title("Кобз")
    controller.cmd_find_by_title("Гаррі Поттер")
    print()

    controller.cmd_return_book(book_id=1, user_id=1)
    controller.cmd_return_book(book_id=1, user_id=1)  # вже повернута
    print()

    controller.cmd_list_books()


if __name__ == "__main__":
    main()
