# 📐 UML Діаграми — BookSwap

Скопіюйте код у [mermaid.live](https://mermaid.live) для перегляду.

---

## 1. Use Case Diagram (Діаграма варіантів використання)

```mermaid
flowchart TD
    Reader([👤 Читач])
    Admin([🛠️ Адмін])

    Reader --> UC1[Реєстрація / Вхід]
    Reader --> UC2[Перегляд каталогу]
    Reader --> UC3[Пошук книг]
    Reader --> UC4[Переглянути деталі книги]
    Reader --> UC5[Додати книгу]
    Reader --> UC6[Написати рецензію]
    Reader --> UC7[Поставити рейтинг]
    Reader --> UC8[Додати до wishlist]
    Reader --> UC9[Запропонувати обмін]
    Reader --> UC10[Прийняти / відхилити обмін]
    Reader --> UC11[Чат для обміну]
    Reader --> UC12[AI-рекомендації]
    Reader --> UC13[Переглянути профіль]
    Reader --> UC14[Редагувати профіль]

    Admin --> UC15[Модерація контенту]
    Admin --> UC2

    UC9 -->|requires| UC1
    UC6 -->|requires| UC1
    UC8 -->|requires| UC1
    UC12 -->|requires| UC1
```

---

## 2. Entity Relationship Diagram (ER)

```mermaid
erDiagram
    USER {
        int id PK
        string email UK
        string username UK
        string hashed_password
        string full_name
        text bio
        string city
        string avatar_url
        bool is_active
        datetime created_at
    }

    BOOK {
        int id PK
        string title
        string author
        text description
        string isbn UK
        string cover_url
        enum genre
        int published_year
        string language
        enum condition
        bool is_available_for_exchange
        int owner_id FK
        datetime created_at
    }

    REVIEW {
        int id PK
        int rating
        text content
        int user_id FK
        int book_id FK
        datetime created_at
        datetime updated_at
    }

    EXCHANGE {
        int id PK
        int requester_id FK
        int owner_id FK
        int offered_book_id FK
        int requested_book_id FK
        enum status
        text message
        datetime created_at
        datetime updated_at
    }

    WISHLIST_ITEM {
        int id PK
        int user_id FK
        int book_id FK
        datetime added_at
    }

    MESSAGE {
        int id PK
        int exchange_id FK
        int sender_id FK
        text content
        bool is_read
        datetime created_at
    }

    USER ||--o{ BOOK : "owns"
    USER ||--o{ REVIEW : "writes"
    USER ||--o{ WISHLIST_ITEM : "has"
    USER ||--o{ EXCHANGE : "requests (requester)"
    USER ||--o{ EXCHANGE : "owns (owner)"
    USER ||--o{ MESSAGE : "sends"

    BOOK ||--o{ REVIEW : "has"
    BOOK ||--o{ WISHLIST_ITEM : "in"
    BOOK ||--o{ EXCHANGE : "offered"
    BOOK ||--o{ EXCHANGE : "requested"

    EXCHANGE ||--o{ MESSAGE : "has"
```

---

## 3. Class Diagram (Діаграма класів)

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
        +bool is_active
        +datetime created_at
    }

    class Book {
        +int id
        +str title
        +str author
        +str description
        +BookGenre genre
        +BookCondition condition
        +bool is_available_for_exchange
        +int owner_id
    }

    class Review {
        +int id
        +int rating
        +str content
        +int user_id
        +int book_id
        +datetime created_at
    }

    class Exchange {
        +int id
        +ExchangeStatus status
        +str message
        +int requester_id
        +int owner_id
        +int offered_book_id
        +int requested_book_id
    }

    class WishlistItem {
        +int id
        +int user_id
        +int book_id
        +datetime added_at
    }

    class Message {
        +int id
        +int exchange_id
        +int sender_id
        +str content
        +bool is_read
    }

    class BookRepository {
        +get_with_owner(id) Book
        +search(query, genre, available_only) tuple
        +get_average_rating(book_id) float
        +get_review_count(book_id) int
    }

    class BookService {
        -BookRepository book_repo
        +get_book(id) Book
        +create_book(data, owner_id) Book
        +update_book(id, data, user_id) Book
        +delete_book(id, user_id) void
        +search_books(...) tuple
    }

    class AuthService {
        -UserRepository user_repo
        +register(data) dict
        +login(email, password) dict
        -_make_tokens(user) dict
    }

    class RecommendationService {
        -Anthropic client
        +get_recommendations(genres, books, count) list
    }

    BookService --> BookRepository : uses
    BookRepository --> Book : manages
    AuthService --> User : manages
    RecommendationService ..> Book : suggests

    User "1" --> "*" Book : owns
    User "1" --> "*" Review : writes
    User "1" --> "*" Exchange : participates
    Book "1" --> "*" Review : has
    Exchange "1" --> "*" Message : contains
```

---

## 4. Sequence Diagram — Exchange Flow

```mermaid
sequenceDiagram
    actor Alice
    actor Bob
    participant FE as Frontend
    participant API as FastAPI
    participant DB as PostgreSQL

    Alice->>FE: Натискає "Запропонувати обмін"
    FE->>API: POST /api/exchanges {offered_book_id, requested_book_id}
    API->>DB: Перевірити книги та власників
    DB-->>API: OK
    API->>DB: INSERT exchange (status=pending)
    DB-->>API: exchange_id
    API-->>FE: 201 Exchange created
    FE-->>Alice: Показати підтвердження

    Note over Bob: Бачить нову пропозицію
    Bob->>FE: Натискає "Прийняти"
    FE->>API: PATCH /api/exchanges/{id}/accept
    API->>DB: UPDATE exchange SET status=accepted
    DB-->>API: OK
    API-->>FE: 200 Exchange updated
    FE-->>Bob: Статус оновлено

    Alice->>FE: Відкриває чат
    FE->>API: GET /api/chat/{exchange_id}
    API-->>FE: [] (порожньо)
    FE->>API: WS /ws/chat/{exchange_id}?token=...
    API-->>FE: WebSocket connected

    Alice->>FE: Пише повідомлення
    FE->>API: POST /api/chat/{id} {content}
    FE->>API: WS send {content}
    API-->>Bob: WS broadcast message
    Bob-->>FE: Отримує повідомлення в реальному часі
```

---

## 5. Sequence Diagram — AI Recommendations

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant API as FastAPI
    participant DB as PostgreSQL
    participant AI as Anthropic Claude API

    User->>FE: Обирає жанри
    User->>FE: Натискає "Отримати рекомендації"
    FE->>API: GET /api/recommendations?genres=Фентезі,Детектив
    API->>DB: SELECT reviews WHERE user_id=... (останні 10)
    DB-->>API: [{book.title, book.author}...]
    API->>AI: POST /v1/messages (prompt з жанрами + прочитаними книгами)
    AI-->>API: JSON масив рекомендацій
    API-->>FE: [{title, author, genre, reason}...]
    FE-->>User: Відображає рекомендації
```

---

## 6. Layered Architecture Diagram

```mermaid
graph TB
    subgraph Frontend["⚛️ React Frontend (Vite)"]
        Pages["Pages\n(HomePage, CatalogPage...)"]
        Components["Components\n(BookCard, ChatWindow...)"]
        Stores["Zustand Store\n(authStore)"]
        AxiosClient["API Client\n(Axios + React Query)"]
    end

    subgraph Backend["🐍 FastAPI Backend"]
        Routes["API Routes\n(auth, books, exchanges...)"]
        Services["Services\n(BookService, AuthService...)"]
        Repositories["Repositories\n(BookRepository, UserRepository...)"]
        Models["SQLAlchemy Models\n(User, Book, Exchange...)"]
    end

    subgraph External["🌐 External"]
        DB[(PostgreSQL)]
        Claude[Anthropic\nClaude API]
    end

    Pages --> Components
    Components --> Stores
    Components --> AxiosClient
    AxiosClient <-->|HTTP/WebSocket| Routes
    Routes --> Services
    Services --> Repositories
    Repositories --> Models
    Models <--> DB
    Services --> Claude
```
