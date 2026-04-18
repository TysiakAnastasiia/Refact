from dataclasses import dataclass


@dataclass
class RegisterUserDTO:

    name: str
    email: str


@dataclass
class IssueBookDTO:

    book_id: int
    user_id: int


@dataclass
class ReturnBookDTO:

    book_id: int
    user_id: int
