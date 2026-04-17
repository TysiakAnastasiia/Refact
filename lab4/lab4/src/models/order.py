from enum import Enum
from src.models.customer import Customer
from src.models.dish import Dish
from src.interfaces import ISubject, IObserver


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Order(ISubject):

    _id_counter = 0

    def __init__(self, customer: Customer, order_type: str = "regular"):
        if not isinstance(customer, Customer):
            raise TypeError("Очікується об'єкт Customer")
        Order._id_counter += 1
        self._id = Order._id_counter
        self._customer = customer
        self._dishes: list[Dish] = []
        self._status = OrderStatus.PENDING
        self._order_type = order_type
        self._observers: list[IObserver] = []

    @property
    def id(self) -> int:
        return self._id

    @property
    def customer(self) -> Customer:
        return self._customer

    @property
    def dishes(self) -> list[Dish]:
        return list(self._dishes)

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def order_type(self) -> str:
        return self._order_type

    def add_dish(self, dish: Dish) -> None:
        if not isinstance(dish, Dish):
            raise TypeError("Очікується об'єкт Dish")
        self._dishes.append(dish)

    def total_price(self) -> float:
        return sum(d.price for d in self._dishes)

    def confirm(self) -> None:
        self._status = OrderStatus.CONFIRMED
        self.notify()

    # --- Observer pattern ---
    def attach(self, observer: IObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IObserver) -> None:
        self._observers.remove(observer)

    def notify(self) -> None:
        for observer in self._observers:
            observer.update(self)

    def __repr__(self) -> str:
        return (f"Order(id={self._id}, customer='{self._customer.name}', "
                f"type='{self._order_type}', status='{self._status.value}', "
                f"dishes={len(self._dishes)})")
