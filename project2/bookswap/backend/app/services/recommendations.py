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
        count: int = 3,
    ) -> list[dict]:
        genres_str = ", ".join(favorite_genres) if favorite_genres else "різні жанри"
        books_str = "; ".join(read_books[:10]) if read_books else "не вказано"

        prompt = f"""Ти — всесвітньо відомий книжковий експерт з величезною базою даних літератури. Порекомендуй {count} книг на основі вподобань користувача.

Улюблені жанри: {genres_str}
Прочитані книги: {books_str}

Рекомендації можуть включати:
- Класичні твори світової літератури
- Сучасні бестселери
- Українську та зарубіжну літературу
- Книги, перекладені українською або оригінальні
- Рідкісні та відомі шедеври

Відповідай ТІЛЬКИ валідним JSON масивом (без markdown, без зайвих пояснень):
[
  {{
    "title": "Назва книги українською (або оригінальна якщо немає перекладу)",
    "author": "Автор",
    "genre": "Жанр",
    "reason": "Чому ця книга ідеально підходить користувачу (2-3 речення)",
    "description": "Що робить цю книгу особливою (1 речення)"
  }}
]

Обирай книги з різних країн та епох, які точно зацікавлять та розширять світогляд."""

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
        except Exception as e:
            print(f"AI recommendation error: {e}")
            # Fallback to diverse world literature recommendations
            return [
                {
                    "title": "Сто років самотності",
                    "author": "Габрієль Гарсія Маркес",
                    "genre": "Магічний реалізм",
                    "reason": "Геніальний роман про історію Латинської Америки через долю сім'ї Буендіа",
                    "description": "Шедевр світової літератури, що змінив уявлення про роман"
                },
                {
                    "title": "1984",
                    "author": "Джордж Орвелл",
                    "genre": "Антиутопія",
                    "reason": "Пророччий твір про тоталітаризм, який залишається актуальним досі",
                    "description": "Класика, що змусить замислитися про свободу та суспільство"
                },
                {
                    "title": "Маленький принц",
                    "author": "Антуан де Сент-Екзюпері",
                    "genre": "Філософська притча",
                    "reason": "Чарівна історія про дружбу, любов і сенс життя, доступна всім вікам",
                    "description": "Твір, який можна читати в будь-якому віці і знаходити новий сенс"
                }
            ]

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
