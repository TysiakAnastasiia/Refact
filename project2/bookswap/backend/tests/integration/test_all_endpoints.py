"""
Comprehensive integration tests for all API endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock

from app.main import app
from app.core.security import get_password_hash
from app.models import User, Book, Review, Exchange, WishlistItem, Message, Friendship
from app.schemas import UserRegister, BookCreate, ReviewCreate, ExchangeCreate, MessageCreate


# ─── Test Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_db():
    """Create test database session."""
    # This would be set up in your test configuration
    pass


@pytest.fixture
async def test_user(test_db):
    """Create test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        bio="Test bio",
        city="Test City"
    )
    # In real implementation, save to test database
    return user


@pytest.fixture
async def auth_headers(client):
    """Get authentication headers."""
    # Register and login to get token
    register_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    }
    
    response = await client.post("/api/auth/register", json=register_data)
    assert response.status_code == 201
    
    login_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─── Authentication Endpoints Tests ─────────────────────────────────────────────

class TestAuthEndpoints:
    
    async def test_register_user_success(self, client):
        """Test successful user registration."""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User",
            "bio": "New user bio",
            "city": "New City"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["access_token"] is not None
        assert data["refresh_token"] is not None
        assert data["user"]["email"] == user_data["email"]
        assert data["user"]["username"] == user_data["username"]
    
    async def test_register_duplicate_email(self, client):
        """Test registration fails with duplicate email."""
        user_data = {
            "email": "duplicate@example.com",
            "username": "user1",
            "password": "password123",
            "full_name": "User 1"
        }
        
        # Register first user
        await client.post("/api/auth/register", json=user_data)
        
        # Try to register with same email
        user_data["username"] = "user2"
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
    
    async def test_login_success(self, client):
        """Test successful login."""
        # Register user first
        user_data = {
            "email": "login@example.com",
            "username": "loginuser",
            "password": "password123",
            "full_name": "Login User"
        }
        await client.post("/api/auth/register", json=user_data)
        
        # Login
        login_data = {
            "email": "login@example.com",
            "password": "password123"
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["access_token"] is not None
        assert data["refresh_token"] is not None
    
    async def test_login_invalid_credentials(self, client):
        """Test login fails with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await client.post("/api/auth/login", json=login_data)
        assert response.status_code == 401
    
    async def test_get_current_user(self, client, auth_headers):
        """Test getting current user info."""
        response = await client.get("/api/users/me", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "email" in data
        assert "username" in data
        assert data["email"] == "test@example.com"


# ─── User Endpoints Tests ───────────────────────────────────────────────────────

class TestUserEndpoints:
    
    async def test_search_users(self, client, auth_headers):
        """Test user search functionality."""
        response = await client.get("/api/users/search?q=test", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_user_by_id(self, client, auth_headers):
        """Test getting user by ID."""
        # First get current user to get ID
        me_response = await client.get("/api/users/me", headers=auth_headers)
        user_id = me_response.json()["id"]
        
        response = await client.get(f"/api/users/{user_id}", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == user_id
    
    async def test_update_user_profile(self, client, auth_headers):
        """Test updating user profile."""
        update_data = {
            "full_name": "Updated Name",
            "bio": "Updated bio",
            "city": "Updated City"
        }
        
        response = await client.patch("/api/users/me", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["full_name"] == "Updated Name"
        assert data["bio"] == "Updated bio"
        assert data["city"] == "Updated City"
    
    async def test_get_user_reviews(self, client, auth_headers):
        """Test getting user's reviews."""
        # First get current user to get ID
        me_response = await client.get("/api/users/me", headers=auth_headers)
        user_id = me_response.json()["id"]
        
        response = await client.get(f"/api/users/{user_id}/reviews", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


# ─── Book Endpoints Tests ───────────────────────────────────────────────────────

class TestBookEndpoints:
    
    async def test_create_book(self, client, auth_headers):
        """Test creating a new book."""
        book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "description": "Test Description",
            "isbn": "1234567890123",
            "genre": "fiction",
            "published_year": 2023,
            "language": "Ukrainian",
            "condition": "good"
        }
        
        response = await client.post("/api/books", json=book_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == book_data["title"]
        assert data["author"] == book_data["author"]
    
    async def test_get_books(self, client):
        """Test getting all books."""
        response = await client.get("/api/books")
        assert response.status_code == 200
        
        data = response.json()
        assert "books" in data
        assert "total" in data
        assert isinstance(data["books"], list)
    
    async def test_get_book_by_id(self, client, auth_headers):
        """Test getting book by ID."""
        # First create a book
        book_data = {
            "title": "Test Book for ID",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        create_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = create_response.json()["id"]
        
        # Get book by ID
        response = await client.get(f"/api/books/{book_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == book_id
        assert data["title"] == book_data["title"]
    
    async def test_update_book(self, client, auth_headers):
        """Test updating book information."""
        # First create a book
        book_data = {
            "title": "Book to Update",
            "author": "Test Author",
            "description": "Original Description"
        }
        
        create_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = create_response.json()["id"]
        
        # Update book
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description"
        }
        
        response = await client.patch(f"/api/books/{book_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"
    
    async def test_delete_book(self, client, auth_headers):
        """Test deleting a book."""
        # First create a book
        book_data = {
            "title": "Book to Delete",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        create_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = create_response.json()["id"]
        
        # Delete book
        response = await client.delete(f"/api/books/{book_id}", headers=auth_headers)
        assert response.status_code == 204
    
    async def test_search_books(self, client):
        """Test searching books."""
        response = await client.get("/api/books/search?q=test")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_books_by_genre(self, client):
        """Test getting books by genre."""
        response = await client.get("/api/books/genre/fiction")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


# ─── Review Endpoints Tests ─────────────────────────────────────────────────────

class TestReviewEndpoints:
    
    async def test_create_review(self, client, auth_headers):
        """Test creating a new review."""
        # First create a book to review
        book_data = {
            "title": "Book for Review",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        book_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        # Create review
        review_data = {
            "book_id": book_id,
            "rating": 5,
            "content": "Great book!"
        }
        
        response = await client.post("/api/reviews", json=review_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["rating"] == 5
        assert data["content"] == "Great book!"
    
    async def test_get_reviews(self, client):
        """Test getting all reviews."""
        response = await client.get("/api/reviews")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_book_reviews(self, client, auth_headers):
        """Test getting reviews for a specific book."""
        # First create a book
        book_data = {
            "title": "Book with Reviews",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        book_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        # Get reviews for the book
        response = await client.get(f"/api/books/{book_id}/reviews")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    async def test_update_review(self, client, auth_headers):
        """Test updating a review."""
        # First create a book and review
        book_data = {
            "title": "Book for Review Update",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        book_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        review_data = {
            "book_id": book_id,
            "rating": 4,
            "content": "Good book"
        }
        
        review_response = await client.post("/api/reviews", json=review_data, headers=auth_headers)
        review_id = review_response.json()["id"]
        
        # Update review
        update_data = {
            "rating": 5,
            "content": "Excellent book!"
        }
        
        response = await client.patch(f"/api/reviews/{review_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["rating"] == 5
        assert data["content"] == "Excellent book!"
    
    async def test_delete_review(self, client, auth_headers):
        """Test deleting a review."""
        # First create a book and review
        book_data = {
            "title": "Book for Review Delete",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        book_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        review_data = {
            "book_id": book_id,
            "rating": 3,
            "content": "Average book"
        }
        
        review_response = await client.post("/api/reviews", json=review_data, headers=auth_headers)
        review_id = review_response.json()["id"]
        
        # Delete review
        response = await client.delete(f"/api/reviews/{review_id}", headers=auth_headers)
        assert response.status_code == 204


# ─── Exchange Endpoints Tests ───────────────────────────────────────────────────

class TestExchangeEndpoints:
    
    async def test_create_exchange(self, client, auth_headers):
        """Test creating a new exchange."""
        # First create two books
        book1_data = {
            "title": "Book 1",
            "author": "Author 1",
            "description": "Description 1"
        }
        
        book2_data = {
            "title": "Book 2",
            "author": "Author 2",
            "description": "Description 2"
        }
        
        book1_response = await client.post("/api/books", json=book1_data, headers=auth_headers)
        book2_response = await client.post("/api/books", json=book2_data, headers=auth_headers)
        
        book1_id = book1_response.json()["id"]
        book2_id = book2_response.json()["id"]
        
        # Create exchange
        exchange_data = {
            "requested_book_id": book2_id,
            "offered_book_id": book1_id,
            "message": "Let's exchange!"
        }
        
        response = await client.post("/api/exchanges", json=exchange_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["requested_book_id"] == book2_id
        assert data["offered_book_id"] == book1_id
    
    async def test_get_exchanges(self, client, auth_headers):
        """Test getting exchanges."""
        response = await client.get("/api/exchanges", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_my_exchanges(self, client, auth_headers):
        """Test getting current user's exchanges."""
        response = await client.get("/api/exchanges/my", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    async def test_accept_exchange(self, client, auth_headers):
        """Test accepting an exchange."""
        # First create an exchange
        book_data = {
            "title": "Book for Exchange",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        book_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        exchange_data = {
            "requested_book_id": book_id,
            "message": "Exchange request"
        }
        
        exchange_response = await client.post("/api/exchanges", json=exchange_data, headers=auth_headers)
        exchange_id = exchange_response.json()["id"]
        
        # Accept exchange
        response = await client.patch(f"/api/exchanges/{exchange_id}/accept", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "accepted"
    
    async def test_complete_exchange(self, client, auth_headers):
        """Test completing an exchange."""
        # First create and accept an exchange
        book_data = {
            "title": "Book for Completion",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        book_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        exchange_data = {
            "requested_book_id": book_id,
            "message": "Exchange for completion"
        }
        
        exchange_response = await client.post("/api/exchanges", json=exchange_data, headers=auth_headers)
        exchange_id = exchange_response.json()["id"]
        
        # Accept first
        await client.patch(f"/api/exchanges/{exchange_id}/accept", headers=auth_headers)
        
        # Complete exchange
        response = await client.patch(f"/api/exchanges/{exchange_id}/complete", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "completed"
    
    async def test_get_exchanges_between_users(self, client, auth_headers):
        """Test getting exchanges between two users."""
        response = await client.get("/api/exchanges/between?user1=1&user2=2", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


# ─── Wishlist Endpoints Tests ───────────────────────────────────────────────────

class TestWishlistEndpoints:
    
    async def test_add_to_wishlist(self, client, auth_headers):
        """Test adding book to wishlist."""
        # First create a book
        book_data = {
            "title": "Book for Wishlist",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        book_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        # Add to wishlist
        response = await client.post(f"/api/wishlist/{book_id}", headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["book_id"] == book_id
    
    async def test_get_wishlist(self, client, auth_headers):
        """Test getting user's wishlist."""
        response = await client.get("/api/wishlist", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    async def test_remove_from_wishlist(self, client, auth_headers):
        """Test removing book from wishlist."""
        # First create a book and add to wishlist
        book_data = {
            "title": "Book for Wishlist Remove",
            "author": "Test Author",
            "description": "Test Description"
        }
        
        book_response = await client.post("/api/books", json=book_data, headers=auth_headers)
        book_id = book_response.json()["id"]
        
        await client.post(f"/api/wishlist/{book_id}", headers=auth_headers)
        
        # Remove from wishlist
        response = await client.delete(f"/api/wishlist/{book_id}", headers=auth_headers)
        assert response.status_code == 204


# ─── Friends Endpoints Tests ─────────────────────────────────────────────────────

class TestFriendsEndpoints:
    
    async def test_add_friend(self, client, auth_headers):
        """Test adding a friend."""
        # First create another user
        user2_data = {
            "email": "friend@example.com",
            "username": "frienduser",
            "password": "password123",
            "full_name": "Friend User"
        }
        
        await client.post("/api/auth/register", json=user2_data)
        
        # Get friend user ID (this would require additional setup in real test)
        friend_id = 2  # Assuming second user gets ID 2
        
        # Add friend
        response = await client.post(f"/api/friends/{friend_id}", headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["status"] == "success"
    
    async def test_get_friends(self, client, auth_headers):
        """Test getting user's friends."""
        response = await client.get("/api/friends", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


# ─── Recommendations Endpoints Tests ─────────────────────────────────────────────

class TestRecommendationsEndpoints:
    
    async def test_get_recommendations(self, client, auth_headers):
        """Test getting book recommendations."""
        response = await client.get("/api/recommendations", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10  # Default limit
    
    async def test_get_recommendations_with_genres(self, client, auth_headers):
        """Test getting recommendations with specific genres."""
        response = await client.get("/api/recommendations?genres=fiction,poetry", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)


# ─── Error Handling Tests ───────────────────────────────────────────────────────

class TestErrorHandling:
    
    async def test_unauthorized_access(self, client):
        """Test unauthorized access to protected endpoints."""
        endpoints = [
            "/api/users/me",
            "/api/books",
            "/api/exchanges",
            "/api/wishlist",
            "/api/friends",
            "/api/recommendations"
        ]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 401
    
    async def test_invalid_book_id(self, client, auth_headers):
        """Test getting non-existent book."""
        response = await client.get("/api/books/99999")
        assert response.status_code == 404
    
    async def test_invalid_exchange_id(self, client, auth_headers):
        """Test getting non-existent exchange."""
        response = await client.get("/api/exchanges/99999", headers=auth_headers)
        assert response.status_code == 404
    
    async def test_invalid_data_validation(self, client, auth_headers):
        """Test validation errors with invalid data."""
        # Invalid book data
        invalid_book_data = {
            "title": "",  # Empty title should fail validation
            "author": "Test Author"
        }
        
        response = await client.post("/api/books", json=invalid_book_data, headers=auth_headers)
        assert response.status_code == 422
        
        # Invalid user data
        invalid_user_data = {
            "email": "invalid-email",  # Invalid email format
            "username": "test",
            "password": "123"  # Too short password
        }
        
        response = await client.post("/api/auth/register", json=invalid_user_data)
        assert response.status_code == 422


# ─── Performance Tests ───────────────────────────────────────────────────────

class TestPerformance:
    
    async def test_concurrent_requests(self, client, auth_headers):
        """Test handling multiple concurrent requests."""
        import asyncio
        
        async def make_request():
            return await client.get("/api/books")
        
        # Make 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
    
    async def test_large_response_handling(self, client, auth_headers):
        """Test handling of large response data."""
        # This would require creating many books in the database
        response = await client.get("/api/books?limit=100")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        # Should handle large lists without issues
