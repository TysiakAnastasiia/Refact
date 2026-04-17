import threading
from src.interfaces import IObserver, IOrderFactory, IDatabase
from src.models.customer import Customer
from src.models.dish import Dish
from src.models.order import Order

class OrderDatabase(IDatabase):
    """
    Singleton: єдиний екземпляр бази даних замовлень.
    Thread-safe реалізація через подвійну перевірку блокування.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._orders = []
        return cls._instance

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._instance = None

    def save_order(self, order: Order) -> None:
        if not isinstance(order, Order):
            raise TypeError("Очікується об'єкт Order")
        self._orders.append(order)

    def get_all_orders(self) -> list:
        return list(self._orders)

    def get_by_customer(self, customer_name: str) -> list:
        return [o for o in self._orders if o.customer.name == customer_name]

    def clear(self) -> None:
        self._orders.clear()

    def __len__(self) -> int:
        return len(self._orders)


class KitchenNotifier(IObserver):
    """
    Observer: сповіщає кухню про нові підтверджені замовлення.
    Відповідає лише за оповіщення (SRP).
    """

    def __init__(self):
        self._notifications: list[str] = []

    def update(self, order: Order) -> None:
        message = (
            f"[КУХНЯ] Нове замовлення #{order.id} "
            f"від '{order.customer.name}' | "
            f"тип: {order.order_type} | "
            f"страв: {len(order.dishes)} | "
            f"сума: {order.total_price():.2f} грн"
        )
        self._notifications.append(message)
        print(message)

    def get_notifications(self) -> list[str]:
        return list(self._notifications)

    def clear(self) -> None:
        self._notifications.clear()

    @property
    def notification_count(self) -> int:
        return len(self._notifications)


class RegularOrderFactory(IOrderFactory):
    """Фабрика звичайних замовлень"""

    def create_order(self, customer: Customer, dishes: list) -> Order:
        if not isinstance(customer, Customer):
            raise TypeError("Очікується об'єкт Customer")
        order = Order(customer, order_type="regular")
        for dish in dishes:
            order.add_dish(dish)
        return order


class BulkOrderFactory(IOrderFactory):
    """Фабрика масових замовлень (для корпоративних клієнтів)"""

    BULK_DISCOUNT = 0.10  # 10% знижка

    def create_order(self, customer: Customer, dishes: list) -> Order:
        if not isinstance(customer, Customer):
            raise TypeError("Очікується об'єкт Customer")
        if len(dishes) < 5:
            raise ValueError("Масове замовлення вимагає щонайменше 5 страв")
        order = Order(customer, order_type="bulk")
        for dish in dishes:
            order.add_dish(dish)
        return order

    @property
    def discount(self) -> float:
        return self.BULK_DISCOUNT


class OrderFactoryProvider:
    """
    Провайдер фабрик замовлень (OCP — відкритий для розширення).
    Повертає потрібну фабрику за типом.
    """

    _factories = {
        "regular": RegularOrderFactory,
        "bulk": BulkOrderFactory,
    }

    @classmethod
    def get_factory(cls, order_type: str) -> IOrderFactory:
        factory_class = cls._factories.get(order_type)
        if not factory_class:
            raise ValueError(f"Невідомий тип замовлення: '{order_type}'. "
                             f"Доступні: {list(cls._factories.keys())}")
        return factory_class()

    @classmethod
    def register(cls, order_type: str, factory_class) -> None:
        """Реєстрація нового типу фабрики (OCP)"""
        cls._factories[order_type] = factory_class
