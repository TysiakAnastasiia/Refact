import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from Refactored import TennisGame


def make_game(p1_pts: int, p2_pts: int,
              p1_name: str = "Alice", p2_name: str = "Bob") -> TennisGame:
    """Створює гру і симулює задану кількість очок."""
    game = TennisGame(p1_name, p2_name)
    for i in range(max(p1_pts, p2_pts)):
        if i < p1_pts:
            game.won_point(p1_name)
        if i < p2_pts:
            game.won_point(p2_name)
    return game


# Тест 1: Початковий рахунок — Love-All
def test_initial_score_is_love_all():
    """На початку гри рахунок повинен бути Love-All."""
    game = TennisGame("Alice", "Bob")
    assert game.score() == "Love-All"

# Тест 2: Нічиї до Deuce
@pytest.mark.parametrize("pts, expected", [
    (0, "Love-All"),
    (1, "Fifteen-All"),
    (2, "Thirty-All"),
    (3, "Forty-All"),
])
def test_tied_scores_before_deuce(pts, expected):
    """Нічия при 0-3 очках кожного гравця дає відповідний X-All."""
    game = make_game(pts, pts)
    assert game.score() == expected

# Тест 3: Deuce при рівних очках >= 4
@pytest.mark.parametrize("pts", [4, 5, 6, 10])
def test_deuce_when_both_above_three(pts):
    """Якщо обидва набрали >= 4 і рівно — Deuce."""
    game = make_game(pts, pts)
    assert game.score() == "Deuce"

# Тест 4: Advantage першого гравця
def test_advantage_player1():
    """Перший гравець на одне очко попереду після Deuce → Advantage P1."""
    game = make_game(4, 3)
    assert game.score() == "Advantage Alice"

# Тест 5: Advantage другого гравця
def test_advantage_player2():
    """Другий гравець на одне очко попереду після Deuce → Advantage P2."""
    game = make_game(3, 4)
    assert game.score() == "Advantage Bob"

# Тест 6: Win для першого гравця (класична перемога 4:0..2)
@pytest.mark.parametrize("p1, p2", [(4, 0), (4, 1), (4, 2)])
def test_win_player1_before_deuce(p1, p2):
    """Перший гравець виграє з рахунком 4:0, 4:1 або 4:2."""
    game = make_game(p1, p2)
    assert game.score() == "Win for Alice"

# Тест 7: Win для другого гравця (класична перемога)
@pytest.mark.parametrize("p1, p2", [(0, 4), (1, 4), (2, 4)])
def test_win_player2_before_deuce(p1, p2):
    """Другий гравець виграє з рахунком 0:4, 1:4 або 2:4."""
    game = make_game(p1, p2)
    assert game.score() == "Win for Bob"

# Тест 8: Win після Deuce (з різницею >= 2)
def test_win_after_deuce_player1():
    """Після Deuce: якщо P1 на 2 очки попереду → Win for P1."""
    game = make_game(6, 4)
    assert game.score() == "Win for Alice"

def test_win_after_deuce_player2():
    """Після Deuce: якщо P2 на 2 очки попереду → Win for P2."""
    game = make_game(4, 6)
    assert game.score() == "Win for Bob"

# Тест 9: Звичайні рахунки (не нічия, до 4 очок)
@pytest.mark.parametrize("p1, p2, expected", [
    (1, 0, "Fifteen-Love"),
    (0, 1, "Love-Fifteen"),
    (2, 1, "Thirty-Fifteen"),
    (3, 2, "Forty-Thirty"),
    (2, 3, "Thirty-Forty"),
    (3, 1, "Forty-Fifteen"),
])
def test_regular_scores(p1, p2, expected):
    """Перевіряє текстові рахунки у звичайних ситуаціях."""
    game = make_game(p1, p2)
    assert game.score() == expected

# Тест 10: Назви гравців правильно відображаються у Advantage і Win
def test_custom_player_names_in_advantage_and_win():
    """Кастомні імена гравців повинні відображатись у рядку рахунку."""
    game = make_game(4, 3, p1_name="Serena", p2_name="Venus")
    assert game.score() == "Advantage Serena"

    game2 = make_game(3, 4, p1_name="Serena", p2_name="Venus")
    assert game2.score() == "Advantage Venus"

    game3 = make_game(6, 4, p1_name="Serena", p2_name="Venus")
    assert game3.score() == "Win for Serena"

# Тест 11: won_point правильно нараховує очки
def test_won_point_increments_correct_player():
    """won_point повинен додавати очко лише названому гравцеві."""
    game = TennisGame("Alice", "Bob")
    game.won_point("Alice")
    game.won_point("Alice")
    game.won_point("Bob")
    # 2:1 → Thirty-Fifteen
    assert game.score() == "Thirty-Fifteen"

# Тест 12: Тривала гра — багаторазовий Deuce і Advantage
def test_long_game_multiple_deuce():
    """Симулює гру, де рахунок багато разів повертається до Deuce."""
    game = TennisGame("Alice", "Bob")
    # Доводимо до 3:3 → Forty-All
    for _ in range(3):
        game.won_point("Alice")
        game.won_point("Bob")
    assert game.score() == "Forty-All"

    # 4:4 → Deuce
    game.won_point("Alice")
    game.won_point("Bob")
    assert game.score() == "Deuce"

    # 5:4 → Advantage Alice
    game.won_point("Alice")
    assert game.score() == "Advantage Alice"

    # 5:5 → Deuce знову
    game.won_point("Bob")
    assert game.score() == "Deuce"

    # 5:6 → Advantage Bob
    game.won_point("Bob")
    assert game.score() == "Advantage Bob"

    # 6:6 → Deuce знову
    game.won_point("Alice")
    assert game.score() == "Deuce"

    # 7:6 → Alice виграє
    game.won_point("Alice")
    game.won_point("Alice")
    assert game.score() == "Win for Alice"

# Тест 13: Некоректна спроба передати не того гравця — очко іде P2
def test_unknown_player_name_scores_for_player2():
    """Якщо передано невідоме ім'я, очко йде player2 (поточна поведінка)."""
    game = TennisGame("Alice", "Bob")
    game.won_point("Unknown")  # не Alice → очко Бобу
    assert game.score() == "Love-Fifteen"