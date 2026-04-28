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
            # Dynamic fallback recommendations based on user preferences
            return self._get_fallback_recommendations(favorite_genres, read_books, count)

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

    def _get_fallback_recommendations(self, favorite_genres: list[str], read_books: list[str], count: int = 3) -> list[dict]:
        """Dynamic fallback recommendations based on user preferences"""
        
        # Genre-based book pools
        genre_books = {
            "детектив": [
                {"title": "Дівчина з татуюванням дракона", "author": "Стьюг Ларссон", "genre": "Детектив", "reason": "Сучасний шведський детектив з інтригою та несподіваними поворотами", "description": "Перша книга трилогії про Мікаель Блумквіст та Лісбет Саландер"},
                {"title": "Убивство у Східному експресі", "author": "Агата Крісті", "genre": "Детектив", "reason": "Класичний детектив від королеви жанру з Еркюлем Пуаро", "description": "Ідеальний приклад детективного роману з логічним розв'язанням"},
                {"title": "Шерлок Холмс", "author": "Артур Конан Дойл", "genre": "Детектив", "reason": "Незабутні пригоди найвідомішого детектива світу", "description": "Класика, яка сформувала жанр детективної літератури"},
            ],
            "поезія": [
                {"title": "Кобзар", "author": "Тарас Шевченко", "genre": "Поезія", "reason": "Фундаментальна збірка української поезії, що визначила національну ідентичність", "description": "Найважливіша поетична збірка в історії української літератури"},
                {"title": "Лірика", "author": "Пабло Неруда", "genre": "Поезія", "reason": "Чуттєва лірика нобелівського лауреата про любов і природу", "description": "Вірші, які торкаються найглибших струн душі"},
                {"title": "Вірші", "author": "Ліна Костенко", "genre": "Поезія", "reason": "Сучасна українська поезія з філософським підтекстом", "description": "Поезія, що поєднує традиції та сучасність"},
            ],
            "фантастика": [
                {"title": "Дюна", "author": "Френк Герберт", "genre": "Наукова фантастика", "reason": "Епічна космічна опера про політику, екологію та людську природу", "description": "Впливовий науково-фантастичний роман, що надихнув багато творів"},
                {"title": "Хранителі", "author": "Сергій Лук'яненко", "genre": "Фентезі", "reason": "Сучасне українське фентезі про світ нічних людей", "description": "Унікальне поєднання міської фентезі та філософських роздумів"},
                {"title": "Метро 2033", "author": "Дмитро Глуховський", "genre": "Постапокаліпсис", "reason": "Постапокаліптичний світ московського метро від українського автора", "description": "Напружена атмосфера та глибокі роздуми про людяність"},
            ],
            "романтика": [
                {"title": "Гордість і упередження", "author": "Джейн Остін", "genre": "Роман", "reason": "Класична історія кохання з британським гумором та соціальною сатирою", "description": "Чарівна романтична комедія звичаїв XIX століття"},
                {"title": "Тіні забутих предків", "author": "Михайло Коцюбинський", "genre": "Роман", "reason": "Лірична історія кохання на тлі карпатських пейзажів", "description": "Перлинка української літератури з поетичним стилем"},
                {"title": "Любов у часи холери", "author": "Габрієль Гарсія Маркес", "genre": "Роман", "reason": "Чарівна історія кохання, що витримує випробування часом", "description": "Магічний реалізм в інтерпретації теми вічного кохання"},
            ],
            "історія": [
                {"title": "Спадщина козацтва", "author": "В'ячеслав Липинський", "genre": "Історія", "reason": "Фундаментальна праця про українську державність та ідентичність", "description": "Класичний аналіз української історії та політичної думки"},
                {"title": "Київська Русь", "author": "Михайло Грушевський", "genre": "Історія", "reason": "Авторитетна історія України від заснування до XIV століття", "description": "Найповніша праця з ранньої історії України"},
                {"title": "Sapiens", "author": "Юваль Ной Харарі", "genre": "Нон-фікшн", "reason": "Захоплююча історія людства від появи Homo Sapiens до сьогодення", "description": "Популярна книга, що пояснює історію людства простою мовою"},
            ]
        }
        
        # Default recommendations for any genre
        default_books = [
            {"title": "Сто років самотності", "author": "Габрієль Гарсія Маркес", "genre": "Магічний реалізм", "reason": "Геніальний роман про історію Латинської Америки через долю сім'ї Буендіа", "description": "Шедевр світової літератури, що змінив уявлення про роман"},
            {"title": "1984", "author": "Джордж Орвелл", "genre": "Антиутопія", "reason": "Пророччий твір про тоталітаризм, який залишається актуальним досі", "description": "Класика, що змусить замислитися про свободу та суспільство"},
            {"title": "Маленький принц", "author": "Антуан де Сент-Екзюпері", "genre": "Філософська притча", "reason": "Чарівна історія про дружбу, любов і сенс життя, доступна всім вікам", "description": "Твір, який можна читати в будь-якому віці і знаходити новий сенс"},
            {"title": "Майстер і Маргарита", "author": "Михайло Булгаков", "genre": "Сатира", "reason": "Роман-міф про любов, добро та зло в радянській Москві", "description": "Найвідоміший роман Булгакова з багатошаровими символами"},
            {"title": "Аліса в Країні чудес", "author": "Льюїс Керрол", "genre": "Фентезі", "reason": "Чарівна пригода, яка надихає мріяти та мислити креативно", "description": "Класична казка для дорослих та дітей з філософським підтекстом"},
        ]
        
        # Select books based on user genres
        recommendations = []
        used_titles = set()
        
        # Add books from user's favorite genres
        for genre in favorite_genres:
            genre_lower = genre.lower()
            for key, books in genre_books.items():
                if key in genre_lower or genre_lower in key:
                    for book in books:
                        if book["title"] not in used_titles and len(recommendations) < count:
                            recommendations.append(book)
                            used_titles.add(book["title"])
        
        # Fill remaining slots with default books
        for book in default_books:
            if book["title"] not in used_titles and len(recommendations) < count:
                recommendations.append(book)
                used_titles.add(book["title"])
        
        return recommendations[:count]
