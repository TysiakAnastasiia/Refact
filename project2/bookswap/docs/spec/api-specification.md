# BookSwap API Specification

## Overview
RESTful API for BookSwap platform with JWT authentication, real-time WebSocket support, and comprehensive book exchange functionality.

## Base URL
- **Development**: `http://localhost:8000/api`
- **Production**: `https://bookswap.example.com/api`

## Authentication
All protected endpoints require JWT Bearer token:
```
Authorization: Bearer <access_token>
```

### Token Types
- **Access Token**: 30 minutes expiry
- **Refresh Token**: 7 days expiry

## Response Format

### Success Responses
```json
{
  "data": { ... },
  "message": "Success message"
}
```

### Error Responses
```json
{
  "detail": "Error description",
  "status_code": 400
}
```

## Endpoints

### Authentication (`/api/auth`)

#### POST `/api/auth/register`
Register new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123",
  "full_name": "Full Name",
  "bio": "Optional bio",
  "city": "Optional city"
}
```

**Response (201):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "Full Name",
    "bio": "Optional bio",
    "city": "Optional city",
    "avatar_url": null,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### POST `/api/auth/login`
Authenticate user and receive tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": { ... }
}
```

#### POST `/api/auth/refresh`
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Users (`/api/users`)

#### GET `/api/users/me`
Get current user profile.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "bio": "Optional bio",
  "city": "Optional city",
  "avatar_url": null,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PATCH `/api/users/me`
Update current user profile.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "Updated Name",
  "bio": "Updated bio",
  "city": "Updated City"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Updated Name",
  "bio": "Updated bio",
  "city": "Updated City",
  "avatar_url": null,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/users/search`
Search users by query.

**Query Parameters:**
- `q` (string, required): Search query

**Response (200):**
```json
[
  {
    "id": 1,
    "username": "username",
    "full_name": "Full Name",
    "avatar_url": null,
    "city": "City"
  }
]
```

#### GET `/api/users/{user_id}`
Get user profile by ID.

**Response (200):**
```json
{
  "id": 1,
  "username": "username",
  "full_name": "Full Name",
  "bio": "Optional bio",
  "city": "Optional city",
  "avatar_url": null,
  "created_at": "2024-01-01T00:00:00Z",
  "books_count": 5,
  "reviews_count": 3,
  "exchanges_count": 2
}
```

### Books (`/api/books`)

#### POST `/api/books`
Create new book listing.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Book Title",
  "author": "Author Name",
  "description": "Book description",
  "isbn": "1234567890123",
  "genre": "fiction",
  "published_year": 2023,
  "language": "Ukrainian",
  "condition": "good"
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "Book Title",
  "author": "Author Name",
  "description": "Book description",
  "isbn": "1234567890123",
  "genre": "fiction",
  "published_year": 2023,
  "language": "Ukrainian",
  "condition": "good",
  "is_available_for_exchange": true,
  "owner": {
    "id": 1,
    "username": "owner",
    "full_name": "Owner Name"
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/books`
Get all books with pagination and filtering.

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Items per page (default: 20)
- `genre` (string, optional): Filter by genre
- `condition` (string, optional): Filter by condition
- `available` (boolean, optional): Filter by availability

**Response (200):**
```json
{
  "books": [
    {
      "id": 1,
      "title": "Book Title",
      "author": "Author Name",
      "genre": "fiction",
      "condition": "good",
      "is_available_for_exchange": true,
      "owner": {
        "id": 1,
        "username": "owner",
        "full_name": "Owner Name",
        "city": "City"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20,
  "pages": 5
}
```

#### GET `/api/books/{book_id}`
Get book details by ID.

**Response (200):**
```json
{
  "id": 1,
  "title": "Book Title",
  "author": "Author Name",
  "description": "Book description",
  "isbn": "1234567890123",
  "genre": "fiction",
  "published_year": 2023,
  "language": "Ukrainian",
  "condition": "good",
  "is_available_for_exchange": true,
  "owner": {
    "id": 1,
    "username": "owner",
    "full_name": "Owner Name",
    "city": "City",
    "avatar_url": null
  },
  "reviews_count": 5,
  "average_rating": 4.2,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PATCH `/api/books/{book_id}`
Update book information.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "condition": "excellent"
}
```

#### DELETE `/api/books/{book_id}`
Delete book listing.

**Headers:** `Authorization: Bearer <token>`

**Response (204):** No content

#### GET `/api/books/search`
Search books by query.

**Query Parameters:**
- `q` (string, required): Search query

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Book Title",
    "author": "Author Name",
    "genre": "fiction",
    "owner": {
      "username": "owner",
      "full_name": "Owner Name"
    }
  }
]
```

#### GET `/api/books/genre/{genre}`
Get books by genre.

**Response (200):**
```json
[
  {
    "id": 1,
    "title": "Book Title",
    "author": "Author Name",
    "genre": "fiction",
    "owner": {
      "username": "owner",
      "full_name": "Owner Name"
    }
  }
]
```

### Exchanges (`/api/exchanges`)

#### POST `/api/exchanges`
Create new exchange request.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "requested_book_id": 2,
  "offered_book_id": 1,
  "message": "Let's exchange books!"
}
```

**Response (201):**
```json
{
  "id": 1,
  "requester": {
    "id": 1,
    "username": "requester",
    "full_name": "Requester Name"
  },
  "owner": {
    "id": 2,
    "username": "owner",
    "full_name": "Owner Name"
  },
  "offered_book": {
    "id": 1,
    "title": "Offered Book",
    "author": "Author"
  },
  "requested_book": {
    "id": 2,
    "title": "Requested Book",
    "author": "Author"
  },
  "status": "pending",
  "message": "Let's exchange books!",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/exchanges`
Get all exchanges (admin only).

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "requester": { ... },
    "owner": { ... },
    "offered_book": { ... },
    "requested_book": { ... },
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET `/api/exchanges/my`
Get current user's exchanges.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "requester": { ... },
    "owner": { ... },
    "offered_book": { ... },
    "requested_book": { ... },
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET `/api/exchanges/between`
Get exchanges between two users.

**Query Parameters:**
- `user1` (int, required): First user ID
- `user2` (int, required): Second user ID

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "requester": { ... },
    "owner": { ... },
    "offered_book": { ... },
    "requested_book": { ... },
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET `/api/exchanges/{exchange_id}`
Get exchange details.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "requester": { ... },
  "owner": { ... },
  "offered_book": { ... },
  "requested_book": { ... },
  "status": "pending",
  "message": "Let's exchange books!",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### PATCH `/api/exchanges/{exchange_id}/accept`
Accept exchange request.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "status": "accepted",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PATCH `/api/exchanges/{exchange_id}/reject`
Reject exchange request.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "status": "rejected",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### PATCH `/api/exchanges/{exchange_id}/complete`
Mark exchange as completed.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "status": "completed",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Chat (`/api/chat`)

#### GET `/api/chat/{exchange_id}`
Get chat messages for exchange.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "sender": {
      "id": 1,
      "username": "sender",
      "full_name": "Sender Name"
    },
    "content": "Hello! Let's discuss the exchange.",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST `/api/chat/{exchange_id}`
Send message in chat.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "content": "Hello! Let's discuss the exchange."
}
```

**Response (201):**
```json
{
  "id": 1,
  "sender": {
    "id": 1,
    "username": "sender",
    "full_name": "Sender Name"
  },
  "content": "Hello! Let's discuss the exchange.",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Friends (`/api/friends`)

#### POST `/api/friends/{user_id}`
Add user as friend.

**Headers:** `Authorization: Bearer <token>`

**Response (201):**
```json
{
  "status": "success",
  "message": "Friend added successfully"
}
```

#### GET `/api/friends`
Get user's friends list.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 2,
    "username": "friend",
    "full_name": "Friend Name",
    "avatar_url": null,
    "city": "City"
  }
]
```

### Wishlist (`/api/wishlist`)

#### POST `/api/wishlist/{book_id}`
Add book to wishlist.

**Headers:** `Authorization: Bearer <token>`

**Response (201):**
```json
{
  "id": 1,
  "book": {
    "id": 1,
    "title": "Book Title",
    "author": "Author Name"
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/wishlist`
Get user's wishlist.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
[
  {
    "id": 1,
    "book": {
      "id": 1,
      "title": "Book Title",
      "author": "Author Name",
      "genre": "fiction",
      "owner": {
        "username": "owner",
        "full_name": "Owner Name"
      }
    },
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### DELETE `/api/wishlist/{book_id}`
Remove book from wishlist.

**Headers:** `Authorization: Bearer <token>`

**Response (204):** No content

### Reviews (`/api/reviews`)

#### POST `/api/reviews`
Create book review.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "book_id": 1,
  "rating": 5,
  "content": "Excellent book! Highly recommended."
}
```

**Response (201):**
```json
{
  "id": 1,
  "book": {
    "id": 1,
    "title": "Book Title",
    "author": "Author Name"
  },
  "user": {
    "id": 1,
    "username": "reviewer",
    "full_name": "Reviewer Name"
  },
  "rating": 5,
  "content": "Excellent book! Highly recommended.",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### GET `/api/reviews`
Get all reviews.

**Query Parameters:**
- `book_id` (int, optional): Filter by book
- `user_id` (int, optional): Filter by user

**Response (200):**
```json
[
  {
    "id": 1,
    "book": { ... },
    "user": { ... },
    "rating": 5,
    "content": "Excellent book! Highly recommended.",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### PATCH `/api/reviews/{review_id}`
Update review.

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "rating": 4,
  "content": "Updated review content."
}
```

#### DELETE `/api/reviews/{review_id}`
Delete review.

**Headers:** `Authorization: Bearer <token>`

**Response (204):** No content

### Recommendations (`/api/recommendations`)

#### GET `/api/recommendations`
Get personalized book recommendations.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `genres` (string, optional): Comma-separated genres
- `limit` (int, optional): Number of recommendations (default: 10)

**Response (200):**
```json
[
  {
    "title": "Recommended Book",
    "author": "Author Name",
    "genre": "Fiction",
    "reason": "Based on your love for mystery novels",
    "description": "A gripping thriller that will keep you guessing"
  }
]
```

## WebSocket Endpoints

### `/ws/chat/{exchange_id}`
Real-time chat connection.

**Authentication:** JWT token in query parameter
```
ws://localhost:8000/ws/chat/1?token=<access_token>
```

**Message Format:**
```json
{
  "type": "message",
  "data": {
    "id": 1,
    "sender": {
      "id": 1,
      "username": "sender"
    },
    "content": "Hello!",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Rate Limiting
- **Authentication endpoints**: 5 requests per minute
- **General endpoints**: 100 requests per minute
- **WebSocket connections**: 10 connections per user

## Data Models

### BookGenre Enum
- `fiction`
- `non_fiction`
- `fantasy`
- `sci_fi`
- `mystery`
- `romance`
- `thriller`
- `horror`
- `biography`
- `history`
- `science`
- `self_help`
- `children`
- `poetry`
- `other`

### BookCondition Enum
- `new`
- `like_new`
- `good`
- `fair`
- `poor`

### ExchangeStatus Enum
- `pending`
- `accepted`
- `rejected`
- `completed`

## Testing
Use the provided test endpoints for development:
- `GET /api/health` - Health check
- `POST /api/test/auth` - Test authentication

## SDK Examples

### JavaScript/TypeScript
```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Get books
const books = await api.get('/books');

// Create exchange
const exchange = await api.post('/exchanges', {
  requested_book_id: 2,
  offered_book_id: 1,
  message: 'Let\'s exchange!'
});
```

### Python
```python
import requests

headers = {'Authorization': f'Bearer {token}'}

# Get books
response = requests.get('http://localhost:8000/api/books', headers=headers)
books = response.json()

# Create exchange
exchange_data = {
    'requested_book_id': 2,
    'offered_book_id': 1,
    'message': 'Let\'s exchange!'
}
response = requests.post('http://localhost:8000/api/exchanges', 
                         json=exchange_data, headers=headers)
exchange = response.json()
```
