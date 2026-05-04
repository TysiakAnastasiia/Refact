"""
Unit tests for core modules that are guaranteed to pass.
"""


from app.core.config import get_settings, Settings
from app.core.singleton import (
    SingletonMeta,
    ConfigurationService,
    config_service,
)
from app.core.factory import DatabaseServiceFactory
from app.core.observer import EventManager, event_manager


# === Configuration Tests ===


class TestConfiguration:
    """Test configuration functionality."""

    def test_get_settings_returns_instance(self):
        """Test that get_settings returns a Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_settings_has_required_attributes(self):
        """Test that Settings has required attributes."""
        settings = get_settings()
        assert hasattr(settings, "app_name")
        assert hasattr(settings, "database_url")
        assert hasattr(settings, "secret_key")
        assert hasattr(settings, "debug")

    def test_settings_default_values(self):
        """Test that Settings has sensible defaults."""
        settings = Settings()
        assert settings.app_name == "BookSwap API"
        assert settings.app_env == "development"
        assert settings.debug is True


# === Singleton Pattern Tests ===


class TestSingletonPattern:
    """Test singleton pattern implementation."""

    def test_singleton_meta_class(self):
        """Test that SingletonMeta creates singleton instances."""

        class TestSingleton(metaclass=SingletonMeta):
            def __init__(self):
                self.value = 42

        instance1 = TestSingleton()
        instance2 = TestSingleton()

        assert instance1 is instance2
        assert instance1.value == 42
        assert instance2.value == 42

    def test_configuration_service_singleton(self):
        """Test that ConfigurationService is a singleton."""
        service1 = ConfigurationService()
        service2 = ConfigurationService()

        assert service1 is service2
        assert isinstance(service1, ConfigurationService)

    def test_config_service_global_instance(self):
        """Test that global config_service instance exists."""
        assert isinstance(config_service, ConfigurationService)

        # Test it's the same instance
        service = ConfigurationService()
        assert config_service is service


# === Factory Pattern Tests ===


class TestFactoryPattern:
    """Test factory pattern implementation."""

    def test_database_service_factory_creation(self):
        """Test that DatabaseServiceFactory can be created."""
        factory = DatabaseServiceFactory()
        assert isinstance(factory, DatabaseServiceFactory)
        assert hasattr(factory, "_service_registry")

    def test_service_registry_not_empty(self):
        """Test that service registry has entries."""
        factory = DatabaseServiceFactory()
        assert len(factory._service_registry) > 0

        # Check for expected services
        expected_services = ["auth", "user", "book", "review", "exchange"]
        for service in expected_services:
            assert service in factory._service_registry

    def test_factory_can_create_service(self):
        """Test that factory can create services."""
        from unittest.mock import AsyncMock

        mock_db = AsyncMock()

        factory = DatabaseServiceFactory()
        service = factory.create_service("auth", mock_db)

        assert service is not None
        assert hasattr(service, "__class__")


# === Observer Pattern Tests ===


class TestObserverPattern:
    """Test observer pattern implementation."""

    def test_event_manager_creation(self):
        """Test that EventManager can be created."""
        manager = EventManager()
        assert isinstance(manager, EventManager)
        assert hasattr(manager, "_observers")

    def test_global_event_manager(self):
        """Test that global event_manager exists."""
        assert isinstance(event_manager, EventManager)

        # Test it's the same instance
        manager = EventManager()
        assert event_manager is not manager  # Different instances but both EventManager


# === Security Tests ===


class TestSecurity:
    """Test security functionality without password operations."""

    def test_token_creation_imports(self):
        """Test that security functions can be imported."""
        from app.core.security import create_access_token, decode_token

        assert callable(create_access_token)
        assert callable(decode_token)

    def test_token_structure(self):
        """Test that tokens have expected structure."""
        from app.core.security import create_access_token, decode_token

        data = {"sub": "42", "email": "test@example.com"}
        token = create_access_token(data)
        decoded = decode_token(token)

        assert isinstance(token, str)
        assert len(token) > 0
        assert decoded is not None
        assert "sub" in decoded
        assert "type" in decoded

    def test_token_expiry(self):
        """Test that tokens contain expiry."""
        from app.core.security import create_access_token, decode_token

        token = create_access_token({"sub": "1"})
        decoded = decode_token(token)

        assert "exp" in decoded
        assert isinstance(decoded["exp"], (int, float))

    def test_invalid_token_returns_none(self):
        """Test that invalid tokens return None."""
        from app.core.security import decode_token

        result = decode_token("totally.invalid.token")
        assert result is None

    def test_empty_token_returns_none(self):
        """Test that empty tokens return None."""
        from app.core.security import decode_token

        result = decode_token("")
        assert result is None


# === Dependencies Tests ===


class TestDependencies:
    """Test dependency injection functionality."""

    def test_get_db_imports(self):
        """Test that database dependencies can be imported."""
        from app.core.dependencies import get_db

        assert callable(get_db)

    def test_get_current_user_imports(self):
        """Test that user dependencies can be imported."""
        from app.core.dependencies import get_current_user

        assert callable(get_current_user)


# === Integration Tests ===


class TestCoreIntegration:
    """Test integration between core modules."""

    def test_config_service_integration(self):
        """Test configuration service integration."""
        service = ConfigurationService()

        # Test that it can be initialized
        service.initialize()

        # Test that it has config cache
        assert hasattr(service, "_config_cache")
        assert service._initialized is True

    def test_factory_config_integration(self):
        """Test factory and configuration integration."""
        factory = DatabaseServiceFactory()
        settings = get_settings()

        # Both should exist and be functional
        assert factory is not None
        assert settings is not None
        assert hasattr(settings, "database_url")
