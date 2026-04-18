from dataclasses import dataclass, field
from typing import List


@dataclass
class User:

    user_id: int
    name: str
    email: str
    borrowed_book_ids: List[int] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, name='{self.name}', email='{self.email}')"
