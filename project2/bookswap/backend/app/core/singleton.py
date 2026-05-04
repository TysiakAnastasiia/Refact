"""
Singleton Pattern Implementation
Ensures only one instance of a class exists throughout the application.
"""

from typing import TypeVar, Type, Dict, Any

T = TypeVar("T")


class SingletonMeta(type):
    """
    Metaclass that implements the Singleton pattern.
    """

    _instances: Dict[Type, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Singleton(metaclass=SingletonMeta):
    """
    Base class for Singleton pattern implementation.
    Classes inheriting from this will have only one instance.
    """

    pass


class ConfigurationService(Singleton):
    """
    Singleton configuration service for managing application settings.
    """

    def __init__(self):
        self._config_cache: Dict[str, Any] = {}
        self._initialized = False

    def initialize(self):
        """Initialize configuration (call once during app startup)."""
        if self._initialized:
            return

        from app.core.config import settings

        self._config_cache = {
            "database_url": settings.database_url,
            "secret_key": settings.secret_key,
            "algorithm": settings.algorithm,
            "access_token_expire_minutes": settings.access_token_expire_minutes,
            "gemini_api_key": settings.gemini_api_key,
            "allowed_origins": settings.allowed_origins_list,
            "app_env": settings.app_env,
            "debug": settings.debug,
        }
        self._initialized = True

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        if not self._initialized:
            self.initialize()
        return self._config_cache.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        if not self._initialized:
            self.initialize()
        return self._config_cache.copy()

    def reload(self):
        """Reload configuration from settings."""
        self._initialized = False
        self.initialize()


# Global instance
config_service = ConfigurationService()
