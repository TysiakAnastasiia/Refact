# BookSwap Architecture Documentation

## Overview
BookSwap is a modern web application for book exchange and recommendations built with FastAPI (backend) and React (frontend).

## System Architecture

### High-Level Architecture
```
Frontend (React) 
    |
    | HTTP/WebSocket
    v
Backend (FastAPI)
    |
    | Async SQLAlchemy
    v
Database (PostgreSQL)
```

### Design Patterns Implemented

#### 1. Repository Pattern
- **Purpose**: Abstract data access logic
- **Implementation**: BaseRepository, UserRepository, BookRepository, etc.
- **Benefits**: Testability, separation of concerns, easy switching of data sources

#### 2. Service Layer Pattern
- **Purpose**: Encapsulate business logic
- **Implementation**: AuthService, UserService, BookService, etc.
- **Benefits**: Reusability, transaction management, clear separation from controllers

#### 3. Singleton Pattern
- **Purpose**: Ensure single instance of configuration service
- **Implementation**: ConfigurationService with metaclass
- **Benefits**: Global access point, memory efficiency

#### 4. Factory Pattern
- **Purpose**: Create objects without specifying exact classes
- **Implementation**: DatabaseServiceFactory, RepositoryFactory
- **Benefits**: Loose coupling, easy extensibility

#### 5. Observer Pattern
- **Purpose**: Event-driven notifications
- **Implementation**: EventManager with multiple observers
- **Benefits**: Decoupled event handling, extensibility

### Layer Architecture

#### 1. Presentation Layer (Controllers)
- **Location**: `app/api/routes/`
- **Responsibility**: HTTP request/response handling
- **Components**: API routers, endpoint definitions

#### 2. Business Logic Layer (Services)
- **Location**: `app/services/`
- **Responsibility**: Business rules, orchestration
- **Components**: Service classes, business logic

#### 3. Data Access Layer (Repositories)
- **Location**: `app/repositories/`
- **Responsibility**: Database operations
- **Components**: Repository classes, CRUD operations

#### 4. Data Model Layer (Models)
- **Location**: `app/models/`
- **Responsibility**: Data structure definition
- **Components**: SQLAlchemy models, relationships

### Technology Stack

#### Backend
- **Framework**: FastAPI
- **Language**: Python 3.12
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy (async)
- **Authentication**: JWT (access/refresh tokens)
- **Validation**: Pydantic schemas
- **Testing**: pytest, asyncio

#### Frontend
- **Framework**: React 18
- **Language**: JavaScript
- **Build Tool**: Vite
- **Styling**: CSS Modules
- **State Management**: TanStack Query
- **HTTP Client**: Axios

#### DevOps
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Code Quality**: Ruff (Python), ESLint (JavaScript)
- **Testing**: pytest with coverage
- **Monitoring**: Structured logging

### Database Schema

#### Core Entities
1. **Users** - User accounts and profiles
2. **Books** - Book listings with owners
3. **Exchanges** - Book exchange requests
4. **Messages** - Chat messages between users
5. **Reviews** - Book reviews and ratings
6. **Friendships** - User relationships
7. **WishlistItems** - User book wishlists

#### Relationships
- Users 1:N Books (owner)
- Users 1:N Exchanges (requester/receiver)
- Books 1:N Reviews
- Exchanges 1:N Messages
- Users N:M Friendships
- Users N:M WishlistItems

### API Design

#### RESTful Endpoints
```
/api/auth/          - Authentication
/api/users/         - User management
/api/books/         - Book operations
/api/exchanges/     - Exchange management
/api/reviews/       - Book reviews
/api/chat/          - Messaging
/api/friends/       - Friend management
/api/wishlist/      - Wishlist operations
/api/recommendations/ - AI recommendations
```

#### WebSocket Endpoints
```
/ws/chat/{exchange_id} - Real-time messaging
```

### Security Architecture

#### Authentication
- JWT access tokens (30 min expiry)
- JWT refresh tokens (7 days expiry)
- Secure password hashing (bcrypt)

#### Authorization
- Role-based access control (single user role for this project)
- Resource ownership validation
- Exchange participant verification

#### Security Measures
- CORS configuration
- Input validation (Pydantic)
- SQL injection prevention (ORM)
- XSS prevention (React)

### Performance Considerations

#### Database Optimization
- Async database operations
- Proper indexing on foreign keys
- Connection pooling

#### Caching Strategy
- Service container caching
- Configuration singleton pattern
- Frontend query caching (TanStack Query)

#### Scalability
- Stateless API design
- Container-based deployment
- Event-driven architecture

### Monitoring & Logging

#### Logging Strategy
- Structured logging with event system
- Multiple observers (console, statistics, email)
- Error tracking and reporting

#### Health Checks
- Database connectivity
- Service availability
- API endpoint health

### Deployment Architecture

#### Container Setup
```
Frontend Container (Node.js + React)
    |
Backend Container (Python + FastAPI)
    |
Database Container (PostgreSQL)
```

#### Environment Configuration
- Development: Docker Compose with hot reload
- Production: Optimized Docker images
- Environment variables for configuration

### Testing Strategy

#### Test Types
1. **Unit Tests** - Service and pattern testing
2. **Integration Tests** - API endpoint testing
3. **Pattern Tests** - Design pattern verification

#### Coverage Requirements
- Minimum 50% code coverage (achieved 80%+)
- All business logic tested
- All API endpoints tested

### Future Enhancements

#### Scalability
- Redis caching layer
- Load balancing
- Microservices decomposition

#### Features
- Book recommendations algorithm improvements
- Advanced search and filtering
- Mobile application support
- Payment integration for book purchases

## Conclusion

The BookSwap architecture follows modern software engineering principles with clear separation of concerns, comprehensive testing, and production-ready deployment configuration. The implementation of multiple design patterns ensures maintainability and extensibility for future requirements.
