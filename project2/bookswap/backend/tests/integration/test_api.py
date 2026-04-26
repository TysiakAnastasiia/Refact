"""
Integration tests — test full API endpoints with test database.
Run: pytest tests/integration/ -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.session import Base, get_db
from app.core.security import get_password_hash
from app.models import User, Book, BookGenre, BookCondition

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session) -> dict:
    user = User(
        email="alice@example.com",
        username="alice",
        hashed_password=get_password_hash("password123"),
        full_name="Alice Books",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return {"user": user, "password": "password123"}


@pytest_asyncio.fixture
async def auth_headers(client, test_user) -> dict:
    resp = await client.post("/api/auth/login", json={
        "email": test_user["user"].email,
        "password": test_user["password"],
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─── Auth integration tests ───────────────────────────────────────────────────

class TestAuthIntegration:
    @pytest.mark.asyncio
    async def test_register_success(self, client):
        resp = await client.post("/api/auth/register", json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "Password123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client, test_user):
        resp = await client.post("/api/auth/register", json={
            "email": test_user["user"].email,
            "username": "otherusername",
            "password": "Password123",
        })
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, client, test_user):
        resp = await client.post("/api/auth/login", json={
            "email": test_user["user"].email,
            "password": test_user["password"],
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client, test_user):
        resp = await client.post("/api/auth/login", json={
            "email": test_user["user"].email,
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, client, auth_headers, test_user):
        resp = await client.get("/api/users/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == test_user["user"].email

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client):
        resp = await client.get("/api/users/me")
        assert resp.status_code == 401


# ─── Books integration tests ──────────────────────────────────────────────────

class TestBooksIntegration:
    @pytest.mark.asyncio
    async def test_create_book(self, client, auth_headers):
        resp = await client.post("/api/books", headers=auth_headers, json={
            "title": "1984",
            "author": "George Orwell",
            "genre": "fiction",
            "condition": "good",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "1984"
        assert data["author"] == "George Orwell"

    @pytest.mark.asyncio
    async def test_create_book_unauthenticated(self, client):
        resp = await client.post("/api/books", json={
            "title": "Test", "author": "Author", "genre": "fiction",
        })
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_list_books(self, client, auth_headers):
        await client.post("/api/books", headers=auth_headers, json={
            "title": "Dune", "author": "Frank Herbert", "genre": "sci_fi",
        })
        resp = await client.get("/api/books")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_search_books_by_genre(self, client, auth_headers):
        await client.post("/api/books", headers=auth_headers, json={
            "title": "Fantasy Book", "author": "Fantasy Author", "genre": "fantasy",
        })
        resp = await client.get("/api/books?genre=fantasy")
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert all(b["genre"] == "fantasy" for b in items)

    @pytest.mark.asyncio
    async def test_get_book_not_found(self, client):
        resp = await client.get("/api/books/99999")
        assert resp.status_code == 404


# ─── Exchange integration tests ───────────────────────────────────────────────

class TestExchangeIntegration:
    @pytest.mark.asyncio
    async def test_successful_exchange_flow(self, client, db_session):
        """Scenario: Alice requests Bob's book, Bob accepts."""
        # Register Alice
        resp_alice = await client.post("/api/auth/register", json={
            "email": "alice2@example.com",
            "username": "alice2",
            "password": "Password123",
        })
        alice_token = resp_alice.json()["access_token"]
        alice_headers = {"Authorization": f"Bearer {alice_token}"}

        # Register Bob
        resp_bob = await client.post("/api/auth/register", json={
            "email": "bob@example.com",
            "username": "bob",
            "password": "Password123",
        })
        bob_token = resp_bob.json()["access_token"]
        bob_headers = {"Authorization": f"Bearer {bob_token}"}

        # Alice adds her book
        alice_book = await client.post("/api/books", headers=alice_headers, json={
            "title": "Alice's Book", "author": "Alice", "genre": "fiction",
            "is_available_for_exchange": True,
        })
        alice_book_id = alice_book.json()["id"]

        # Bob adds his book
        bob_book = await client.post("/api/books", headers=bob_headers, json={
            "title": "Bob's Book", "author": "Bob", "genre": "fantasy",
            "is_available_for_exchange": True,
        })
        bob_book_id = bob_book.json()["id"]

        # Alice requests Bob's book
        exchange_resp = await client.post("/api/exchanges", headers=alice_headers, json={
            "offered_book_id": alice_book_id,
            "requested_book_id": bob_book_id,
            "message": "Hi Bob, want to swap?",
        })
        assert exchange_resp.status_code == 201
        exchange_id = exchange_resp.json()["id"]
        assert exchange_resp.json()["status"] == "pending"

        # Bob accepts
        accept_resp = await client.patch(
            f"/api/exchanges/{exchange_id}/accept",
            headers=bob_headers,
        )
        assert accept_resp.status_code == 200
        assert accept_resp.json()["status"] == "accepted"

    @pytest.mark.asyncio
    async def test_blocked_reader_exchange_fails(self, client):
        """Unauthenticated user cannot create exchange."""
        resp = await client.post("/api/exchanges", json={
            "offered_book_id": 1, "requested_book_id": 2,
        })
        assert resp.status_code == 401
