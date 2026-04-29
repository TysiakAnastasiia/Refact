# BookSwap Class Diagram

## Core Domain Models

```mermaid
classDiagram
    class User {
        +int id
        +str email
        +str username
        +str hashed_password
        +str full_name
        +str bio
        +str city
        +str avatar_url
        +bool is_active
        +datetime created_at
        +List~Book~ books
        +List~Review~ reviews
        +List~WishlistItem~ wishlist_items
        +List~Exchange~ sent_exchanges
        +List~Exchange~ received_exchanges
        +List~Message~ sent_messages
        +List~Friendship~ friendships
    }

    class Book {
        +int id
        +str title
        +str author
        +str description
        +str isbn
        +BookGenre genre
        +int published_year
        +str language
        +BookCondition condition
        +bool is_available_for_exchange
        +int owner_id
        +datetime created_at
        +User owner
        +List~Review~ reviews
        +List~Exchange~ exchanges_as_offered
        +List~Exchange~ exchanges_as_requested
        +List~WishlistItem~ wishlist_items
    }

    class Exchange {
        +int id
        +int requester_id
        +int owner_id
        +int offered_book_id
        +int requested_book_id
        +ExchangeStatus status
        +str message
        +datetime created_at
        +datetime updated_at
        +User requester
        +User owner
        +Book offered_book
        +Book requested_book
        +List~Message~ messages
    }

    class Message {
        +int id
        +int exchange_id
        +int sender_id
        +str content
        +datetime created_at
        +Exchange exchange
        +User sender
    }

    class Review {
        +int id
        +int book_id
        +int user_id
        +int rating
        +str content
        +datetime created_at
        +datetime updated_at
        +Book book
        +User user
    }

    class Friendship {
        +int id
        +int requester_id
        +int addressee_id
        +str status
        +datetime created_at
        +datetime updated_at
        +User requester
        +User addressee
    }

    class WishlistItem {
        +int id
        +int user_id
        +int book_id
        +datetime created_at
        +User user
        +Book book
    }

    %% Relationships
    User "1" -- "N" Book : owns
    User "1" -- "N" Review : writes
    User "1" -- "N" WishlistItem : has
    User "1" -- "N" Exchange : requests
    User "1" -- "N" Exchange : receives
    User "1" -- "N" Message : sends
    User "N" -- "N" Friendship : participates
    
    Book "1" -- "N" Review : receives
    Book "1" -- "N" Exchange : offered_in
    Book "1" -- "N" Exchange : requested_in
    Book "N" -- "N" WishlistItem : appears_in
    
    Exchange "1" -- "N" Message : contains
    Exchange "N" -- "1" Book : offered_book
    Exchange "N" -- "1" Book : requested_book
    Exchange "N" -- "1" User : requester
    Exchange "N" -- "1" User : owner
    
    Message "N" -- "1" Exchange : belongs_to
    Message "N" -- "1" User : sent_by
    
    Review "N" -- "1" Book : about
    Review "N" -- "1" User : written_by
    
    Friendship "N" -- "1" User : requester
    Friendship "N" -- "1" User : addressee
    
    WishlistItem "N" -- "1" User : belongs_to
    WishlistItem "N" -- "1" Book : references
```

## Service Layer Architecture

```mermaid
classDiagram
    class AuthService {
        +AsyncSession db
        +UserRepository user_repo
        +register(UserRegister) dict
        +login(str, str) dict
        +refresh_token(str) dict
        +verify_token(str) dict
    }

    class UserService {
        +AsyncSession db
        +UserRepository user_repo
        +get_user(int) User
        +get_user_by_email(str) User
        +update_user(int, UserUpdate) User
        +delete_user(int) bool
        +search_users(str) List~User~
    }

    class BookService {
        +AsyncSession db
        +BookRepository book_repo
        +create_book(BookCreate, int) Book
        +get_book(int) Book
        +update_book(int, BookUpdate) Book
        +delete_book(int) bool
        +search_books(str) List~Book~
        +get_books_by_genre(BookGenre) List~Book~
    }

    class ExchangeService {
        +AsyncSession db
        +ExchangeRepository exchange_repo
        +BookRepository book_repo
        +create_exchange(ExchangeCreate, int) Exchange
        +update_status(int, ExchangeStatus, int) Exchange
        +get_exchanges_for_user(int) List~Exchange~
        +get_between_users(int, int) List~Exchange~
    }

    class ChatService {
        +AsyncSession db
        +MessageRepository message_repo
        +ExchangeRepository exchange_repo
        +send_message(int, int, MessageCreate) Message
        +get_messages(int, int) List~Message~
    }

    class FriendshipService {
        +AsyncSession db
        +FriendshipRepository friendship_repo
        +add_friend(int, int) dict
        +get_user_friends(int) List~User~
    }

    class RecommendationService {
        +get_recommendations(List~str~, List~str~, int) List~dict~
        +_get_fallback_recommendations(List~str~, List~str~, int) List~dict~
    }

    %% Service Dependencies
    AuthService --> UserRepository : uses
    UserService --> UserRepository : uses
    BookService --> BookRepository : uses
    ExchangeService --> ExchangeRepository : uses
    ExchangeService --> BookRepository : uses
    ChatService --> MessageRepository : uses
    ChatService --> ExchangeRepository : uses
    FriendshipService --> FriendshipRepository : uses
```

## Repository Layer Architecture

```mermaid
classDiagram
    class BaseRepository~T~ {
        +AsyncSession db
        +create(T) T
        +get(int) Optional~T~
        +get_all() List~T~
        +update(T) T
        +delete(int) bool
        +delete(T) bool
    }

    class UserRepository {
        +get_by_email(str) Optional~User~
        +get_by_username(str) Optional~User~
        +search(str) List~User~
    }

    class BookRepository {
        +get_by_isbn(str) Optional~Book~
        +get_by_genre(BookGenre) List~Book~
        +get_by_owner(int) List~Book~
        +search(str) List~Book~
        +get_available() List~Book~
    }

    class ExchangeRepository {
        +get_between_users(int, int) List~Exchange~
        +get_for_user(int) List~Exchange~
        +get_with_details(int) Optional~Exchange~
    }

    class MessageRepository {
        +get_exchange_messages(int) List~Message~
        +get_by_sender(int) List~Message~
    }

    class FriendshipRepository {
        +get_friendship(int, int) Optional~Friendship~
        +get_user_friends(int) List~User~
    }

    %% Inheritance
    UserRepository --|> BaseRepository : inherits
    BookRepository --|> BaseRepository : inherits
    ExchangeRepository --|> BaseRepository : inherits
    MessageRepository --|> BaseRepository : inherits
    FriendshipRepository --|> BaseRepository : inherits
```

## Design Patterns Implementation

```mermaid
classDiagram
    class SingletonMeta {
        +Dict~Type, Any~ _instances
        +__call__(cls, *args, **kwargs) Any
    }

    class ConfigurationService {
        +str app_name
        +str database_url
        +str secret_key
        +initialize() void
        +get(str, Any) Any
        +reload() void
    }

    class DatabaseServiceFactory {
        +Dict~str, Type~ _service_registry
        +create_service(str, AsyncSession, **kwargs) Any
        +register_service(str, Type) void
    }

    class RepositoryFactory {
        +Dict~str, Type~ _repository_registry
        +create_repository(str, AsyncSession) Any
        +register_repository(str, Type) void
    }

    class ServiceContainer {
        +DatabaseServiceFactory _service_factory
        +RepositoryFactory _repository_factory
        +Dict~str, Any~ _instances
        +get_service(str, AsyncSession, **kwargs) Any
        +get_repository(str, AsyncSession) Any
        +clear_cache() void
    }

    class EventManager {
        +List~Observer~ _observers
        +List~Event~ _event_history
        +attach(Observer) void
        +detach(Observer) void
        +notify(Event) void
        +get_event_history(EventType, int) List~Event~
    }

    class Observer {
        <<interface>>
        +update(Event) void
    }

    class LoggingObserver {
        +str log_level
        +update(Event) void
    }

    class StatisticsObserver {
        +Dict~EventType, int~ _event_counts
        +int _total_events
        +update(Event) void
        +get_statistics() Dict~str, Any~
    }

    %% Pattern Relationships
    ConfigurationService --|> SingletonMeta : uses
    DatabaseServiceFactory --> ServiceContainer : used_by
    RepositoryFactory --> ServiceContainer : used_by
    EventManager --> Observer : manages
    LoggingObserver --|> Observer : implements
    StatisticsObserver --|> Observer : implements
```

## API Layer Structure

```mermaid
classDiagram
    class APIRouter {
        +str prefix
        +List~str~ tags
        +get(path, response_model, dependencies) endpoint
        +post(path, response_model, dependencies) endpoint
        +patch(path, response_model, dependencies) endpoint
        +delete(path, status_code, dependencies) endpoint
    }

    class AuthRouter {
        +register(UserRegister) dict
        +login(LoginData) dict
        +refresh_token(str) dict
        +verify_token(str) dict
    }

    class UserRouter {
        +get_me() UserPublic
        +update_me(UserUpdate) UserPublic
        +get_user(int) UserPublic
        +search_users(str) List~UserPublic~
    }

    class BookRouter {
        +create_book(BookCreate) BookResponse
        +get_books(BookQuery) BookListResponse
        +get_book(int) BookResponse
        +update_book(int, BookUpdate) BookResponse
        +delete_book(int) None
        +search_books(str) List~BookResponse~
        +get_books_by_genre(BookGenre) List~BookResponse~
    }

    class ExchangeRouter {
        +create_exchange(ExchangeCreate) ExchangeResponse
        +get_exchanges() List~ExchangeResponse~
        +get_my_exchanges() List~ExchangeResponse~
        +get_exchange(int) ExchangeResponse
        +accept_exchange(int) ExchangeResponse
        +reject_exchange(int) ExchangeResponse
        +complete_exchange(int) ExchangeResponse
        +get_exchanges_between_users(int, int) List~ExchangeResponse~
    }

    class ChatRouter {
        +get_messages(int) List~MessageResponse~
        +send_message(int, MessageCreate) MessageResponse
    }

    class FriendsRouter {
        +add_friend(int) dict
        +get_friends() List~UserPublic~
    }

    %% Router Inheritance
    AuthRouter --|> APIRouter : extends
    UserRouter --|> APIRouter : extends
    BookRouter --|> APIRouter : extends
    ExchangeRouter --|> APIRouter : extends
    ChatRouter --|> APIRouter : extends
    FriendsRouter --|> APIRouter : extends
```

## Database Schema Relationships

```mermaid
erDiagram
    USERS {
        int id PK
        varchar email UK
        varchar username UK
        varchar hashed_password
        varchar full_name
        text bio
        varchar city
        varchar avatar_url
        varchar role
        boolean is_active
        timestamp created_at
    }

    BOOKS {
        int id PK
        varchar title
        varchar author
        text description
        varchar isbn
        varchar genre
        int published_year
        varchar language
        varchar condition
        boolean is_available_for_exchange
        int owner_id FK
        timestamp created_at
    }

    EXCHANGES {
        int id PK
        int requester_id FK
        int owner_id FK
        int offered_book_id FK
        int requested_book_id FK
        varchar status
        text message
        timestamp created_at
        timestamp updated_at
    }

    MESSAGES {
        int id PK
        int exchange_id FK
        int sender_id FK
        text content
        timestamp created_at
    }

    REVIEWS {
        int id PK
        int book_id FK
        int user_id FK
        int rating
        text content
        timestamp created_at
        timestamp updated_at
    }

    FRIENDSHIPS {
        int id PK
        int requester_id FK
        int addressee_id FK
        varchar status
        timestamp created_at
        timestamp updated_at
    }

    WISHLIST_ITEMS {
        int id PK
        int user_id FK
        int book_id FK
        timestamp created_at
    }

    %% Relationships
    USERS ||--o{ BOOKS : owns
    USERS ||--o{ REVIEWS : writes
    USERS ||--o{ WISHLIST_ITEMS : has
    USERS ||--o{ EXCHANGES : requests
    USERS ||--o{ EXCHANGES : receives
    USERS ||--o{ MESSAGES : sends
    USERS ||--o{ FRIENDSHIPS : participates
    
    BOOKS ||--o{ REVIEWS : receives
    BOOKS ||--o{ EXCHANGES : offered_in
    BOOKS ||--o{ EXCHANGES : requested_in
    BOOKS ||--o{ WISHLIST_ITEMS : appears_in
    
    EXCHANGES ||--o{ MESSAGES : contains
    EXCHAGES }o--|| BOOKS : offered_book
    EXCHAGES }o--|| BOOKS : requested_book
    EXCHAGES }o--|| USERS : requester
    EXCHAGES }o--|| USERS : owner
    
    MESSAGES }o--|| USERS : sent_by
    
    REVIEWS }o--|| USERS : written_by
    
    FRIENDSHIPS }o--|| USERS : requester
    FRIENDSHIPS }o--|| USERS : addressee
    
    WISHLIST_ITEMS }o--|| USERS : belongs_to
    WISHLIST_ITEMS }o--|| BOOKS : references
```
