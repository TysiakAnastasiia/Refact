"""
Unit tests for services and utilities.
Run: pytest tests/ -v --cov=app
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.security import (
    get_password_hash, verify_password,
    create_access_token, decode_token,
)
from app.schemas import UserRegister, BookCreate, ReviewCreate, ExchangeCreate
from app.models import BookGenre, BookCondition, ExchangeStatus


# ─── Security tests ───────────────────────────────────────────────────────────

class TestSecurity:
    def test_password_hash_and_verify(self):
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct")
        assert not verify_password("wrong", hashed)

    def test_create_and_decode_access_token(self):
        data = {"sub": "42", "email": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_token(token)
        assert decoded["sub"] == "42"
        assert decoded["type"] == "access"

    def test_invalid_token_returns_none(self):
        result = decode_token("totally.invalid.token")
        assert result is None

    def test_token_contains_expiry(self):
        token = create_access_token({"sub": "1"})
        payload = decode_token(token)
        assert "exp" in payload


# ─── Schema validation tests ──────────────────────────────────────────────────

class TestSchemas:
    def test_user_register_valid(self):
        user = UserRegister(
            email="user@example.com",
            username="bookworm",
            password="Password123",
        )
        assert user.email == "user@example.com"

    def test_user_register_short_password_fails(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserRegister(email="u@e.com", username="abc", password="short")

    def test_user_register_invalid_email_fails(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            UserRegister(email="notanemail", username="abc", password="password123")

    def test_book_create_valid(self):
        book = BookCreate(
            title="Кобзар",
            author="Тарас Шевченко",
            genre=BookGenre.poetry,
            condition=BookCondition.good,
        )
        assert book.title == "Кобзар"

    def test_book_create_empty_title_fails(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            BookCreate(title="", author="Author", genre=BookGenre.fiction)

    def test_review_create_rating_bounds(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            ReviewCreate(book_id=1, rating=6)
        with pytest.raises(ValidationError):
            ReviewCreate(book_id=1, rating=0)

    def test_review_create_valid(self):
        r = ReviewCreate(book_id=1, rating=5, content="Чудова книга!")
        assert r.rating == 5

    def test_book_isbn_validation(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            BookCreate(title="T", author="A", genre=BookGenre.fiction, isbn="123")

    def test_book_isbn_valid_13(self):
        book = BookCreate(
            title="Test", author="Author",
            genre=BookGenre.fiction,
            isbn="9780306406157"
        )
        assert book.isbn == "9780306406157"


# ─── Auth Service tests ───────────────────────────────────────────────────────

class TestAuthService:
    @pytest.mark.asyncio
    async def test_register_duplicate_email_raises(self):
        from app.services import AuthService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = AuthService(mock_db)
        service.user_repo = AsyncMock()
        service.user_repo.get_by_email = AsyncMock(return_value=MagicMock())

        with pytest.raises(HTTPException) as exc:
            await service.register(UserRegister(
                email="existing@test.com",
                username="newuser",
                password="password123",
            ))
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_login_invalid_password_raises(self):
        from app.services import AuthService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        mock_user = MagicMock()
        mock_user.hashed_password = get_password_hash("correctpassword")
        mock_user.is_active = True
        service.user_repo = AsyncMock()
        service.user_repo.get_by_email = AsyncMock(return_value=mock_user)

        with pytest.raises(HTTPException) as exc:
            await service.login("user@test.com", "wrongpassword")
        assert exc.value.status_code == 401

    @pytest.mark.asyncio
    async def test_login_inactive_user_raises(self):
        from app.services import AuthService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = AuthService(mock_db)

        mock_user = MagicMock()
        mock_user.hashed_password = get_password_hash("password123")
        mock_user.is_active = False
        service.user_repo = AsyncMock()
        service.user_repo.get_by_email = AsyncMock(return_value=mock_user)

        with pytest.raises(HTTPException) as exc:
            await service.login("user@test.com", "password123")
        assert exc.value.status_code == 403


# ─── Book Service tests ───────────────────────────────────────────────────────

class TestBookService:
    @pytest.mark.asyncio
    async def test_get_nonexistent_book_raises_404(self):
        from app.services import BookService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = BookService(mock_db)
        service.book_repo = AsyncMock()
        service.book_repo.get_with_owner = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await service.get_book(9999)
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_book_wrong_owner_raises_403(self):
        from app.services import BookService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = BookService(mock_db)

        mock_book = MagicMock()
        mock_book.owner_id = 1
        service.book_repo = AsyncMock()
        service.book_repo.get_with_owner = AsyncMock(return_value=mock_book)

        with pytest.raises(HTTPException) as exc:
            await service.delete_book(1, user_id=2)  # wrong user
        assert exc.value.status_code == 403


# ─── Exchange Service tests ───────────────────────────────────────────────────

class TestExchangeService:
    @pytest.mark.asyncio
    async def test_cannot_request_own_book(self):
        from app.services import ExchangeService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = ExchangeService(mock_db)

        mock_book = MagicMock()
        mock_book.owner_id = 5
        mock_book.is_available_for_exchange = True
        service.book_repo = AsyncMock()
        service.book_repo.get = AsyncMock(return_value=mock_book)

        with pytest.raises(HTTPException) as exc:
            await service.create_exchange(
                ExchangeCreate(offered_book_id=2, requested_book_id=1),
                requester_id=5,  # same as owner
            )
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_unavailable_book_raises_400(self):
        from app.services import ExchangeService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = ExchangeService(mock_db)

        mock_book = MagicMock()
        mock_book.owner_id = 3
        mock_book.is_available_for_exchange = False
        service.book_repo = AsyncMock()
        service.book_repo.get = AsyncMock(return_value=mock_book)

        with pytest.raises(HTTPException) as exc:
            await service.create_exchange(
                ExchangeCreate(offered_book_id=2, requested_book_id=1),
                requester_id=7,
            )
        assert exc.value.status_code == 400


# ─── Review Service tests ─────────────────────────────────────────────────────

class TestReviewService:
    @pytest.mark.asyncio
    async def test_duplicate_review_raises_400(self):
        from app.services import ReviewService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = ReviewService(mock_db)
        service.review_repo = AsyncMock()
        service.review_repo.get_user_review_for_book = AsyncMock(return_value=MagicMock())

        with pytest.raises(HTTPException) as exc:
            await service.create_review(ReviewCreate(book_id=1, rating=5), user_id=1)
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_edit_others_review_raises_403(self):
        from app.services import ReviewService
        from app.schemas import ReviewUpdate
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = ReviewService(mock_db)
        mock_review = MagicMock()
        mock_review.user_id = 10
        service.review_repo = AsyncMock()
        service.review_repo.get = AsyncMock(return_value=mock_review)

        with pytest.raises(HTTPException) as exc:
            await service.update_review(1, ReviewUpdate(rating=3), user_id=99)
        assert exc.value.status_code == 403


# ─── Wishlist Service tests ───────────────────────────────────────────────────

class TestWishlistService:
    @pytest.mark.asyncio
    async def test_add_duplicate_raises_400(self):
        from app.services import WishlistService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = WishlistService(mock_db)
        service.wishlist_repo = AsyncMock()
        service.wishlist_repo.get_item = AsyncMock(return_value=MagicMock())

        with pytest.raises(HTTPException) as exc:
            await service.add_to_wishlist(user_id=1, book_id=5)
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_remove_nonexistent_raises_404(self):
        from app.services import WishlistService
        from fastapi import HTTPException

        mock_db = AsyncMock()
        service = WishlistService(mock_db)
        service.wishlist_repo = AsyncMock()
        service.wishlist_repo.get_item = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc:
            await service.remove_from_wishlist(user_id=1, book_id=5)
        assert exc.value.status_code == 404
