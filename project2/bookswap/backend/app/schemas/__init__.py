from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import BookGenre, BookCondition, ExchangeStatus


#  Auth 

class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


#  User 

class UserBase(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    city: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    city: Optional[str] = None
    avatar_url: Optional[str] = None


class UserPublic(BaseModel):
    id: int
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    city: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


#  Book 

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    author: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    isbn: Optional[str] = None
    cover_url: Optional[str] = None
    genre: BookGenre
    published_year: Optional[int] = Field(None, ge=1000, le=2100)
    language: str = "Ukrainian"
    condition: BookCondition = BookCondition.good
    is_available_for_exchange: bool = True

    @field_validator("isbn")
    @classmethod
    def validate_isbn(cls, v):
        if v and len(v.replace("-", "")) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 digits")
        return v


class BookUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = None
    condition: Optional[BookCondition] = None
    is_available_for_exchange: Optional[bool] = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    description: Optional[str]
    isbn: Optional[str]
    cover_url: Optional[str]
    genre: BookGenre
    published_year: Optional[int]
    language: str
    condition: BookCondition
    is_available_for_exchange: bool
    owner_id: int
    owner: UserPublic
    average_rating: Optional[float] = None
    review_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    items: list[BookResponse]
    total: int
    page: int
    page_size: int
    pages: int


#  Review 

class ReviewCreate(BaseModel):
    book_id: int
    rating: int = Field(ge=1, le=5)
    content: Optional[str] = Field(None, max_length=2000)


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    content: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    rating: int
    content: Optional[str]
    user: UserPublic
    book_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


#  Exchange 

class ExchangeCreate(BaseModel):
    offered_book_id: Optional[int] = None
    requested_book_id: int
    message: Optional[str] = Field(None, max_length=500)


class ExchangeResponse(BaseModel):
    id: int
    status: ExchangeStatus
    message: Optional[str]
    requester: UserPublic
    owner: UserPublic
    offered_book: Optional[BookResponse] = None
    requested_book: BookResponse
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


#  Wishlist 

class WishlistItemResponse(BaseModel):
    id: int
    book: BookResponse
    added_at: datetime

    class Config:
        from_attributes = True


#  Chat 

class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class MessageResponse(BaseModel):
    id: int
    exchange_id: int
    sender: UserPublic
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


#  Recommendations 

class RecommendationResponse(BaseModel):
    title: str
    author: str
    genre: str
    reason: str
