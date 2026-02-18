# -*- coding: utf-8 -*-
"""
Система "Інтернет-магазин"
Лабораторна робота 3 — реалізація класів на основі UML-діаграм
"""

from datetime import datetime
from typing import List, Optional


# Product
class Product:
    """Товар в магазині."""

    def __init__(self, product_id: int, name: str, price: float, stock: int):
        self.__product_id = product_id
        self.__name = name
        self.__price = price
        self.__stock = stock  # кількість на складі

    #  Getters 
    def get_id(self) -> int:
        return self.__product_id

    def get_name(self) -> str:
        return self.__name

    def get_price(self) -> float:
        return self.__price

    def get_stock(self) -> int:
        return self.__stock

    #  Methods 
    def set_price(self, price: float) -> None:
        if price < 0:
            raise ValueError("Ціна не може бути від'ємною")
        self.__price = price

    def update_stock(self, quantity: int) -> None:
        """Додає або списує товар зі складу."""
        if self.__stock + quantity < 0:
            raise ValueError("Недостатньо товару на складі")
        self.__stock += quantity

    def is_available(self) -> bool:
        return self.__stock > 0

    def __repr__(self):
        return f"Product({self.__name}, {self.__price} грн, склад: {self.__stock})"


# CartItem — один рядок у кошику (товар + кількість)

class CartItem:
    """Позиція в кошику: товар та кількість."""

    def __init__(self, product: Product, quantity: int):
        if quantity <= 0:
            raise ValueError("Кількість має бути більше 0")
        self.__product = product
        self.__quantity = quantity

    def get_product(self) -> Product:
        return self.__product

    def get_quantity(self) -> int:
        return self.__quantity

    def set_quantity(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Кількість має бути більше 0")
        self.__quantity = quantity

    def subtotal(self) -> float:
        return self.__product.get_price() * self.__quantity

    def __repr__(self):
        return f"CartItem({self.__product.get_name()} x{self.__quantity})"


# Order

class Order:
    """Замовлення користувача."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"

    def __init__(self, order_id: int, user):
        self.__order_id = order_id
        self.__user = user
        self.__items: List[CartItem] = []
        self.__status = self.STATUS_PENDING
        self.__created_at = datetime.now()

    def get_id(self) -> int:
        return self.__order_id

    def get_user(self):
        return self.__user

    def get_status(self) -> str:
        return self.__status

    def get_items(self) -> List[CartItem]:
        return list(self.__items)

    def get_created_at(self) -> datetime:
        return self.__created_at

    def add_product(self, product: Product, quantity: int = 1) -> None:
        """Додає товар до замовлення."""
        if not product.is_available():
            raise ValueError(f"Товар '{product.get_name()}' недоступний")
        if quantity > product.get_stock():
            raise ValueError("Недостатньо товару на складі")
        # Якщо товар вже є — збільшуємо кількість
        for item in self.__items:
            if item.get_product().get_id() == product.get_id():
                item.set_quantity(item.get_quantity() + quantity)
                return
        self.__items.append(CartItem(product, quantity))

    def remove_product(self, product_id: int) -> None:
        """Видаляє товар із замовлення."""
        self.__items = [i for i in self.__items if i.get_product().get_id() != product_id]

    def calculate_total(self) -> float:
        """Рахує загальну суму замовлення."""
        return sum(item.subtotal() for item in self.__items)

    def confirm(self) -> None:
        if self.__status != self.STATUS_PENDING:
            raise ValueError("Можна підтвердити лише нове замовлення")
        if not self.__items:
            raise ValueError("Замовлення порожнє")
        self.__status = self.STATUS_CONFIRMED

    def cancel(self) -> None:
        if self.__status in (self.STATUS_SHIPPED, self.STATUS_DELIVERED):
            raise ValueError("Не можна скасувати відправлене замовлення")
        self.__status = self.STATUS_CANCELLED

    def __repr__(self):
        return f"Order(#{self.__order_id}, {self.__status}, {self.calculate_total():.2f} грн)"


# User

class User:
    """Користувач інтернет-магазину."""

    def __init__(self, user_id: int, username: str, email: str, password: str):
        self.__user_id = user_id
        self.__username = username
        self.__email = email
        self.__password = password
        self.__orders: List[Order] = []
        self.__is_logged_in = False
        self._order_counter = 0  # лічильник для генерації id замовлень

    def get_id(self) -> int:
        return self.__user_id

    def get_username(self) -> str:
        return self.__username

    def get_email(self) -> str:
        return self.__email

    def is_logged_in(self) -> bool:
        return self.__is_logged_in

    def get_orders(self) -> List[Order]:
        return list(self.__orders)

    def register(self) -> str:
        """Реєстрація — повертає повідомлення про успіх."""
        return f"Користувача '{self.__username}' успішно зареєстровано"

    def login(self, password: str) -> bool:
        """Вхід у систему."""
        if password == self.__password:
            self.__is_logged_in = True
            return True
        return False

    def logout(self) -> None:
        self.__is_logged_in = False

    def place_order(self) -> Order:
        """Створює нове замовлення для користувача."""
        if not self.__is_logged_in:
            raise PermissionError("Потрібно увійти в систему")
        self._order_counter += 1
        order = Order(self._order_counter, self)
        self.__orders.append(order)
        return order

    def view_orders(self) -> List[Order]:
        return self.get_orders()

    def __repr__(self):
        return f"User({self.__username}, {self.__email})"


# Admin (розширює User)

class Admin(User):
    """Адміністратор магазину."""

    def __init__(self, user_id: int, username: str, email: str, password: str):
        super().__init__(user_id, username, email, password)

    def add_product(self, catalog, product: Product) -> None:
        catalog.add_product(product)

    def remove_product(self, catalog, product_id: int) -> None:
        catalog.remove_product(product_id)

    def update_product_price(self, product: Product, new_price: float) -> None:
        product.set_price(new_price)


# Catalog

class Catalog:
    """Каталог товарів магазину."""

    def __init__(self):
        self.__products: List[Product] = []

    def add_product(self, product: Product) -> None:
        self.__products.append(product)

    def remove_product(self, product_id: int) -> None:
        self.__products = [p for p in self.__products if p.get_id() != product_id]

    def search(self, query: str) -> List[Product]:
        """Пошук товарів за назвою (без урахування регістру)."""
        query_lower = query.lower()
        return [p for p in self.__products if query_lower in p.get_name().lower()]

    def get_all(self) -> List[Product]:
        return list(self.__products)

    def get_by_id(self, product_id: int) -> Optional[Product]:
        for p in self.__products:
            if p.get_id() == product_id:
                return p
        return None
