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
    WishlistRepository, MessageRepository, FriendshipRepository,
)
from app.core.observer import event_manager, Event, EventType
from app.schemas import (
    UserRegister, UserUpdate, BookCreate, BookUpdate,
    ReviewCreate, ReviewUpdate, ExchangeCreate, MessageCreate,
)


# ─── Auth Service ─────────────────────────────────────────────────────────────

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserRegister) -> dict:
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        existing_username = await self.user_repo.get_by_username(user_data.username)
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")

        # Create new user
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
            bio=user_data.bio,
            city=user_data.city,
        )
        created_user = await self.user_repo.create(user)

        # Emit user registration event
        await event_manager.notify(Event(
            EventType.USER_REGISTERED,
            {
                'user_id': created_user.id,
                'username': created_user.username,
                'email': created_user.email,
                'full_name': created_user.full_name
            }
        ))

        # Generate tokens
        access_token = create_access_token(created_user.id)
        refresh_token = create_refresh_token(created_user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": created_user,
        }

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

    async def search_books(self, query=None, genre=None, available_only=False, owner_id=None, page=1, page_size=20):
        skip = (page - 1) * page_size
        books, total = await self.book_repo.search(query, genre, available_only, owner_id, skip, page_size)

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

        # Перевіряємо пропоновану книгу, якщо вона вказана
        if data.offered_book_id:
            offered_book = await self.book_repo.get(data.offered_book_id)
            if not offered_book or offered_book.owner_id != requester_id:
                raise HTTPException(status_code=403, detail="Offered book must be yours")

        exchange = Exchange(
            requester_id=requester_id,
            owner_id=requested_book.owner_id,
            offered_book_id=data.offered_book_id,
            requested_book_id=data.requested_book_id,
            message=data.message,
        )
        created_exchange = await self.exchange_repo.create(exchange)
        
        # Emit exchange creation event
        await event_manager.notify(Event(
            EventType.EXCHANGE_CREATED,
            {
                'exchange_id': created_exchange.id,
                'requester_id': created_exchange.requester_id,
                'owner_id': created_exchange.owner_id,
                'offered_book_id': created_exchange.offered_book_id,
                'requested_book_id': created_exchange.requested_book_id,
                'status': created_exchange.status.value
            }
        ))
        
        # Load relationships for response schema
        return await self.exchange_repo.get_with_details(created_exchange.id)

    async def update_status(self, exchange_id: int, new_status: ExchangeStatus, user_id: int) -> Exchange:
        exchange = await self.exchange_repo.get(exchange_id)
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")
        if exchange.owner_id != user_id and exchange.requester_id != user_id:
            raise HTTPException(status_code=403, detail="Not your exchange")
        exchange.status = new_status
        await self.exchange_repo.update(exchange)
        
        # Emit exchange status update event
        event_type = None
        if new_status == ExchangeStatus.accepted:
            event_type = EventType.EXCHANGE_ACCEPTED
        elif new_status == ExchangeStatus.completed:
            event_type = EventType.EXCHANGE_COMPLETED
        
        if event_type:
            await event_manager.notify(Event(
                event_type,
                {
                    'exchange_id': exchange.id,
                    'requester_id': exchange.requester_id,
                    'owner_id': exchange.owner_id,
                    'old_status': exchange.status.value,
                    'new_status': new_status.value,
                    'updated_by_user_id': user_id
                }
            ))
        
        # Load relationships for response schema
        return await self.exchange_repo.get_with_details(exchange_id)


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
        created_message = await self.message_repo.create(msg)
        
        # Emit message sent event
        await event_manager.notify(Event(
            EventType.MESSAGE_SENT,
            {
                'message_id': created_message.id,
                'exchange_id': exchange_id,
                'sender_id': sender_id,
                'content': data.content,
                'created_at': created_message.created_at.isoformat()
            }
        ))
        
        return created_message

    async def get_messages(self, exchange_id: int, user_id: int):
        exchange = await self.exchange_repo.get(exchange_id)
        if not exchange:
            raise HTTPException(status_code=404, detail="Exchange not found")
        if user_id not in (exchange.requester_id, exchange.owner_id):
            raise HTTPException(status_code=403, detail="Access denied")
        return await self.message_repo.get_exchange_messages(exchange_id)


# ─── Friendship Service ─────────────────────────────────────────────────────────

class FriendshipService:
    def __init__(self, db: AsyncSession):
        self.friendship_repo = FriendshipRepository(db)

    async def add_friend(self, requester_id: int, addressee_id: int) -> dict:
        # Check if already friends
        existing = await self.friendship_repo.get_friendship(requester_id, addressee_id)
        if existing:
            raise HTTPException(status_code=400, detail="Already friends or request pending")
        
        if requester_id == addressee_id:
            raise HTTPException(status_code=400, detail="Cannot add yourself as friend")
        
        # Create friendship (automatically accepted for simplicity)
        friendship = Friendship(requester_id=requester_id, addressee_id=addressee_id, status="accepted")
        created_friendship = await self.friendship_repo.create(friendship)
        
        # Emit friend added event
        await event_manager.notify(Event(
            EventType.FRIEND_ADDED,
            {
                'friendship_id': created_friendship.id,
                'requester_id': requester_id,
                'addressee_id': addressee_id,
                'status': created_friendship.status,
                'created_at': created_friendship.created_at.isoformat()
            }
        ))
        
        return {"status": "success", "message": "Friend added successfully"}

    async def get_user_friends(self, user_id: int) -> Sequence[User]:
        return await self.friendship_repo.get_user_friends(user_id)
