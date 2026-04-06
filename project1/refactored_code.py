# pylint: disable=too-few-public-methods, missing-class-docstring, missing-function-docstring, missing-module-docstring
from __future__ import annotations
import datetime
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


# Техніка 1: Replace Magic Numbers with Named Constants
class DiscountThreshold:
    LOW    = 500
    MEDIUM = 1000
    HIGH   = 2000

class RatingThreshold:
    SILVER   = 500
    GOLD     = 2000
    PLATINUM = 5000

LOW_STOCK_THRESHOLD = 10


# Техніка 2: Replace Type Code with Enum
class CustomerType(Enum):
    REGULAR = "regular"
    VIP     = "vip"

class OrderStatus(Enum):
    NEW       = "new"
    CANCELLED = "cancelled"

class RatingLevel(Enum):
    BRONZE   = "Bronze"
    SILVER   = "Silver"
    GOLD     = "Gold"
    PLATINUM = "Platinum"


# Техніка 3: Replace Primitive Dict with Data Class
@dataclass
class Product:
    product_id: int
    name: str
    price: float
    stock: int

    def has_stock(self, qty: int) -> bool:
        return self.stock >= qty

    def deduct(self, qty: int) -> None:
        self.stock -= qty

    def restock(self, qty: int) -> None:
        if qty <= 0:
            raise ValueError("Кількість має бути більше 0")
        self.stock += qty

    def update_price(self, new_price: float) -> None:
        if new_price < 0:
            raise ValueError("Ціна не може бути від'ємною")
        self.price = new_price

    def is_low_stock(self) -> bool:
        return self.stock < LOW_STOCK_THRESHOLD


@dataclass
class Customer:
    customer_id: int
    full_name: str
    email: str
    customer_type: CustomerType


@dataclass
class Supplier:
    supplier_id: int
    name: str
    phone: str


@dataclass
class PromoCode:
    code: str
    discount_rate: float
    min_total: float
    active: bool = True

    def deactivate(self) -> None:
        self.active = False

    def is_applicable(self, total: float) -> bool:
        return self.active and total >= self.min_total


@dataclass
class OrderItem:
    product_id: int
    product_name: str
    quantity: int
    unit_price: float

    @property
    def line_total(self) -> float:
        return round(self.unit_price * self.quantity, 2)


@dataclass
class Order:
    order_id: int
    customer: Customer
    items: list[OrderItem]
    subtotal: float
    discount_percent: float
    discount_amount: float
    promo_code: Optional[str]
    promo_discount_percent: float
    promo_discount_amount: float
    total: float
    created_at: str
    status: OrderStatus = OrderStatus.NEW


# Техніка 4: Extract Method — логіка знижки
def calculate_discount_rate(customer_type: CustomerType, subtotal: float) -> float:
    if customer_type == CustomerType.VIP:
        return _vip_discount_rate(subtotal)
    return _regular_discount_rate(subtotal)

def _vip_discount_rate(subtotal: float) -> float:
    if subtotal > DiscountThreshold.HIGH:   return 0.20
    if subtotal > DiscountThreshold.MEDIUM: return 0.15
    if subtotal > DiscountThreshold.LOW:    return 0.10
    return 0.05

def _regular_discount_rate(subtotal: float) -> float:
    if subtotal > DiscountThreshold.HIGH:   return 0.10
    if subtotal > DiscountThreshold.MEDIUM: return 0.07
    if subtotal > DiscountThreshold.LOW:    return 0.05
    return 0.00


#  Техніка 5: Extract Method — логіка рейтингу
def calculate_rating(total_spent: float) -> RatingLevel:
    if total_spent >= RatingThreshold.PLATINUM: return RatingLevel.PLATINUM
    if total_spent >= RatingThreshold.GOLD:     return RatingLevel.GOLD
    if total_spent >= RatingThreshold.SILVER:   return RatingLevel.SILVER
    return RatingLevel.BRONZE


#  Техніка 6: Introduce Repository
class ProductRepository:
    def __init__(self) -> None:
        self._data: dict[int, Product] = {}

    def add(self, product: Product) -> None:
        self._data[product.product_id] = product

    def find(self, product_id: int) -> Optional[Product]:
        return self._data.get(product_id)

    def all(self) -> list[Product]:
        return list(self._data.values())

    def low_stock(self) -> list[Product]:
        return [p for p in self._data.values() if p.is_low_stock()]


class CustomerRepository:
    def __init__(self) -> None:
        self._data: dict[int, Customer] = {}

    def add(self, customer: Customer) -> None:
        self._data[customer.customer_id] = customer

    def find(self, customer_id: int) -> Optional[Customer]:
        return self._data.get(customer_id)

    def all(self) -> list[Customer]:
        return list(self._data.values())


class SupplierRepository:
    def __init__(self) -> None:
        self._data: dict[int, Supplier] = {}
        self._next_id = 1

    def add(self, supplier: Supplier) -> None:
        self._data[supplier.supplier_id] = supplier

    def find(self, supplier_id: int) -> Optional[Supplier]:
        return self._data.get(supplier_id)

    def all(self) -> list[Supplier]:
        return list(self._data.values())

    def next_id(self) -> int:
        current = self._next_id
        self._next_id += 1
        return current


class PromoRepository:
    def __init__(self) -> None:
        self._data: dict[str, PromoCode] = {}

    def add(self, promo: PromoCode) -> None:
        self._data[promo.code] = promo

    def find(self, code: str) -> Optional[PromoCode]:
        return self._data.get(code)

    def all(self) -> list[PromoCode]:
        return list(self._data.values())

    def exists(self, code: str) -> bool:
        return code in self._data


class OrderRepository:
    def __init__(self) -> None:
        self._data: dict[int, Order] = {}
        self._next_id = 1

    def save(self, order: Order) -> None:
        self._data[order.order_id] = order

    def find(self, order_id: int) -> Optional[Order]:
        return self._data.get(order_id)

    def all(self) -> list[Order]:
        return list(self._data.values())

    def by_customer(self, customer_id: int) -> list[Order]:
        return [o for o in self._data.values() if o.customer.customer_id == customer_id]

    def next_id(self) -> int:
        current = self._next_id
        self._next_id += 1
        return current


#  Техніка 7: Extract Class — Service Layer
class OrderService:
    def __init__(
        self,
        products: ProductRepository,
        customers: CustomerRepository,
        orders: OrderRepository,
        promos: PromoRepository,
    ) -> None:
        self._products  = products
        self._customers = customers
        self._orders    = orders
        self._promos    = promos

    #  Техніка 8: Decompose Method
    def place_order(
        self,
        customer_id: int,
        line_items: list[dict],
        promo_code: Optional[str] = None,
    ) -> Order:
        customer    = self._resolve_customer(customer_id)
        items       = self._build_items(line_items)
        subtotal    = self._subtotal(items)
        disc_rate   = calculate_discount_rate(customer.customer_type, subtotal)
        disc_amount = round(subtotal * disc_rate, 2)
        after_disc  = round(subtotal - disc_amount, 2)

        promo_obj, promo_disc_rate, promo_disc_amount = self._apply_promo(
            promo_code, after_disc
        )

        total = round(after_disc - promo_disc_amount, 2)
        self._deduct_stock(line_items)

        order = Order(
            order_id              = self._orders.next_id(),
            customer              = customer,
            items                 = items,
            subtotal              = subtotal,
            discount_percent      = round(disc_rate * 100, 2),
            discount_amount       = disc_amount,
            promo_code            = promo_obj.code if promo_obj else None,
            promo_discount_percent= round(promo_disc_rate * 100, 2),
            promo_discount_amount = promo_disc_amount,
            total                 = total,
            created_at            = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._orders.save(order)
        return order

    def cancel_order(self, order_id: int) -> None:
        order = self._orders.find(order_id)
        if order is None:
            raise ValueError(f"Замовлення #{order_id} не знайдено")
        if order.status != OrderStatus.NEW:
            raise ValueError(f"Не можна скасувати замовлення зі статусом '{order.status.value}'")
        order.status = OrderStatus.CANCELLED
        self._restore_stock(order)
        self._send_cancellation_email(order.customer.full_name, order_id)

    def get_orders(self, customer_id: int) -> list[Order]:
        return self._orders.by_customer(customer_id)

    def get_customer_summary(self, customer_id: int) -> dict:
        active = [
            o for o in self._orders.by_customer(customer_id)
            if o.status != OrderStatus.CANCELLED
        ]
        total_spent = round(sum(o.total for o in active), 2)
        return {
            "order_count": len(active),
            "total_spent": total_spent,
            "rating": calculate_rating(total_spent).value,
        }

    def get_revenue(self) -> float:
        return round(
            sum(o.total for o in self._orders.all() if o.status != OrderStatus.CANCELLED),
            2,
        )

    def get_all_orders(self) -> list[Order]:
        return self._orders.all()

    #  Техніка 9: Separate Query from Command
    def _resolve_customer(self, customer_id: int) -> Customer:
        customer = self._customers.find(customer_id)
        if customer is None:
            raise ValueError(f"Клієнта з ID={customer_id} не знайдено")
        return customer

    def _build_items(self, line_items: list[dict]) -> list[OrderItem]:
        result = []
        for item in line_items:
            product = self._products.find(item["product_id"])
            if product is None:
                raise ValueError(f"Товар з ID={item['product_id']} не знайдено")
            if not product.has_stock(item["quantity"]):
                raise ValueError(f"Недостатньо товару '{product.name}' на складі")
            result.append(OrderItem(
                product_id   = product.product_id,
                product_name = product.name,
                quantity     = item["quantity"],
                unit_price   = product.price,
            ))
        return result

    def _subtotal(self, items: list[OrderItem]) -> float:
        return round(sum(i.line_total for i in items), 2)

    def _apply_promo(
        self, code: Optional[str], after_disc: float
    ) -> tuple[Optional[PromoCode], float, float]:
        if not code:
            return None, 0.0, 0.0
        promo = self._promos.find(code)
        if promo is None or not promo.is_applicable(after_disc):
            return None, 0.0, 0.0
        amount = round(after_disc * promo.discount_rate, 2)
        return promo, promo.discount_rate, amount

    def _deduct_stock(self, line_items: list[dict]) -> None:
        for item in line_items:
            product = self._products.find(item["product_id"])
            if product:
                product.deduct(item["quantity"])

    def _restore_stock(self, order: Order) -> None:
        for item in order.items:
            product = self._products.find(item.product_id)
            if product:
                product.restock(item.quantity)

    @staticmethod
    def _send_cancellation_email(full_name: str, order_id: int) -> None:
        print(f"Email надіслано клієнту {full_name} про скасування замовлення #{order_id}")


class PromoService:
    def __init__(self, promos: PromoRepository) -> None:
        self._promos = promos

    def add(self, code: str, discount_rate: float, min_total: float) -> PromoCode:
        if self._promos.exists(code):
            raise ValueError(f"Промокод {code} вже існує")
        if not (0 < discount_rate < 1):
            raise ValueError("Знижка має бути між 0 і 1")
        if min_total < 0:
            raise ValueError("Мінімальна сума не може бути від'ємною")
        promo = PromoCode(code=code, discount_rate=discount_rate, min_total=min_total)
        self._promos.add(promo)
        return promo

    def deactivate(self, code: str) -> None:
        promo = self._promos.find(code)
        if promo is None:
            raise ValueError(f"Промокод {code} не знайдено")
        if not promo.active:
            raise ValueError(f"Промокод {code} вже неактивний")
        promo.deactivate()

    def list_all(self) -> list[PromoCode]:
        return self._promos.all()


class SupplierService:
    def __init__(self, suppliers: SupplierRepository, products: ProductRepository) -> None:
        self._suppliers = suppliers
        self._products  = products

    def add_supplier(self, name: str, phone: str) -> Supplier:
        supplier = Supplier(
            supplier_id = self._suppliers.next_id(),
            name        = name,
            phone       = phone,
        )
        self._suppliers.add(supplier)
        return supplier

    def restock(self, product_id: int, qty: int, supplier_id: int) -> None:
        product  = self._products.find(product_id)
        supplier = self._suppliers.find(supplier_id)
        if product is None:
            raise ValueError(f"Товар з ID={product_id} не знайдено")
        if supplier is None:
            raise ValueError(f"Постачальника з ID={supplier_id} не знайдено")
        product.restock(qty)

    def restock_low_items(self, supplier_id: int, qty: int) -> list[Product]:
        low = self._products.low_stock()
        for product in low:
            self.restock(product.product_id, qty, supplier_id)
        return low

    def list_suppliers(self) -> list[Supplier]:
        return self._suppliers.all()


class RatingService:
    def __init__(self, customers: CustomerRepository, orders: OrderRepository) -> None:
        self._customers = customers
        self._orders    = orders

    def get_rating(self, customer_id: int) -> dict:
        customer = self._customers.find(customer_id)
        if customer is None:
            raise ValueError(f"Клієнта з ID={customer_id} не знайдено")
        active_orders = [
            o for o in self._orders.by_customer(customer_id)
            if o.status != OrderStatus.CANCELLED
        ]
        total_spent = round(sum(o.total for o in active_orders), 2)
        return {
            "customer_id": customer_id,
            "full_name":   customer.full_name,
            "order_count": len(active_orders),
            "total_spent": total_spent,
            "rating":      calculate_rating(total_spent).value,
        }

    #  Техніка 10: Introduce Factory Method / Replace Loop with enumerate
    def all_ratings_sorted(self) -> list[dict]:
        ratings = [self.get_rating(c.customer_id) for c in self._customers.all()]
        return sorted(ratings, key=lambda r: r["total_spent"], reverse=True)


#  Техніка 11: Introduce Factory
def build_default_store() -> tuple[
    ProductRepository, CustomerRepository,
    SupplierRepository, PromoRepository
]:
    products = ProductRepository()
    for p in [
        Product(1, "Яблуко", 15.0, 100),
        Product(2, "Банан",  8.0, 150),
        Product(3, "Молоко", 32.0, 50),
        Product(4, "Хліб",   25.0, 80),
        Product(5, "Сир",   120.0, 30),
        Product(6, "Масло",  85.0, 40),
        Product(7, "Яйця",   60.0, 200),
        Product(8, "Кефір",  28.0, 60),
    ]:
        products.add(p)

    customers = CustomerRepository()
    for c in [
        Customer(1, "Іван Петренко",    "ivan@mail.com",  CustomerType.REGULAR),
        Customer(2, "Марія Коваль",     "maria@mail.com", CustomerType.VIP),
        Customer(3, "Олег Сидоренко",   "oleg@mail.com",  CustomerType.REGULAR),
        Customer(4, "Тетяна Мороз",     "tanya@mail.com", CustomerType.REGULAR),
        Customer(5, "Василь Гриценко",  "vasyl@mail.com", CustomerType.VIP),
    ]:
        customers.add(c)

    suppliers = SupplierRepository()
    suppliers._next_id = 4
    for s in [
        Supplier(1, "АгроПостач",       "050-111-22-33"),
        Supplier(2, "МолокоОпт",        "067-444-55-66"),
        Supplier(3, "ХлібзаводПостач",  "093-777-88-99"),
    ]:
        suppliers.add(s)

    promos = PromoRepository()
    for pr in [
        PromoCode("SAVE10",  0.10, 200),
        PromoCode("VIP20",   0.20, 500),
        PromoCode("WELCOME", 0.05,   0),
        PromoCode("SUMMER",  0.15, 300, active=False),
    ]:
        promos.add(pr)

    return products, customers, suppliers, promos


if __name__ == "__main__":
    product_repo, customer_repo, supplier_repo, promo_repo = build_default_store()
    order_repo = OrderRepository()

    order_svc    = OrderService(product_repo, customer_repo, order_repo, promo_repo)
    promo_svc    = PromoService(promo_repo)
    supplier_svc = SupplierService(supplier_repo, product_repo)
    rating_svc   = RatingService(customer_repo, order_repo)

    print(" Звичайні замовлення ")
    o1 = order_svc.place_order(1, [{"product_id": 1, "quantity": 5}, {"product_id": 3, "quantity": 2}])
    print(f"Замовлення #{o1.order_id}: {o1.total} грн")

    o2 = order_svc.place_order(2, [{"product_id": 5, "quantity": 3}, {"product_id": 4, "quantity": 10}])
    print(f"Замовлення #{o2.order_id}: {o2.total} грн")

    o3 = order_svc.place_order(3, [{"product_id": 7, "quantity": 10}, {"product_id": 2, "quantity": 5}])
    print(f"Замовлення #{o3.order_id}: {o3.total} грн")

    print("\n Замовлення з промокодами ")
    o4 = order_svc.place_order(4, [{"product_id": 6, "quantity": 2}, {"product_id": 8, "quantity": 3}], "SAVE10")
    print(f"Замовлення #{o4.order_id}: {o4.total} грн (промокод: {o4.promo_code})")

    o5 = order_svc.place_order(5, [{"product_id": 5, "quantity": 2}, {"product_id": 1, "quantity": 20}], "VIP20")
    print(f"Замовлення #{o5.order_id}: {o5.total} грн (промокод: {o5.promo_code})")

    print("\n Промокоди ")
    promo_svc.add("AUTUMN", 0.12, 400)
    promo_svc.deactivate("WELCOME")
    for pr in promo_svc.list_all():
        status = "активний" if pr.active else "неактивний"
        print(f"  {pr.code} — {pr.discount_rate*100}% від {pr.min_total} грн ({status})")

    print("\nСкасування замовлення")
    order_svc.cancel_order(o1.order_id)

    print("\n Постачальники та поповнення складу")
    supplier_svc.add_supplier("ФермаСвіжа", "066-000-11-22")
    supplier_svc.restock(3, 100, 2)
    supplier_svc.restock(5, 50, 1)
    supplier_svc.restock_low_items(1, 30)

    print("\n Рейтинг клієнтів")
    for i, r in enumerate(rating_svc.all_ratings_sorted(), 1):
        print(f"{i}. {r['full_name']} — {r['total_spent']} грн ({r['rating']})")

    print(f"\nЗагальний дохід: {order_svc.get_revenue()} грн")
