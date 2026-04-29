from typing import Optional, Sequence
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Review, Exchange, WishlistItem, Message, ExchangeStatus, Book, Friendship
from app.repositories.base import BaseRepository
from app.repositories.book import BookRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, db: AsyncSession):
        super().__init__(Review, db)

    async def get_by_book(self, book_id: int, skip: int = 0, limit: int = 20) -> Sequence[Review]:
        result = await self.db.execute(
            select(Review)
            .options(selectinload(Review.user))
            .where(Review.book_id == book_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user(self, user_id: int) -> Sequence[Review]:
        result = await self.db.execute(
            select(Review)
            .options(selectinload(Review.user), selectinload(Review.book))
            .where(Review.user_id == user_id)
            .order_by(Review.created_at.desc())
        )
        return result.scalars().all()

    async def get_user_review_for_book(self, user_id: int, book_id: int) -> Optional[Review]:
        result = await self.db.execute(
            select(Review).where(
                and_(Review.user_id == user_id, Review.book_id == book_id)
            )
        )
        return result.scalar_one_or_none()


class ExchangeRepository(BaseRepository[Exchange]):
    def __init__(self, db: AsyncSession):
        super().__init__(Exchange, db)

    async def get_with_details(self, exchange_id: int) -> Optional[Exchange]:
        result = await self.db.execute(
            select(Exchange)
            .options(
                selectinload(Exchange.requester),
                selectinload(Exchange.owner),
                selectinload(Exchange.offered_book).selectinload(Book.owner),
                selectinload(Exchange.requested_book).selectinload(Book.owner),
            )
            .where(Exchange.id == exchange_id)
        )
        return result.scalar_one_or_none()

    async def get_for_user(self, user_id: int) -> Sequence[Exchange]:
        result = await self.db.execute(
            select(Exchange)
            .options(
                selectinload(Exchange.requester),
                selectinload(Exchange.owner),
                selectinload(Exchange.offered_book).selectinload(Book.owner),
                selectinload(Exchange.requested_book).selectinload(Book.owner),
            )
            .where(
                (Exchange.requester_id == user_id) | (Exchange.owner_id == user_id)
            )
            .order_by(Exchange.created_at.desc())
        )
        return result.scalars().all()

    async def get_all_with_details(self, skip: int = 0, limit: int = 20) -> Sequence[Exchange]:
        result = await self.db.execute(
            select(Exchange)
            .options(
                selectinload(Exchange.requester),
                selectinload(Exchange.owner),
                selectinload(Exchange.offered_book).selectinload(Book.owner),
                selectinload(Exchange.requested_book).selectinload(Book.owner),
            )
            .where(Exchange.status == ExchangeStatus.pending)
            .order_by(Exchange.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_between_users(self, user1_id: int, user2_id: int) -> Sequence[Exchange]:
        result = await self.db.execute(
            select(Exchange)
            .options(
                selectinload(Exchange.requester),
                selectinload(Exchange.owner),
                selectinload(Exchange.offered_book).selectinload(Book.owner),
                selectinload(Exchange.requested_book).selectinload(Book.owner),
            )
            .where(
                (Exchange.requester_id == user1_id) & (Exchange.owner_id == user2_id) |
                (Exchange.requester_id == user2_id) & (Exchange.owner_id == user1_id)
            )
            .order_by(Exchange.created_at.desc())
        )
        return result.scalars().all()


class WishlistRepository(BaseRepository[WishlistItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(WishlistItem, db)

    async def get_user_wishlist(self, user_id: int) -> Sequence[WishlistItem]:
        result = await self.db.execute(
            select(WishlistItem)
            .options(
                selectinload(WishlistItem.book).selectinload(Book.owner)
            )
            .where(WishlistItem.user_id == user_id)
            .order_by(WishlistItem.added_at.desc())
        )
        return result.scalars().all()

    async def get_item(self, user_id: int, book_id: int) -> Optional[WishlistItem]:
        result = await self.db.execute(
            select(WishlistItem).where(
                and_(WishlistItem.user_id == user_id, WishlistItem.book_id == book_id)
            )
        )
        return result.scalar_one_or_none()


class MessageRepository(BaseRepository[Message]):
    def __init__(self, db: AsyncSession):
        super().__init__(Message, db)

    async def get_exchange_messages(self, exchange_id: int) -> Sequence[Message]:
        result = await self.db.execute(
            select(Message)
            .options(selectinload(Message.sender))
            .where(Message.exchange_id == exchange_id)
            .order_by(Message.created_at.asc())
        )
        return result.scalars().all()


class FriendshipRepository(BaseRepository[Friendship]):
    def __init__(self, db: AsyncSession):
        super().__init__(Friendship, db)

    async def get_friendship(self, user1_id: int, user2_id: int) -> Optional[Friendship]:
        result = await self.db.execute(
            select(Friendship).where(
                (Friendship.requester_id == user1_id) & (Friendship.addressee_id == user2_id) |
                (Friendship.requester_id == user2_id) & (Friendship.addressee_id == user1_id)
            )
        )
        return result.scalar_one_or_none()

    async def create_friendship(self, requester_id: int, addressee_id: int) -> Friendship:
        friendship = Friendship(requester_id=requester_id, addressee_id=addressee_id, status="accepted")
        return await self.create(friendship)

    async def get_user_friends(self, user_id: int) -> Sequence[User]:
        result = await self.db.execute(
            select(User)
            .join(Friendship, (
                (Friendship.requester_id == user_id) & (Friendship.status == "accepted") |
                (Friendship.addressee_id == user_id) & (Friendship.status == "accepted")
            ))
            .where(
                (User.id == Friendship.addressee_id) | (User.id == Friendship.requester_id)
            )
            .where(User.id != user_id)
        )
        return result.scalars().all()
