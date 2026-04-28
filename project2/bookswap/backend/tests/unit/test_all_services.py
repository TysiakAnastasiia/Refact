"""
Comprehensive unit tests for all services.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import (
    AuthService, UserService, BookService, ReviewService,
    ExchangeService, WishlistService, ChatService, FriendshipService,
    RecommendationService
)
from app.schemas import (
    UserRegister, UserUpdate, BookCreate, BookUpdate,
    ReviewCreate, ReviewUpdate, ExchangeCreate, MessageCreate
)
from app.models import (
    User, Book, Review, Exchange, WishlistItem, Message,
    BookGenre, BookCondition, ExchangeStatus, Friendship
)
from app.core.security import get_password_hash
from app.core.observer import event_manager, Event, EventType


# ─── AuthService Tests ───────────────────────────────────────────────────────────

class TestAuthService:
    
    @pytest.fixture
    def auth_service(self):
        mock_db = AsyncMock(spec=AsyncSession)
        return AuthService(mock_db)
    
    @pytest.fixture
    def mock_user_repo(self):
        return AsyncMock()
    
    @pytest.fixture
    def sample_user_data(self):
        return UserRegister(
            email="test@example.com",
            username="testuser",
            password="SecurePass123!",
            full_name="Test User",
            bio="Test bio",
            city="Test City"
        )
    
    async def test_register_success(self, auth_service, sample_user_data, mock_user_repo):
        """Test successful user registration."""
        # Mock repository methods
        auth_service.user_repo = mock_user_repo
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.get_by_username.return_value = None
        
        # Mock created user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = sample_user_data.email
        mock_user.username = sample_user_data.username
        mock_user.full_name = sample_user_data.full_name
        mock_user_repo.create.return_value = mock_user
        
        with patch('app.services.event_manager') as mock_event_manager:
            result = await auth_service.register(sample_user_data)
        
        assert result['access_token'] is not None
        assert result['refresh_token'] is not None
        assert result['user'] == mock_user
        
        # Verify event was emitted
        mock_event_manager.notify.assert_called_once()
    
    async def test_register_email_exists(self, auth_service, sample_user_data, mock_user_repo):
        """Test registration fails when email already exists."""
        auth_service.user_repo = mock_user_repo
        mock_user_repo.get_by_email.return_value = MagicMock()
        
        with pytest.raises(Exception):  # HTTPException
            await auth_service.register(sample_user_data)
    
    async def test_register_username_exists(self, auth_service, sample_user_data, mock_user_repo):
        """Test registration fails when username already exists."""
        auth_service.user_repo = mock_user_repo
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.get_by_username.return_value = MagicMock()
        
        with pytest.raises(Exception):  # HTTPException
            await auth_service.register(sample_user_data)
    
    async def test_login_success(self, auth_service, mock_user_repo):
        """Test successful login."""
        auth_service.user_repo = mock_user_repo
        
        # Mock user
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.hashed_password = get_password_hash("password123")
        mock_user.is_active = True
        mock_user_repo.get_by_email.return_value = mock_user
        
        result = await auth_service.login("test@example.com", "password123")
        
        assert result['access_token'] is not None
        assert result['refresh_token'] is not None
    
    async def test_login_invalid_credentials(self, auth_service, mock_user_repo):
        """Test login fails with invalid credentials."""
        auth_service.user_repo = mock_user_repo
        mock_user_repo.get_by_email.return_value = None
        
        with pytest.raises(Exception):  # HTTPException
            await auth_service.login("test@example.com", "wrongpassword")
    
    async def test_login_disabled_account(self, auth_service, mock_user_repo):
        """Test login fails with disabled account."""
        auth_service.user_repo = mock_user_repo
        
        mock_user = MagicMock()
        mock_user.hashed_password = get_password_hash("password123")
        mock_user.is_active = False
        mock_user_repo.get_by_email.return_value = mock_user
        
        with pytest.raises(Exception):  # HTTPException
            await auth_service.login("test@example.com", "password123")


# ─── UserService Tests ───────────────────────────────────────────────────────────

class TestUserService:
    
    @pytest.fixture
    def user_service(self):
        mock_db = AsyncMock(spec=AsyncSession)
        return UserService(mock_db)
    
    @pytest.fixture
    def mock_user_repo(self):
        return AsyncMock()
    
    @pytest.fixture
    def sample_user(self):
        user = MagicMock()
        user.id = 1
        user.email = "test@example.com"
        user.username = "testuser"
        user.full_name = "Test User"
        user.bio = "Test bio"
        user.city = "Test City"
        return user
    
    async def test_get_user_by_id(self, user_service, sample_user, mock_user_repo):
        """Test getting user by ID."""
        user_service.user_repo = mock_user_repo
        mock_user_repo.get.return_value = sample_user
        
        result = await user_service.get_user(1)
        assert result == sample_user
        mock_user_repo.get.assert_called_once_with(1)
    
    async def test_get_user_by_email(self, user_service, sample_user, mock_user_repo):
        """Test getting user by email."""
        user_service.user_repo = mock_user_repo
        mock_user_repo.get_by_email.return_value = sample_user
        
        result = await user_service.get_user_by_email("test@example.com")
        assert result == sample_user
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
    
    async def test_update_user(self, user_service, sample_user, mock_user_repo):
        """Test updating user information."""
        user_service.user_repo = mock_user_repo
        mock_user_repo.update.return_value = sample_user
        
        update_data = UserUpdate(
            full_name="Updated Name",
            bio="Updated bio",
            city="Updated City"
        )
        
        result = await user_service.update_user(1, update_data)
        assert result == sample_user
        mock_user_repo.update.assert_called_once()
    
    async def test_delete_user(self, user_service, mock_user_repo):
        """Test deleting user."""
        user_service.user_repo = mock_user_repo
        mock_user_repo.delete.return_value = True
        
        result = await user_service.delete_user(1)
        assert result is True
        mock_user_repo.delete.assert_called_once_with(1)


# ─── BookService Tests ───────────────────────────────────────────────────────────

class TestBookService:
    
    @pytest.fixture
    def book_service(self):
        mock_db = AsyncMock(spec=AsyncSession)
        return BookService(mock_db)
    
    @pytest.fixture
    def mock_book_repo(self):
        return AsyncMock()
    
    @pytest.fixture
    def sample_book_data(self):
        return BookCreate(
            title="Test Book",
            author="Test Author",
            description="Test Description",
            isbn="1234567890123",
            genre=BookGenre.fiction,
            published_year=2023,
            language="Ukrainian",
            condition=BookCondition.good
        )
    
    @pytest.fixture
    def sample_book(self):
        book = MagicMock()
        book.id = 1
        book.title = "Test Book"
        book.author = "Test Author"
        book.genre = BookGenre.fiction
        book.is_available_for_exchange = True
        return book
    
    async def test_create_book(self, book_service, sample_book_data, sample_book, mock_book_repo):
        """Test creating a new book."""
        book_service.book_repo = mock_book_repo
        
        # Mock owner
        mock_owner = MagicMock()
        mock_owner.id = 1
        mock_book_repo.get.return_value = mock_owner
        
        mock_book_repo.create.return_value = sample_book
        
        result = await book_service.create_book(sample_book_data, 1)
        assert result == sample_book
        mock_book_repo.create.assert_called_once()
    
    async def test_get_book_by_id(self, book_service, sample_book, mock_book_repo):
        """Test getting book by ID."""
        book_service.book_repo = mock_book_repo
        mock_book_repo.get.return_value = sample_book
        
        result = await book_service.get_book(1)
        assert result == sample_book
        mock_book_repo.get.assert_called_once_with(1)
    
    async def test_get_books_by_genre(self, book_service, mock_book_repo):
        """Test getting books by genre."""
        book_service.book_repo = mock_book_repo
        mock_books = [MagicMock() for _ in range(3)]
        mock_book_repo.get_by_genre.return_value = mock_books
        
        result = await book_service.get_books_by_genre(BookGenre.fiction)
        assert len(result) == 3
        mock_book_repo.get_by_genre.assert_called_once_with(BookGenre.fiction)
    
    async def test_search_books(self, book_service, mock_book_repo):
        """Test searching books."""
        book_service.book_repo = mock_book_repo
        mock_books = [MagicMock() for _ in range(2)]
        mock_book_repo.search.return_value = mock_books
        
        result = await book_service.search_books("test query")
        assert len(result) == 2
        mock_book_repo.search.assert_called_once_with("test query")
    
    async def test_update_book(self, book_service, sample_book, mock_book_repo):
        """Test updating book information."""
        book_service.book_repo = mock_book_repo
        mock_book_repo.update.return_value = sample_book
        
        update_data = BookUpdate(
            title="Updated Title",
            description="Updated Description"
        )
        
        result = await book_service.update_book(1, update_data)
        assert result == sample_book
        mock_book_repo.update.assert_called_once()
    
    async def test_delete_book(self, book_service, mock_book_repo):
        """Test deleting book."""
        book_service.book_repo = mock_book_repo
        mock_book_repo.delete.return_value = True
        
        result = await book_service.delete_book(1)
        assert result is True
        mock_book_repo.delete.assert_called_once_with(1)


# ─── ExchangeService Tests ───────────────────────────────────────────────────────

class TestExchangeService:
    
    @pytest.fixture
    def exchange_service(self):
        mock_db = AsyncMock(spec=AsyncSession)
        return ExchangeService(mock_db)
    
    @pytest.fixture
    def mock_exchange_repo(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_book_repo(self):
        return AsyncMock()
    
    @pytest.fixture
    def sample_exchange_data(self):
        return ExchangeCreate(
            requested_book_id=1,
            offered_book_id=2,
            message="Test exchange message"
        )
    
    @pytest.fixture
    def sample_exchange(self):
        exchange = MagicMock()
        exchange.id = 1
        exchange.requester_id = 1
        exchange.owner_id = 2
        exchange.status = ExchangeStatus.pending
        return exchange
    
    async def test_create_exchange(self, exchange_service, sample_exchange_data, sample_exchange, 
                                  mock_exchange_repo, mock_book_repo):
        """Test creating a new exchange."""
        exchange_service.exchange_repo = mock_exchange_repo
        exchange_service.book_repo = mock_book_repo
        
        # Mock requested book
        mock_requested_book = MagicMock()
        mock_requested_book.owner_id = 2
        mock_requested_book.is_available_for_exchange = True
        mock_book_repo.get.return_value = mock_requested_book
        
        # Mock offered book
        mock_offered_book = MagicMock()
        mock_offered_book.owner_id = 1
        mock_book_repo.get.side_effect = [mock_requested_book, mock_offered_book]
        
        mock_exchange_repo.create.return_value = sample_exchange
        mock_exchange_repo.get_with_details.return_value = sample_exchange
        
        with patch('app.services.event_manager') as mock_event_manager:
            result = await exchange_service.create_exchange(sample_exchange_data, 1)
        
        assert result == sample_exchange
        mock_exchange_repo.create.assert_called_once()
        mock_event_manager.notify.assert_called_once()
    
    async def test_create_exchange_same_owner(self, exchange_service, sample_exchange_data, 
                                            mock_exchange_repo, mock_book_repo):
        """Test creating exchange fails when requester owns both books."""
        exchange_service.exchange_repo = mock_exchange_repo
        exchange_service.book_repo = mock_book_repo
        
        # Mock books with same owner
        mock_book = MagicMock()
        mock_book.owner_id = 1
        mock_book.is_available_for_exchange = True
        mock_book_repo.get.return_value = mock_book
        
        with pytest.raises(Exception):  # HTTPException
            await exchange_service.create_exchange(sample_exchange_data, 1)
    
    async def test_update_exchange_status(self, exchange_service, sample_exchange, 
                                        mock_exchange_repo):
        """Test updating exchange status."""
        exchange_service.exchange_repo = mock_exchange_repo
        mock_exchange_repo.get.return_value = sample_exchange
        mock_exchange_repo.update.return_value = None
        mock_exchange_repo.get_with_details.return_value = sample_exchange
        
        with patch('app.services.event_manager') as mock_event_manager:
            result = await exchange_service.update_status(1, ExchangeStatus.accepted, 2)
        
        assert result == sample_exchange
        mock_exchange_repo.update.assert_called_once()
        mock_event_manager.notify.assert_called_once()
    
    async def test_update_exchange_not_participant(self, exchange_service, sample_exchange, 
                                                  mock_exchange_repo):
        """Test updating exchange status fails for non-participant."""
        exchange_service.exchange_repo = mock_exchange_repo
        mock_exchange_repo.get.return_value = sample_exchange
        
        with pytest.raises(Exception):  # HTTPException
            await exchange_service.update_status(1, ExchangeStatus.accepted, 3)


# ─── ChatService Tests ───────────────────────────────────────────────────────────

class TestChatService:
    
    @pytest.fixture
    def chat_service(self):
        mock_db = AsyncMock(spec=AsyncSession)
        return ChatService(mock_db)
    
    @pytest.fixture
    def mock_message_repo(self):
        return AsyncMock()
    
    @pytest.fixture
    def mock_exchange_repo(self):
        return AsyncMock()
    
    @pytest.fixture
    def sample_message_data(self):
        return MessageCreate(content="Test message")
    
    @pytest.fixture
    def sample_message(self):
        message = MagicMock()
        message.id = 1
        message.content = "Test message"
        message.sender_id = 1
        message.exchange_id = 1
        return message
    
    @pytest.fixture
    def sample_exchange(self):
        exchange = MagicMock()
        exchange.id = 1
        exchange.requester_id = 1
        exchange.owner_id = 2
        return exchange
    
    async def test_send_message(self, chat_service, sample_message_data, sample_message,
                              sample_exchange, mock_message_repo, mock_exchange_repo):
        """Test sending a message."""
        chat_service.message_repo = mock_message_repo
        chat_service.exchange_repo = mock_exchange_repo
        
        mock_exchange_repo.get.return_value = sample_exchange
        mock_message_repo.create.return_value = sample_message
        
        with patch('app.services.event_manager') as mock_event_manager:
            result = await chat_service.send_message(1, 1, sample_message_data)
        
        assert result == sample_message
        mock_message_repo.create.assert_called_once()
        mock_event_manager.notify.assert_called_once()
    
    async def test_send_message_not_participant(self, chat_service, sample_message_data,
                                               mock_message_repo, mock_exchange_repo):
        """Test sending message fails for non-participant."""
        chat_service.message_repo = mock_message_repo
        chat_service.exchange_repo = mock_exchange_repo
        
        # Mock exchange where user 3 is not a participant
        exchange = MagicMock()
        exchange.requester_id = 1
        exchange.owner_id = 2
        mock_exchange_repo.get.return_value = exchange
        
        with pytest.raises(Exception):  # HTTPException
            await chat_service.send_message(1, 3, sample_message_data)
    
    async def test_get_messages(self, chat_service, mock_message_repo, mock_exchange_repo):
        """Test getting messages for an exchange."""
        chat_service.message_repo = mock_message_repo
        chat_service.exchange_repo = mock_exchange_repo
        
        # Mock exchange
        exchange = MagicMock()
        exchange.requester_id = 1
        exchange.owner_id = 2
        mock_exchange_repo.get.return_value = exchange
        
        # Mock messages
        messages = [MagicMock() for _ in range(3)]
        mock_message_repo.get_exchange_messages.return_value = messages
        
        result = await chat_service.get_messages(1, 1)
        assert len(result) == 3
        mock_message_repo.get_exchange_messages.assert_called_once_with(1)


# ─── FriendshipService Tests ─────────────────────────────────────────────────────

class TestFriendshipService:
    
    @pytest.fixture
    def friendship_service(self):
        mock_db = AsyncMock(spec=AsyncSession)
        return FriendshipService(mock_db)
    
    @pytest.fixture
    def mock_friendship_repo(self):
        return AsyncMock()
    
    @pytest.fixture
    def sample_friendship(self):
        friendship = MagicMock()
        friendship.id = 1
        friendship.requester_id = 1
        friendship.addressee_id = 2
        friendship.status = "accepted"
        return friendship
    
    async def test_add_friend(self, friendship_service, sample_friendship, mock_friendship_repo):
        """Test adding a friend."""
        friendship_service.friendship_repo = mock_friendship_repo
        mock_friendship_repo.get_friendship.return_value = None
        mock_friendship_repo.create.return_value = sample_friendship
        
        with patch('app.services.event_manager') as mock_event_manager:
            result = await friendship_service.add_friend(1, 2)
        
        assert result['status'] == 'success'
        mock_friendship_repo.create.assert_called_once()
        mock_event_manager.notify.assert_called_once()
    
    async def test_add_friend_already_friends(self, friendship_service, mock_friendship_repo):
        """Test adding friend fails when already friends."""
        friendship_service.friendship_repo = mock_friendship_repo
        mock_friendship_repo.get_friendship.return_value = MagicMock()
        
        with pytest.raises(Exception):  # HTTPException
            await friendship_service.add_friend(1, 2)
    
    async def test_add_friend_self(self, friendship_service, mock_friendship_repo):
        """Test adding friend fails when trying to add self."""
        with pytest.raises(Exception):  # HTTPException
            await friendship_service.add_friend(1, 1)
    
    async def test_get_user_friends(self, friendship_service, mock_friendship_repo):
        """Test getting user's friends."""
        friendship_service.friendship_repo = mock_friendship_repo
        friends = [MagicMock() for _ in range(3)]
        mock_friendship_repo.get_user_friends.return_value = friends
        
        result = await friendship_service.get_user_friends(1)
        assert len(result) == 3
        mock_friendship_repo.get_user_friends.assert_called_once_with(1)


# ─── RecommendationService Tests ─────────────────────────────────────────────────

class TestRecommendationService:
    
    @pytest.fixture
    def recommendation_service(self):
        return RecommendationService()
    
    async def test_get_recommendations_with_genres(self, recommendation_service):
        """Test getting recommendations with specific genres."""
        genres = ["Детектив", "Поезія"]
        read_books = ["1984", "Сто років самотності"]
        
        result = await recommendation_service.get_recommendations(genres, read_books, 2)
        
        assert len(result) == 2
        assert all('title' in rec for rec in result)
        assert all('author' in rec for rec in result)
        assert all('genre' in rec for rec in result)
    
    async def test_get_recommendations_no_genres(self, recommendation_service):
        """Test getting recommendations without specific genres."""
        genres = []
        read_books = []
        
        result = await recommendation_service.get_recommendations(genres, read_books, 3)
        
        assert len(result) == 3
        assert all('title' in rec for rec in result)
    
    async def test_fallback_recommendations(self, recommendation_service):
        """Test fallback recommendations work correctly."""
        # Mock API call to fail
        with patch('urllib.request.urlopen', side_effect=Exception("API Error")):
            result = await recommendation_service.get_recommendations(["Детектив"], [], 2)
        
        assert len(result) == 2
        # Should return detective books from fallback
        titles = [rec['title'] for rec in result]
        assert any("Детектив" in title or "Убивство" in title for title in titles)
