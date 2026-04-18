from typing import Dict, List, Optional

from src.models.book import Book


class BookRepository:

    def __init__(self) -> None:
        self._books: Dict[int, Book] = {}
        self._next_id: int = 1

    def add(self, title: str, author: str, isbn: str) -> Book:
        book = Book(
            book_id=self._next_id,
            title=title,
            author=author,
            isbn=isbn,
        )
        self._books[self._next_id] = book
        self._next_id += 1
        return book

    def get_by_id(self, book_id: int) -> Optional[Book]:
        return self._books.get(book_id)

    def get_all(self) -> List[Book]:
        return list(self._books.values())

    def find_by_title(self, title: str) -> List[Book]:
        title_lower = title.lower()
        return [b for b in self._books.values() if title_lower in b.title.lower()]

    def find_by_author(self, author: str) -> List[Book]:
        author_lower = author.lower()
        return [b for b in self._books.values() if author_lower in b.author.lower()]

    def save(self, book: Book) -> Book:
        self._books[book.book_id] = book
        return book
