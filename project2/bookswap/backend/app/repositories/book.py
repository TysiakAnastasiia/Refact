from typing import Optional, Sequence
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Book, Review, BookGenre
from app.repositories.base import BaseRepository


class BookRepository(BaseRepository[Book]):
    def __init__(self, db: AsyncSession):
        super().__init__(Book, db)

    async def get_with_owner(self, book_id: int) -> Optional[Book]:
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.owner))
            .where(Book.id == book_id)
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        query: Optional[str] = None,
        genre: Optional[BookGenre] = None,
        available_only: bool = False,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[Sequence[Book], int]:
        filters = []

        if query:
            filters.append(
                or_(
                    Book.title.ilike(f"%{query}%"),
                    Book.author.ilike(f"%{query}%"),
                )
            )
        if genre:
            filters.append(Book.genre == genre)
        if available_only:
            filters.append(Book.is_available_for_exchange == True)

        base_q = select(Book).options(selectinload(Book.owner))
        if filters:
            base_q = base_q.where(and_(*filters))

        total_result = await self.db.execute(
            select(func.count()).select_from(base_q.subquery())
        )
        total = total_result.scalar_one()

        result = await self.db.execute(
            base_q.order_by(Book.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def get_average_rating(self, book_id: int) -> Optional[float]:
        result = await self.db.execute(
            select(func.avg(Review.rating)).where(Review.book_id == book_id)
        )
        val = result.scalar_one_or_none()
        return round(float(val), 2) if val else None

    async def get_review_count(self, book_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).where(Review.book_id == book_id)
        )
        return result.scalar_one()

    async def get_by_owner(self, owner_id: int) -> Sequence[Book]:
        result = await self.db.execute(
            select(Book)
            .options(selectinload(Book.owner))
            .where(Book.owner_id == owner_id)
            .order_by(Book.created_at.desc())
        )
        return result.scalars().all()
