"""
Seed script — populates the DB with sample data for development.
Run: python -m app.db.seed
"""

import asyncio

from app.db.session import AsyncSessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models import User, Book, Review, BookGenre, BookCondition


SAMPLE_USERS = [
    {
        "email": "alice@bookswap.ua",
        "username": "alice_reads",
        "full_name": "Аліса Книжкова",
        "city": "Київ",
    },
    {
        "email": "bob@bookswap.ua",
        "username": "bob_pages",
        "full_name": "Боб Читальний",
        "city": "Львів",
    },
    {
        "email": "carol@bookswap.ua",
        "username": "carol_lit",
        "full_name": "Кароль Лісова",
        "city": "Одеса",
    },
]

SAMPLE_BOOKS = [
    {
        "title": "Майстер і Маргарита",
        "author": "Михайло Булгаков",
        "genre": BookGenre.fiction,
        "condition": BookCondition.good,
        "description": "Один з найвидатніших романів XX століття, де переплітаються сатира, містика та філософія.",
        "published_year": 1967,
        "language": "Ukrainian",
        "is_available_for_exchange": True,
    },
    {
        "title": "Гаррі Поттер і філософський камінь",
        "author": "Джоан Роулінг",
        "genre": BookGenre.fantasy,
        "condition": BookCondition.good,
        "description": "Перша книга з серії про юного чарівника Гаррі Поттера.",
        "published_year": 1997,
        "language": "Ukrainian",
        "is_available_for_exchange": True,
    },
    {
        "title": "1984",
        "author": "Джордж Орвелл",
        "genre": BookGenre.fiction,
        "condition": BookCondition.new,
        "description": "Антиутопічний роман про тоталітарне суспільство під керівництвом Великого Брата.",
        "published_year": 1949,
        "language": "Ukrainian",
        "is_available_for_exchange": True,
    },
    {
        "title": "Дюна",
        "author": "Френк Герберт",
        "genre": BookGenre.sci_fi,
        "condition": BookCondition.fair,
        "description": "Епічна наукова фантастика про пустельну планету Арракіс і боротьбу за владу.",
        "published_year": 1965,
        "language": "Ukrainian",
        "is_available_for_exchange": False,
    },
    {
        "title": "Злочин і кара",
        "author": "Федір Достоєвський",
        "genre": BookGenre.fiction,
        "condition": BookCondition.good,
        "description": "Психологічний роман про студента Раскольнікова та його внутрішню боротьбу.",
        "published_year": 1866,
        "language": "Ukrainian",
        "is_available_for_exchange": True,
    },
    {
        "title": "Атлант розправив плечі",
        "author": "Айн Ренд",
        "genre": BookGenre.fiction,
        "condition": BookCondition.good,
        "description": "Роман-антиутопія про капіталізм, індивідуалізм та силу розуму.",
        "published_year": 1957,
        "language": "Ukrainian",
        "is_available_for_exchange": True,
    },
    {
        "title": "Сапієнс: Коротка історія людства",
        "author": "Юваль Ной Гарарі",
        "genre": BookGenre.non_fiction,
        "condition": BookCondition.new,
        "description": "Огляд еволюції Homo sapiens від кам'яного віку до сучасності.",
        "published_year": 2011,
        "language": "Ukrainian",
        "is_available_for_exchange": True,
    },
    {
        "title": "Кобзар",
        "author": "Тарас Шевченко",
        "genre": BookGenre.poetry,
        "condition": BookCondition.good,
        "description": "Збірка поетичних творів видатного українського поета.",
        "published_year": 1840,
        "language": "Ukrainian",
        "is_available_for_exchange": False,
    },
]

SAMPLE_REVIEWS = [
    {
        "book_idx": 0,
        "user_idx": 1,
        "rating": 5,
        "content": "Геніальний твір! Читав на одному диханні, не міг відірватися.",
    },
    {
        "book_idx": 0,
        "user_idx": 2,
        "rating": 4,
        "content": "Чудова книга, але потребує уважного читання. Дуже багато смислових шарів.",
    },
    {
        "book_idx": 1,
        "user_idx": 0,
        "rating": 5,
        "content": "Магічний світ, неймовірна фантазія автора. Рекомендую всім!",
    },
    {
        "book_idx": 2,
        "user_idx": 1,
        "rating": 5,
        "content": "Актуально навіть сьогодні. Моторошно, наскільки точно передбачено.",
    },
    {
        "book_idx": 3,
        "user_idx": 2,
        "rating": 4,
        "content": "Складна але захоплива книга. Потрібна терпіння на початку.",
    },
    {
        "book_idx": 6,
        "user_idx": 0,
        "rating": 5,
        "content": "Змінила моє розуміння людської цивілізації. Обов'язкова до прочитання.",
    },
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Check if already seeded
        from sqlalchemy import select

        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("⚠️  Database already seeded, skipping.")
            return

        # Create users
        users = []
        for u in SAMPLE_USERS:
            user = User(
                **u,
                hashed_password=get_password_hash("password123"),
                is_active=True,
            )
            session.add(user)
            users.append(user)
        await session.flush()

        # Create books
        books = []
        for i, b in enumerate(SAMPLE_BOOKS):
            book = Book(**b, owner_id=users[i % len(users)].id)
            session.add(book)
            books.append(book)
        await session.flush()

        # Create reviews
        for r in SAMPLE_REVIEWS:
            review = Review(
                book_id=books[r["book_idx"]].id,
                user_id=users[r["user_idx"]].id,
                rating=r["rating"],
                content=r["content"],
            )
            session.add(review)

        await session.commit()
        print(
            f"Seeded {len(users)} users, {len(books)} books, {len(SAMPLE_REVIEWS)} reviews."
        )
        print(" Login: alice@bookswap.ua / password123")


if __name__ == "__main__":
    asyncio.run(seed())
