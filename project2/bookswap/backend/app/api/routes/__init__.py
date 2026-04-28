"""
API Routes — thin controllers that delegate to service layer.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.models import User, BookGenre, ExchangeStatus
from app.services import (
    AuthService, UserService, BookService, ReviewService,
    ExchangeService, WishlistService, ChatService, FriendshipService,
)
from app.services.recommendations import RecommendationService
from app.schemas import (
    UserRegister, UserLogin, TokenResponse, UserBase, UserUpdate, UserPublic,
    BookCreate, BookUpdate, BookResponse, BookListResponse,
    ReviewCreate, ReviewUpdate, ReviewResponse,
    ExchangeCreate, ExchangeResponse,
    WishlistItemResponse,
    MessageCreate, MessageResponse,
    RecommendationResponse,
)
from app.repositories import ReviewRepository

router = APIRouter()


#  Auth 

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).register(data)


@auth_router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await AuthService(db).login(data.email, data.password)


#  Users 

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me", response_model=UserBase)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@users_router.patch("/me", response_model=UserBase)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await UserService(db).update_profile(current_user, data)


@users_router.get("/search", response_model=list[UserPublic])
async def search_users(
    q: str = Query(..., min_length=1, description="Search query"),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import or_, select
    result = await db.execute(
        select(User)
        .where(
            or_(
                User.username.ilike(f"%{q}%"),
                User.full_name.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
            )
        )
        .limit(20)
    )
    users = result.scalars().all()
    return users


@users_router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await UserService(db).get_user(user_id)


@users_router.get("/{user_id}/reviews", response_model=list[ReviewResponse])
async def get_user_reviews(user_id: int, db: AsyncSession = Depends(get_db)):
    return await ReviewRepository(db).get_by_user(user_id)


#  Books 

books_router = APIRouter(prefix="/books", tags=["Books"])


@books_router.get("", response_model=BookListResponse)
async def list_books(
    q: Optional[str] = Query(None, description="Search by title or author"),
    genre: Optional[BookGenre] = None,
    available_only: bool = False,
    owner_id: Optional[int] = Query(None, description="Filter by owner ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = BookService(db)
    books, total = await service.search_books(q, genre, available_only, owner_id, page, page_size)
    pages = (total + page_size - 1) // page_size
    return {"items": books, "total": total, "page": page, "page_size": page_size, "pages": pages}


@books_router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    service = BookService(db)
    book = await service.get_book(book_id)
    book.average_rating = await service.book_repo.get_average_rating(book_id)
    book.review_count = await service.book_repo.get_review_count(book_id)
    return book


@books_router.post("", response_model=BookResponse, status_code=201)
async def create_book(
    data: BookCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await BookService(db).create_book(data, current_user.id)


@books_router.patch("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    data: BookUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await BookService(db).update_book(book_id, data, current_user.id)


@books_router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await BookService(db).delete_book(book_id, current_user.id)


@books_router.get("/{book_id}/reviews", response_model=list[ReviewResponse])
async def get_book_reviews(
    book_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    return await ReviewService(db).get_book_reviews(book_id, skip, limit)


#  Reviews 

reviews_router = APIRouter(prefix="/reviews", tags=["Reviews"])


@reviews_router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ReviewService(db).create_review(data, current_user.id)


@reviews_router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ReviewService(db).update_review(review_id, data, current_user.id)


@reviews_router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ReviewService(db).delete_review(review_id, current_user.id)


#  Exchanges 

exchanges_router = APIRouter(prefix="/exchanges", tags=["Exchanges"])


@exchanges_router.get("", response_model=list[ExchangeResponse])
async def list_exchanges(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    from app.repositories import ExchangeRepository
    return await ExchangeRepository(db).get_all_with_details(skip, limit)


@exchanges_router.get("/my", response_model=list[ExchangeResponse])
async def my_exchanges(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories import ExchangeRepository
    return await ExchangeRepository(db).get_for_user(current_user.id)


@exchanges_router.get("/between", response_model=list[ExchangeResponse])
async def exchanges_between_users(
    user1: int = Query(..., description="First user ID"),
    user2: int = Query(..., description="Second user ID"),
    db: AsyncSession = Depends(get_db),
):
    from app.repositories import ExchangeRepository
    return await ExchangeRepository(db).get_between_users(user1, user2)


@exchanges_router.post("", response_model=ExchangeResponse, status_code=201)
async def create_exchange(
    data: ExchangeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ExchangeService(db).create_exchange(data, current_user.id)


@exchanges_router.patch("/{exchange_id}/accept", response_model=ExchangeResponse)
async def accept_exchange(
    exchange_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ExchangeService(db).update_status(exchange_id, ExchangeStatus.accepted, current_user.id)


@exchanges_router.patch("/{exchange_id}/reject", response_model=ExchangeResponse)
async def reject_exchange(
    exchange_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ExchangeService(db).update_status(exchange_id, ExchangeStatus.rejected, current_user.id)


@exchanges_router.patch("/{exchange_id}/complete", response_model=ExchangeResponse)
async def complete_exchange(
    exchange_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ExchangeService(db).update_status(exchange_id, ExchangeStatus.completed, current_user.id)


#  Wishlist 

wishlist_router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@wishlist_router.get("", response_model=list[WishlistItemResponse])
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await WishlistService(db).get_wishlist(current_user.id)


@wishlist_router.post("/{book_id}", response_model=WishlistItemResponse, status_code=201)
async def add_to_wishlist(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await WishlistService(db).add_to_wishlist(current_user.id, book_id)


@wishlist_router.delete("/{book_id}", status_code=204)
async def remove_from_wishlist(
    book_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await WishlistService(db).remove_from_wishlist(current_user.id, book_id)


#  Chat 

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


@chat_router.get("/{exchange_id}", response_model=list[MessageResponse])
async def get_messages(
    exchange_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ChatService(db).get_messages(exchange_id, current_user.id)


#  Friends 

friends_router = APIRouter(prefix="/friends", tags=["Friends"])


@friends_router.post("/{user_id}", status_code=201)
async def add_friend(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FriendshipService(db).add_friend(current_user.id, user_id)


@friends_router.get("", response_model=list[UserPublic])
async def get_friends(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await FriendshipService(db).get_user_friends(current_user.id)


@chat_router.post("/{exchange_id}", response_model=MessageResponse, status_code=201)
async def send_message(
    exchange_id: int,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ChatService(db).send_message(exchange_id, current_user.id, data)


#  Recommendations

recs_router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@recs_router.get("", response_model=list[RecommendationResponse])
async def get_recommendations(
    genres: Optional[str] = Query(None, description="Comma-separated genres"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    genre_list = [g.strip() for g in genres.split(",")] if genres else []

    # Get user's reviewed books as context
    review_repo = ReviewRepository(db)
    user_reviews = await review_repo.get_by_user(current_user.id)
    read_books = [f"{r.book.title} ({r.book.author})" for r in user_reviews[:10] if r.book]

    service = RecommendationService()
    return await service.get_recommendations(genre_list, read_books)
