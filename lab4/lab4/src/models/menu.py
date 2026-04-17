from src.models.dish import Dish


class Menu:

    def __init__(self):
        self._dishes: list[Dish] = []

    def add_dish(self, dish: Dish) -> None:
        if not isinstance(dish, Dish):
            raise TypeError("Очікується об'єкт Dish")
        if self.contains_dish(dish):
            raise ValueError(f"Страва '{dish.name}' вже є в меню")
        self._dishes.append(dish)

    def remove_dish(self, dish: Dish) -> None:
        if not self.contains_dish(dish):
            raise ValueError(f"Страва '{dish.name}' не знайдена в меню")
        self._dishes.remove(dish)

    def contains_dish(self, dish: Dish) -> bool:
        return dish in self._dishes

    def get_all_dishes(self) -> list[Dish]:
        return list(self._dishes)

    def get_by_category(self, category: str) -> list[Dish]:
        return [d for d in self._dishes if d.category == category]

    def is_empty(self) -> bool:
        return len(self._dishes) == 0

    def __len__(self) -> int:
        return len(self._dishes)

    def __repr__(self) -> str:
        return f"Menu(dishes={len(self._dishes)})"
