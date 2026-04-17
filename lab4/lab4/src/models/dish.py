class Dish:

    def __init__(self, name: str, price: float, category: str = "general"):
        if not name or not name.strip():
            raise ValueError("Назва страви не може бути порожньою")
        if price < 0:
            raise ValueError("Ціна не може бути від'ємною")
        self._name = name.strip()
        self._price = price
        self._category = category

    @property
    def name(self) -> str:
        return self._name

    @property
    def price(self) -> float:
        return self._price

    @property
    def category(self) -> str:
        return self._category

    def __repr__(self) -> str:
        return f"Dish(name='{self._name}', price={self._price}, category='{self._category}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Dish):
            return False
        return self._name == other._name and self._price == other._price
