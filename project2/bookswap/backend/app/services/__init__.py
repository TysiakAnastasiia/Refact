"""
Service layer — business logic separated from HTTP concerns.
Each service depends on repositories injected via constructor (Dependency Injection).
"""
from typing import Optional, Sequence
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.models import User, Book, Review, Exchange, WishlistItem, Message, ExchangeStatus
from app.repositories.book import BookRepository
from app.repositories import (
    UserRepository, ReviewRepository, ExchangeRepository,
    WishlistRepository, MessageRepository,
)
from app.schemas import (
    UserRegister, UserUpdate, BookCreate, BookUpdate,
    ReviewCreate, ReviewUpdate, ExchangeCreate, MessageCreate,
)


# ─── Auth Service ─────────────────────────────────────────────────────────────

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register(self, data: UserRegister) -> dict:
        if await self.user_repo.get_by_email(data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if await self.user_repo.get_by_username(data.username):
            raise HTTPException(status_code=400, detail="Username already taken")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
        )
        user = await self.user_repo.create(user)
        return self._make_tokens(user)

    async def login(self, email: str, password: str) -> dict:
        user = await self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")
        return self._make_tokens(user)

    def _make_tokens(self, user: User) -> dict:
        payload = {"sub": str(user.id), "email": user.email}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer",
        }


# ─── User Service ─────────────────────────────────────────────────────────────

class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_profile(self, user: User, data: UserUpdate) -> User:
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)
        return await self.user_repo.update(user)


# ─── Book Service ─────────────────────────────────────────────────────────────

class BookService:
    def __init__(self, db: AsyncSession):
        self.book_repo = BookRepository(db)

    async def get_book(self, book_id: int) -> Book:
        book = await self.book_repo.get_with_owner(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return book

    async def create_book(self, data: BookCreate, owner_id: int) -> Book:
        book = Book(**data.model_dump(), owner_id=owner_id)
        return await self.book_repo.create(book)

    async def update_book(self, book_id: int, data: BookUpdate, user_id: int) -> Book:
        book = await self.get_book(book_id)
        if book.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Not your book")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(book, field, value)
        return await self.book_repo.update(book)

    async def delete_book(self, book_id: int, user_id: int) -> None:
        book = await self.get_book(book_id)
        if book.owner_id != user_id:
            raise HTTPException(status_code=403, detail="Not your book")
        await self.book_repo.delete(book)

    async def search_books(self, query=None, genre=None, available_only=False, page=1, page_size=20):
        skip = (page - 1) * page_size
        books, total = await self.book_repo.search(query, genre, available_only, skip, page_size)

        # Enrich with ratings
        enriched = []
        for book in books:
            avg = await self.book_repo.get_average_rating(book.id)
            count = await self.book_repo.get_review_count(book.id)
            book.average_rating = avg
            book.review_count = count
            enriched.append(book)

        return enriched, total


# ─── Review Service ───────────────────────────────────────────────────────────

class ReviewService:
    def __init__(self, db: AsyncSession):
        self.review_repo = ReviewRepository(db)
        self.book_repo = BookRepository(db)

    async def create_review(self, data: ReviewCreate, user_id: int) -> Review:
        existing = await self.review_repo.get_user_review_for_book(user_id, data.book_id)
        if existing:
            raise HTTPException(status_code=400, detail="You already reviewed this book")
        book = await self.book_repo.get(data.book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        review = Review(**data.model_dump(), user_id=user_id)
        return await self.review_repo.create(review)

    async def update_review(self, review_id: int, data: ReviewUpdate, user_id: int) -> Review:
        review = await self.review_repo.get(review_id)
        if not review:
            raise HTTPException(status_code=404, detail="Review not found")
        if review.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not your review")
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(review, field, value)
        return await self.review_repo.update(review)

    async def delete_review(self, review_id: int, user_id: int) -> None:
        review = await self.review_repo.get(review_id)
        if not review or review.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not allowed")
        await self.review_repo.delete(review)

    async def get_book_reviews(self, book_id: int, skip=0, limit=20) -> Sequence[Review]:
        return await self.review_repo.get_by_book(book_id, skip, limit)


# ─── Exchange Service ─────────────────────────────────────────────────────────

class ExchangeService:
    def __init__(self, db: AsyncSession):
        self.exchange_repo = ExchangeRepository(db)
        self.book_repo = BookRepository(db)

    async def create_exchange(self, data: ExchangeCreate, requester_id: int) -> Exchange:
        requested_book = await self.book_repo.get(data.requested_book_id)
        if not requested_book:
            raise HTTPException(status_code=404, detail="Requested book not found")
        if not requested_book.is_available_for_exchange:
            raise HTTPException(status_code=400, detail="Book not available for exchange")
        if requested_book.owner_id == requester_id:
            raise HTTPException(status_code=400, detail="Cannot request your own book")

        offered_book = await self.book_repo.get(data.offered_book_id)
        if not offered_book or offered_book.owner_id != requester_id:
            raise HTTPException(status_code=403, detail="Offered book must be yours")

        exchange = Exchange(
            requester_id=requester_id,
            owner_id=requested_book.owner_id,
            **data.model_dump(),
        )
        return await self.exchange_repo.create(exchange)

    async def update_status(self, exchange_id: int, new_status: ExchangeStatus, user_id: int) -> Exchange:
        exchange = await self.exchange_repo.get(exchange_id)
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")
        if exchange.owner_id != user_id and exchange.requester_id != user_id:
            raise HTTPException(status_code=403, detail="Not your exchange")
        exchange.status = new_status
        return await self.exchange_repo.update(exchange)


# ─── Wishlist Service ─────────────────────────────────────────────────────────

class WishlistService:
    def __init__(self, db: AsyncSession):
        self.wishlist_repo = WishlistRepository(db)

    async def add_to_wishlist(self, user_id: int, book_id: int) -> WishlistItem:
        existing = await self.wishlist_repo.get_item(user_id, book_id)
        if existing:
            raise HTTPException(status_code=400, detail="Already in wishlist")
        item = WishlistItem(user_id=user_id, book_id=book_id)
        await self.wishlist_repo.create(item)
        items = await self.wishlist_repo.get_user_wishlist(user_id)
        return next(i for i in items if i.book_id == book_id)

    async def remove_from_wishlist(self, user_id: int, book_id: int) -> None:
        item = await self.wishlist_repo.get_item(user_id, book_id)
        if not item:
            raise HTTPException(status_code=404, detail="Not in wishlist")
        await self.wishlist_repo.delete(item)

    async def get_wishlist(self, user_id: int):
        return await self.wishlist_repo.get_user_wishlist(user_id)


# ─── Chat Service ─────────────────────────────────────────────────────────────

class ChatService:
    def __init__(self, db: AsyncSession):
        self.message_repo = MessageRepository(db)
        self.exchange_repo = ExchangeRepository(db)

    async def send_message(self, exchange_id: int, sender_id: int, data: MessageCreate) -> Message:
        exchange = await self.exchange_repo.get(exchange_id)
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")
        if sender_id not in (exchange.requester_id, exchange.owner_id):
            raise HTTPException(status_code=403, detail="Not participant of this exchange")
        msg = Message(exchange_id=exchange_id, sender_id=sender_id, content=data.content)
        return await self.message_repo.create(msg)

    async def get_messages(self, exchange_id: int, user_id: int):
        exchange = await self.exchange_repo.get(exchange_id)
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")
        if user_id not in (exchange.requester_id, exchange.owner_id):
            raise HTTPException(status_code=403, detail="Access denied")
        return await self.message_repo.get_exchange_messages(exchange_id)
