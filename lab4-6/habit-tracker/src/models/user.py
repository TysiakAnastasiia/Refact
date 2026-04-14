from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class User:
    """Represents a user of the habit tracking system. (SRP: only stores user data)"""
    name: str
    email: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self):
        if not self.name or not self.name.strip():
            raise ValueError("User name cannot be empty")
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, email={self.email!r})"
