"""
Unit tests for design patterns implementation.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.core.singleton import SingletonMeta, ConfigurationService, config_service
from app.core.factory import DatabaseServiceFactory, RepositoryFactory, ServiceContainer
from app.core.observer import (
    EventManager, EventType, Event, Observer, Subject,
    LoggingObserver, StatisticsObserver, WebSocketObserver
)
from app.services import AuthService, UserService, ExchangeService
from app.repositories import UserRepository, ExchangeRepository


# ─── Singleton Pattern Tests ─────────────────────────────────────────────────────

class TestSingletonPattern:
    
    def test_singleton_meta_class(self):
        """Test that SingletonMeta creates only one instance."""
        class TestClass(metaclass=SingletonMeta):
            def __init__(self):
                self.value = 0
        
        instance1 = TestClass()
        instance2 = TestClass()
        
        assert instance1 is instance2
        assert id(instance1) == id(instance2)
    
    def test_configuration_service_singleton(self):
        """Test ConfigurationService singleton behavior."""
        service1 = ConfigurationService()
        service2 = ConfigurationService()
        
        assert service1 is service2
    
        
    def test_configuration_service_reload(self):
        """Test ConfigurationService reload functionality."""
        # Initialize first time
        config_service.initialize()
        original_value = config_service.get('debug')
        
        # Reload should reinitialize
        config_service.reload()
        assert config_service.get('debug') == original_value


# ─── Factory Pattern Tests ───────────────────────────────────────────────────────

class TestFactoryPattern:
    
    def test_service_factory_creation(self):
        """Test ServiceFactory creates correct service types."""
        factory = DatabaseServiceFactory()
        mock_db = AsyncMock()
        
        # Test creating different services
        auth_service = factory.create_service('auth', mock_db)
        user_service = factory.create_service('user', mock_db)
        
        assert isinstance(auth_service, AuthService)
        assert isinstance(user_service, UserService)
    
    def test_service_factory_unknown_type(self):
        """Test ServiceFactory raises error for unknown service type."""
        factory = DatabaseServiceFactory()
        mock_db = AsyncMock()
        
        with pytest.raises(ValueError, match="Unknown service type"):
            factory.create_service('unknown_service', mock_db)
    
    def test_service_factory_registration(self):
        """Test ServiceFactory can register new service types."""
        factory = DatabaseServiceFactory()
        mock_db = AsyncMock()
        
        # Register a new service type
        factory.register_service('test_service', UserService)
        
        # Create the registered service
        service = factory.create_service('test_service', mock_db)
        assert isinstance(service, UserService)
    
    def test_repository_factory_creation(self):
        """Test RepositoryFactory creates correct repository types."""
        factory = RepositoryFactory()
        mock_db = AsyncMock()
        
        user_repo = factory.create_repository('user', mock_db)
        exchange_repo = factory.create_repository('exchange', mock_db)
        
        assert isinstance(user_repo, UserRepository)
        assert isinstance(exchange_repo, ExchangeRepository)
    
    def test_service_container_caching(self):
        """Test ServiceContainer caches instances."""
        container = ServiceContainer()
        mock_db = AsyncMock()
        
        # Create service twice
        service1 = container.get_service('auth', mock_db)
        service2 = container.get_service('auth', mock_db)
        
        assert service1 is service2
    
    def test_service_container_cache_clear(self):
        """Test ServiceContainer can clear cache."""
        container = ServiceContainer()
        mock_db = AsyncMock()
        
        # Create service
        service = container.get_service('auth', mock_db)
        
        # Clear cache and create again
        container.clear_cache()
        service2 = container.get_service('auth', mock_db)
        
        # Should be different instances after cache clear
        assert service is not service2


# ─── Observer Pattern Tests ─────────────────────────────────────────────────────

class TestObserverPattern:
    
    def test_event_creation(self):
        """Test Event object creation and serialization."""
        data = {'user_id': 1, 'action': 'test'}
        event = Event(EventType.USER_REGISTERED, data)
        
        assert event.event_type == EventType.USER_REGISTERED
        assert event.data == data
        assert isinstance(event.timestamp, datetime)
        
        event_dict = event.to_dict()
        assert event_dict['event_type'] == 'user_registered'
        assert event_dict['data'] == data
        assert 'timestamp' in event_dict
    
    def test_event_manager_attach_detach(self):
        """Test EventManager observer attachment and detachment."""
        manager = EventManager()
        observer = LoggingObserver()
        
        # Attach observer
        manager.attach(observer)
        assert observer in manager._observers
        
        # Detach observer
        manager.detach(observer)
        assert observer not in manager._observers
    
    async def test_event_manager_notify(self):
        """Test EventManager notifies observers."""
        manager = EventManager()
        observer = LoggingObserver()
        
        manager.attach(observer)
        
        event = Event(EventType.USER_REGISTERED, {'user_id': 1})
        await manager.notify(event)
        
        # Check event was added to history
        assert len(manager._event_history) == 1
        assert manager._event_history[0] == event
    
    async def test_event_manager_multiple_observers(self):
        """Test EventManager notifies multiple observers."""
        manager = EventManager()
        observer1 = LoggingObserver()
        observer2 = StatisticsObserver()
        
        manager.attach(observer1)
        manager.attach(observer2)
        
        event = Event(EventType.BOOK_CREATED, {'book_id': 1})
        await manager.notify(event)
        
        # Both observers should have been notified
        assert len(manager._event_history) == 1
    
    def test_event_manager_history_filtering(self):
        """Test EventManager event history filtering."""
        manager = EventManager()
        
        # Add different events
        event1 = Event(EventType.USER_REGISTERED, {'user_id': 1})
        event2 = Event(EventType.BOOK_CREATED, {'book_id': 1})
        event3 = Event(EventType.USER_REGISTERED, {'user_id': 2})
        
        manager._event_history = [event1, event2, event3]
        
        # Filter by event type
        user_events = manager.get_event_history(EventType.USER_REGISTERED)
        assert len(user_events) == 2
        assert all(e.event_type == EventType.USER_REGISTERED for e in user_events)
        
        # Test limit
        limited_events = manager.get_event_history(limit=2)
        assert len(limited_events) == 2
        assert limited_events == [event2, event3]
    
    def test_logging_observer(self):
        """Test LoggingObserver functionality."""
        observer = LoggingObserver()
        event = Event(EventType.USER_REGISTERED, {'user_id': 1})
        
        # This would normally log to console, we just test it doesn't crash
        # In real implementation, we might capture stdout
        assert observer.log_level == "INFO"
    
    async def test_statistics_observer(self):
        """Test StatisticsObserver tracks events correctly."""
        observer = StatisticsObserver()
        
        # Send multiple events
        events = [
            Event(EventType.USER_REGISTERED, {'user_id': 1}),
            Event(EventType.USER_REGISTERED, {'user_id': 2}),
            Event(EventType.BOOK_CREATED, {'book_id': 1}),
        ]
        
        for event in events:
            await observer.update(event)
        
        stats = observer.get_statistics()
        assert stats['total_events'] == 3
        assert stats['event_counts']['user_registered'] == 2
        assert stats['event_counts']['book_created'] == 1
    
    def test_websocket_observer_client_management(self):
        """Test WebSocketObserver client management."""
        observer = WebSocketObserver()
        client1 = MagicMock()
        client2 = MagicMock()
        
        # Add clients
        observer.add_client(client1)
        observer.add_client(client2)
        
        assert len(observer._connected_clients) == 2
        assert client1 in observer._connected_clients
        assert client2 in observer._connected_clients
        
        # Remove client
        observer.remove_client(client1)
        assert len(observer._connected_clients) == 1
        assert client1 not in observer._connected_clients
        assert client2 in observer._connected_clients


# ─── Integration Tests for Patterns ───────────────────────────────────────────────

class TestPatternIntegration:
    
    @patch('app.core.config.settings')
    async def test_singleton_with_observer_integration(self, mock_settings):
        """Test Singleton pattern working with Observer pattern."""
        # Setup mock settings
        mock_settings.database_url = "test://db"
        mock_settings.secret_key = "test-key"
        mock_settings.algorithm = "HS256"
        mock_settings.access_token_expire_minutes = 30
        mock_settings.gemini_api_key = "test-key"
        mock_settings.allowed_origins_list = ["http://localhost:3000"]
        mock_settings.app_env = "test"
        mock_settings.debug = True
        
        # Get singleton instance
        config = ConfigurationService()
        config.initialize()
        
        # Create event manager
        event_manager = EventManager()
        stats_observer = StatisticsObserver()
        event_manager.attach(stats_observer)
        
        # Send configuration change event
        event = Event(EventType.USER_REGISTERED, {
            'config_db_url': config.get('database_url'),
            'config_debug': config.get('debug')
        })
        
        await event_manager.notify(event)
        
        # Verify statistics
        stats = stats_observer.get_statistics()
        assert stats['total_events'] == 1
        assert stats['event_counts']['user_registered'] == 1
    
    def test_factory_with_service_container_integration(self):
        """Test Factory pattern working with ServiceContainer."""
        container = ServiceContainer()
        mock_db = AsyncMock()
        
        # Create services through container (which uses factory)
        auth_service = container.get_service('auth', mock_db)
        user_service = container.get_service('user', mock_db)
        
        # Verify services are created correctly
        assert isinstance(auth_service, AuthService)
        assert isinstance(user_service, UserService)
        
        # Verify caching works
        auth_service2 = container.get_service('auth', mock_db)
        assert auth_service is auth_service2
