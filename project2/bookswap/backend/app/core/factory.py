"""
Factory Pattern Implementation
Creates objects without specifying the exact class of the object that will be created.
"""

from abc import ABC, abstractmethod
from typing import Dict, Type, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import (
    AuthService,
    UserService,
    BookService,
    ReviewService,
    ExchangeService,
    WishlistService,
    ChatService,
    FriendshipService,
)
from app.repositories import (
    UserRepository,
    BookRepository,
    ReviewRepository,
    ExchangeRepository,
    WishlistRepository,
    MessageRepository,
    FriendshipRepository,
)


class ServiceFactory(ABC):
    """Abstract factory for creating service instances."""

    @abstractmethod
    def create_service(self, service_type: str, db: AsyncSession, **kwargs) -> Any:
        pass


class DatabaseServiceFactory(ServiceFactory):
    """
    Factory for creating database-dependent services.
    Implements the Factory Method pattern.
    """

    def __init__(self):
        self._service_registry: Dict[str, Type] = {
            "auth": AuthService,
            "user": UserService,
            "book": BookService,
            "review": ReviewService,
            "exchange": ExchangeService,
            "wishlist": WishlistService,
            "chat": ChatService,
            "friendship": FriendshipService,
        }

    def create_service(self, service_type: str, db: AsyncSession, **kwargs) -> Any:
        """Create a service instance based on type."""
        if service_type not in self._service_registry:
            raise ValueError(f"Unknown service type: {service_type}")

        service_class = self._service_registry[service_type]

        return service_class(db)

    def register_service(self, service_type: str, service_class: Type) -> None:
        """Register a new service type."""
        self._service_registry[service_type] = service_class


class RepositoryFactory:
    """
    Factory for creating repository instances.
    Implements the Abstract Factory pattern.
    """

    def __init__(self):
        self._repository_registry: Dict[str, Type] = {
            "user": UserRepository,
            "book": BookRepository,
            "review": ReviewRepository,
            "exchange": ExchangeRepository,
            "wishlist": WishlistRepository,
            "message": MessageRepository,
            "friendship": FriendshipRepository,
        }

    def create_repository(self, repository_type: str, db: AsyncSession) -> Any:
        """Create a repository instance based on type."""
        if repository_type not in self._repository_registry:
            raise ValueError(f"Unknown repository type: {repository_type}")

        repository_class = self._repository_registry[repository_type]
        return repository_class(db)

    def register_repository(self, repository_type: str, repository_class: Type) -> None:
        """Register a new repository type."""
        self._repository_registry[repository_type] = repository_class


class ServiceContainer:
    """
    Dependency Injection Container using Factory pattern.
    Manages service lifecycles and dependencies.
    """

    def __init__(self):
        self._service_factory = DatabaseServiceFactory()
        self._repository_factory = RepositoryFactory()
        self._instances: Dict[str, Any] = {}

    def get_service(self, service_type: str, db: AsyncSession, **kwargs) -> Any:
        """Get or create a service instance."""
        cache_key = f"{service_type}_{id(db)}"

        if cache_key not in self._instances:
            self._instances[cache_key] = self._service_factory.create_service(
                service_type, db, **kwargs
            )

        return self._instances[cache_key]

    def get_repository(self, repository_type: str, db: AsyncSession) -> Any:
        """Get or create a repository instance."""
        cache_key = f"{repository_type}_{id(db)}"

        if cache_key not in self._instances:
            self._instances[cache_key] = self._repository_factory.create_repository(
                repository_type, db
            )

        return self._instances[cache_key]

    def clear_cache(self) -> None:
        """Clear all cached instances."""
        self._instances.clear()


# Global container instance
service_container = ServiceContainer()
