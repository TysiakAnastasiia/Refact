import json
import urllib.request

from app.core.config import settings
from app.models import BookGenre


GENRE_LABELS = {
    BookGenre.fiction: "Художня проза",
    BookGenre.non_fiction: "Нон-фікшн",
    BookGenre.fantasy: "Фентезі",
    BookGenre.sci_fi: "Наукова фантастика",
    BookGenre.mystery: "Детектив",
    BookGenre.romance: "Романтика",
    BookGenre.thriller: "Трилер",
    BookGenre.horror: "Жахи",
    BookGenre.biography: "Біографія",
    BookGenre.history: "Історія",
    BookGenre.science: "Наука",
    BookGenre.self_help: "Саморозвиток",
    BookGenre.children: "Дитяча",
    BookGenre.poetry: "Поезія",
    BookGenre.other: "Інше",
}

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models"
    "/gemini-2.0-flash:generateContent?key={key}"
)


class RecommendationService:

    async def get_recommendations(
        self,
        favorite_genres: list[str],
        read_books: list[str],
        count: int = 5,
    ) -> list[dict]:
        genres_str = ", ".join(favorite_genres) if favorite_genres else "різні жанри"
        books_str = "; ".join(read_books[:10]) if read_books else "не вказано"

        prompt = f"""Ти — книжковий експерт. Порекомендуй {count} книг на основі вподобань користувача.

Улюблені жанри: {genres_str}
Прочитані книги: {books_str}

Відповідай ТІЛЬКИ валідним JSON масивом (без markdown, без пояснень):
[
  {{
    "title": "Назва книги",
    "author": "Автор",
    "genre": "Жанр",
    "reason": "Коротке пояснення чому рекомендуємо (1-2 речення)"
  }}
]

Рекомендуй різноманітні книги — як класику, так і сучасні твори."""

        body = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 1000, "temperature": 0.7},
        }).encode()

        url = GEMINI_URL.format(key=settings.gemini_api_key)
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            raw = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            return []

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []
