class Customer:

    def __init__(self, name: str, phone: str = ""):
        if not name or not name.strip():
            raise ValueError("Ім'я клієнта не може бути порожнім")
        self._name = name.strip()
        self._phone = phone

    @property
    def name(self) -> str:
        return self._name

    @property
    def phone(self) -> str:
        return self._phone

    def __repr__(self) -> str:
        return f"Customer(name='{self._name}', phone='{self._phone}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Customer):
            return False
        return self._name == other._name and self._phone == other._phone
