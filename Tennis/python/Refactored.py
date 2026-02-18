# -*- coding: utf-8 -*-

# Аналіз проблем (Code Smells)
# 1. Дублювання коду: TennisGameDefactored1 і 2 і 3 реалізують одну й ту саму логіку по-різному. Метод won_point майже дентичний у всіх трьох класах.
#2. Магічні числа: числа 0,1,2,3,4 розкидані по коду без іменованих констант — незрозуміло, що вони означають.
# 3. Надмірна складність: TennisGameDefactored2.score() містить 10+ умовних гілок, які важко читати й підтримувати.
# 4. Погані назви: p1N, p2N, p1, p2 у Defactored3 — незрозумілі. P1Score/P2Score у Defactored2 — порушення PEP8 (CamelCase для методів замість snake_case).
# 5. Великий клас: Defactored2 містить допоміжні методи SetP1Score/SetP2Score, які використовуються лише в тестах — змішано відповідальності.


# Іменовані константи замість магічних чисел
SCORE_NAMES = ["Love", "Fifteen", "Thirty", "Forty"]  # замінює жорстко задані рядки по всьому коду

DEUCE_THRESHOLD = 3       # мінімум очок для можливості Deuce (обидва >= 4)
WIN_DIFF = 2              # різниця очок для перемоги після Deuce


class TennisGame:
    """
    Рефакторована версія тенісної гри.
    Об'єднує три дефакторовані класи в один чистий клас.

    Зміни порівняно з оригіналами:
    - Видалено дублювання між Defactored1/2/3 — залишено одну реалізацію.
    - Замінено магічні числа іменованими константами.
    - score() розбито на допоміжні методи для зменшення складності.
    - Назви змінних відповідають PEP8 і є зрозумілими.
    - Прибрано SetP1Score/SetP2Score з класу (не належать до відповідальності гри).
    """

    def __init__(self, player1_name: str, player2_name: str):
        self.player1_name = player1_name   # раніше: player1Name / p1N
        self.player2_name = player2_name   # раніше: player2Name / p2N
        self.p1_points = 0                 # раніше: p1points / p1
        self.p2_points = 0                 # раніше: p2points / p2

    def won_point(self, player_name: str) -> None:
        """Нараховує очко гравцю за іменем."""
        # Логіка ідентична у всіх трьох оригінальних класах — залишено одну реалізацію, прибрано дублювання.
        if player_name == self.player1_name:
            self.p1_points += 1
        else:
            self.p2_points += 1

    # Допоміжні методи (витягнуто з великого score() Defactored2)
    def _is_tied(self) -> bool:
        return self.p1_points == self.p2_points

    def _is_deuce_phase(self) -> bool:
        """Обидва гравці набрали >= 4 очок."""
        return self.p1_points >= 4 and self.p2_points >= 4

    def _score_name(self, points: int) -> str:
        """Повертає текстову назву рахунку (Love/Fifteen/Thirty/Forty)."""
        # Замінює повторювані словники/if-ланцюги у всіх трьох класах.
        return SCORE_NAMES[points]

    def score(self) -> str:
        """
        Повертає поточний рахунок у тенісному форматі.

        Рефакторинг: замінено складний монолітний if-ланцюг
        (особливо у Defactored2) на послідовні, зрозумілі гілки.
        """
        p1, p2 = self.p1_points, self.p2_points
        diff = p1 - p2

        #  Фаза Deuce або після (хоч один набрав >= 4) 
        if p1 >= 4 or p2 >= 4:
            if diff == 0:
                return "Deuce"
            leading = self.player1_name if diff > 0 else self.player2_name
            if abs(diff) == 1:
                return "Advantage " + leading
            return "Win for " + leading

        #  Нічия до Deuce 
        if self._is_tied():
            # Раніше: словник у Defactored1, if-if-if у Defactored2
            return self._score_name(p1) + "-All"

        #  Звичайний рахунок 
        # Раніше: цикл з tempScore у Defactored1, довгий if у Defactored2
        return self._score_name(p1) + "-" + self._score_name(p2)


# NOTE: Вказуємо на рефакторований клас
TennisGame = TennisGame

if __name__ == "__main__":
    game = TennisGame("Alice", "Bob")
    moves = ["Alice", "Alice", "Bob", "Alice", "Bob", "Bob", "Alice", "Bob", "Alice", "Alice"]
    for player in moves:
        game.won_point(player)
        print(f"{player} scores → {game.score()}")