import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


#  User 

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(200))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    books: Mapped[list["Book"]] = relationship("Book", back_populates="owner", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    wishlist_items: Mapped[list["WishlistItem"]] = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")
    sent_exchanges: Mapped[list["Exchange"]] = relationship("Exchange", foreign_keys="Exchange.requester_id", back_populates="requester")
    received_exchanges: Mapped[list["Exchange"]] = relationship("Exchange", foreign_keys="Exchange.owner_id", back_populates="owner")
    sent_messages: Mapped[list["Message"]] = relationship("Message", back_populates="sender")


#  Book 

class BookGenre(str, enum.Enum):
    fiction = "fiction"
    non_fiction = "non_fiction"
    fantasy = "fantasy"
    sci_fi = "sci_fi"
    mystery = "mystery"
    romance = "romance"
    thriller = "thriller"
    horror = "horror"
    biography = "biography"
    history = "history"
    science = "science"
    self_help = "self_help"
    children = "children"
    poetry = "poetry"
    other = "other"


class BookCondition(str, enum.Enum):
    new = "new"
    good = "good"
    fair = "fair"
    poor = "poor"


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    isbn: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    cover_url: Mapped[Optional[str]] = mapped_column(String(500))
    genre: Mapped[BookGenre] = mapped_column(Enum(BookGenre), nullable=False)
    published_year: Mapped[Optional[int]] = mapped_column(Integer)
    language: Mapped[str] = mapped_column(String(50), default="Ukrainian")
    condition: Mapped[BookCondition] = mapped_column(Enum(BookCondition), default=BookCondition.good)
    is_available_for_exchange: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    owner: Mapped["User"] = relationship("User", back_populates="books")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="book", cascade="all, delete-orphan")
    wishlist_items: Mapped[list["WishlistItem"]] = relationship("WishlistItem", back_populates="book")
    exchange_offers: Mapped[list["Exchange"]] = relationship("Exchange", foreign_keys="Exchange.offered_book_id", back_populates="offered_book")
    exchange_requests: Mapped[list["Exchange"]] = relationship("Exchange", foreign_keys="Exchange.requested_book_id", back_populates="requested_book")


#  Review 

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    content: Mapped[Optional[str]] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="reviews")
    book: Mapped["Book"] = relationship("Book", back_populates="reviews")


#  Exchange 

class ExchangeStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    completed = "completed"
    rejected = "rejected"
    cancelled = "cancelled"


class Exchange(Base):
    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    requester_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    offered_book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    requested_book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    status: Mapped[ExchangeStatus] = mapped_column(Enum(ExchangeStatus), default=ExchangeStatus.pending)
    message: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now())

    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id], back_populates="sent_exchanges")
    owner: Mapped["User"] = relationship("User", foreign_keys=[owner_id], back_populates="received_exchanges")
    offered_book: Mapped["Book"] = relationship("Book", foreign_keys=[offered_book_id], back_populates="exchange_offers")
    requested_book: Mapped["Book"] = relationship("Book", foreign_keys=[requested_book_id], back_populates="exchange_requests")
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="exchange")


#  Wishlist 

class WishlistItem(Base):
    __tablename__ = "wishlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="wishlist_items")
    book: Mapped["Book"] = relationship("Book", back_populates="wishlist_items")


#  Message 

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey("exchanges.id"), nullable=False)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    exchange: Mapped["Exchange"] = relationship("Exchange", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="sent_messages")
