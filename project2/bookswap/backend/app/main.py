import json
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import decode_token
from app.api.routes import (
    auth_router,
    users_router,
    books_router,
    reviews_router,
    exchanges_router,
    wishlist_router,
    chat_router,
    recs_router,
    friends_router,
)


#  WebSocket Connection Manager


class ConnectionManager:
    """Manages active WebSocket connections per exchange room."""

    def __init__(self):
        self.active: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, exchange_id: int):
        await websocket.accept()
        self.active.setdefault(exchange_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, exchange_id: int):
        if exchange_id in self.active:
            self.active[exchange_id].discard(websocket)

    async def broadcast(
        self, exchange_id: int, message: dict, exclude: Optional[WebSocket] = None
    ):
        for ws in list(self.active.get(exchange_id, [])):
            if ws != exclude:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


#  App factory


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (use alembic in production)
    from app.db.session import engine, Base
    import app.models  # noqa: F401 — register models

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="BookSwap — Book Recommendations & Exchange Platform",
    lifespan=lifespan,
)

# CORS
# Тимчасово дозволяємо всі origins для вирішення проблеми
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Дозволяє запити з будь-яких адрес
    allow_credentials=True,
    allow_methods=["*"],  # Дозволяє всі методи (GET, POST, PUT, DELETE тощо)
    allow_headers=["*"],  # Дозволяє всі заголовки
)

# Routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(books_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(exchanges_router, prefix="/api")
app.include_router(wishlist_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(recs_router, prefix="/api")
app.include_router(friends_router, prefix="/api")


#  WebSocket endpoint


@app.websocket("/ws/chat/{exchange_id}")
async def websocket_chat(
    websocket: WebSocket,
    exchange_id: int,
    token: str = Query(...),
):
    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    await manager.connect(websocket, exchange_id)
    user_id = int(payload["sub"])

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            await manager.broadcast(
                exchange_id,
                {
                    "type": "message",
                    "exchange_id": exchange_id,
                    "sender_id": user_id,
                    "content": msg.get("content", ""),
                },
                exclude=websocket,
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket, exchange_id)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "version": "1.0.0"}
