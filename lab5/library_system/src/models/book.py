from dataclasses import dataclass
from typing import Optional


@dataclass
class Book:

    book_id: int
    title: str
    author: str
    isbn: str
    is_available: bool = True
    borrowed_by: Optional[int] = None  # user_id або None

    def __repr__(self) -> str:
        status = "доступна" if self.is_available else f"позичена (user_id={self.borrowed_by})"
        return f"Book(id={self.book_id}, title='{self.title}', author='{self.author}', {status})"
