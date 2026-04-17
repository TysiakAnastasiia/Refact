
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.dish import Dish
from src.models.menu import Menu
from src.models.customer import Customer
from src.models.order import Order, OrderStatus
from src.patterns import (
    OrderDatabase,
    KitchenNotifier,
    RegularOrderFactory,
    BulkOrderFactory,
    OrderFactoryProvider,
)
class TestDish(unittest.TestCase):

    def test_dish_creation(self):
        dish = Dish("Піца", 150.0)
        self.assertEqual(dish.name, "Піца")
        self.assertEqual(dish.price, 150.0)

    def test_dish_with_category(self):
        dish = Dish("Борщ", 80.0, category="soup")
        self.assertEqual(dish.category, "soup")

    def test_dish_empty_name_raises(self):
        with self.assertRaises(ValueError):
            Dish("", 100)

    def test_dish_negative_price_raises(self):
        with self.assertRaises(ValueError):
            Dish("Суп", -10)

    def test_dish_equality(self):
        d1 = Dish("Піца", 150.0)
        d2 = Dish("Піца", 150.0)
        self.assertEqual(d1, d2)

    def test_dish_inequality(self):
        d1 = Dish("Піца", 150.0)
        d2 = Dish("Суп", 80.0)
        self.assertNotEqual(d1, d2)

    def test_dish_zero_price_allowed(self):
        dish = Dish("Вода", 0)
        self.assertEqual(dish.price, 0)


class TestMenu(unittest.TestCase):

    def setUp(self):
        self.menu = Menu()
        self.pizza = Dish("Піца", 150.0, "pizza")
        self.soup = Dish("Борщ", 80.0, "soup")

    def test_add_dish_to_menu(self):
        self.menu.add_dish(self.pizza)
        self.assertTrue(self.menu.contains_dish(self.pizza))

    def test_menu_starts_empty(self):
        self.assertTrue(self.menu.is_empty())

    def test_menu_length(self):
        self.menu.add_dish(self.pizza)
        self.menu.add_dish(self.soup)
        self.assertEqual(len(self.menu), 2)

    def test_duplicate_dish_raises(self):
        self.menu.add_dish(self.pizza)
        with self.assertRaises(ValueError):
            self.menu.add_dish(self.pizza)

    def test_remove_dish(self):
        self.menu.add_dish(self.pizza)
        self.menu.remove_dish(self.pizza)
        self.assertFalse(self.menu.contains_dish(self.pizza))

    def test_remove_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.menu.remove_dish(self.pizza)

    def test_add_invalid_type_raises(self):
        with self.assertRaises(TypeError):
            self.menu.add_dish("not a dish")

    def test_get_by_category(self):
        self.menu.add_dish(self.pizza)
        self.menu.add_dish(self.soup)
        pizzas = self.menu.get_by_category("pizza")
        self.assertEqual(len(pizzas), 1)
        self.assertIn(self.pizza, pizzas)

    def test_get_all_dishes_returns_copy(self):
        self.menu.add_dish(self.pizza)
        dishes = self.menu.get_all_dishes()
        dishes.clear()
        self.assertFalse(self.menu.is_empty())


class TestCustomer(unittest.TestCase):

    def test_customer_creation(self):
        c = Customer("Іван Петренко", "+380501234567")
        self.assertEqual(c.name, "Іван Петренко")
        self.assertEqual(c.phone, "+380501234567")

    def test_customer_empty_name_raises(self):
        with self.assertRaises(ValueError):
            Customer("")

    def test_customer_equality(self):
        c1 = Customer("Марія", "123")
        c2 = Customer("Марія", "123")
        self.assertEqual(c1, c2)

    def test_customer_strips_whitespace(self):
        c = Customer("  Олег  ")
        self.assertEqual(c.name, "Олег")


class TestOrder(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("Аліна", "+380")
        self.dish1 = Dish("Піца", 150.0)
        self.dish2 = Dish("Кола", 40.0)

    def test_order_creation(self):
        order = Order(self.customer)
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.status, OrderStatus.PENDING)

    def test_order_add_dish(self):
        order = Order(self.customer)
        order.add_dish(self.dish1)
        self.assertIn(self.dish1, order.dishes)

    def test_order_total_price(self):
        order = Order(self.customer)
        order.add_dish(self.dish1)
        order.add_dish(self.dish2)
        self.assertAlmostEqual(order.total_price(), 190.0)

    def test_order_invalid_customer_raises(self):
        with self.assertRaises(TypeError):
            Order("not a customer")

    def test_order_invalid_dish_raises(self):
        order = Order(self.customer)
        with self.assertRaises(TypeError):
            order.add_dish("not a dish")

    def test_order_confirm_changes_status(self):
        order = Order(self.customer)
        order.confirm()
        self.assertEqual(order.status, OrderStatus.CONFIRMED)

    def test_order_empty_dishes_total(self):
        order = Order(self.customer)
        self.assertEqual(order.total_price(), 0.0)



class TestSingletonOrderDatabase(unittest.TestCase):

    def setUp(self):
        OrderDatabase.reset()

    def test_singleton_same_instance(self):
        db1 = OrderDatabase()
        db2 = OrderDatabase()
        self.assertIs(db1, db2)

    def test_singleton_shared_state(self):
        db1 = OrderDatabase()
        db2 = OrderDatabase()
        customer = Customer("Тест")
        order = Order(customer)
        db1.save_order(order)
        self.assertEqual(len(db2.get_all_orders()), 1)

    def test_save_and_retrieve_order(self):
        db = OrderDatabase()
        customer = Customer("Олена")
        order = Order(customer)
        db.save_order(order)
        orders = db.get_all_orders()
        self.assertIn(order, orders)

    def test_get_by_customer(self):
        db = OrderDatabase()
        c1 = Customer("Богдан")
        c2 = Customer("Наталія")
        o1 = Order(c1)
        o2 = Order(c2)
        db.save_order(o1)
        db.save_order(o2)
        result = db.get_by_customer("Богдан")
        self.assertEqual(len(result), 1)

    def test_invalid_order_raises(self):
        db = OrderDatabase()
        with self.assertRaises(TypeError):
            db.save_order("not an order")

    def test_clear_database(self):
        db = OrderDatabase()
        db.save_order(Order(Customer("X")))
        db.clear()
        self.assertEqual(len(db), 0)


class TestObserverKitchenNotifier(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("Ярослав")
        self.dish = Dish("Піца Маргарита", 160.0)
        self.notifier = KitchenNotifier()

    def test_notifier_receives_update_on_confirm(self):
        order = Order(self.customer)
        order.add_dish(self.dish)
        order.attach(self.notifier)
        order.confirm()
        self.assertEqual(self.notifier.notification_count, 1)

    def test_notifier_not_called_before_confirm(self):
        order = Order(self.customer)
        order.attach(self.notifier)
        self.assertEqual(self.notifier.notification_count, 0)

    def test_multiple_observers(self):
        notifier2 = KitchenNotifier()
        order = Order(self.customer)
        order.add_dish(self.dish)
        order.attach(self.notifier)
        order.attach(notifier2)
        order.confirm()
        self.assertEqual(self.notifier.notification_count, 1)
        self.assertEqual(notifier2.notification_count, 1)

    def test_detach_observer(self):
        order = Order(self.customer)
        order.add_dish(self.dish)
        order.attach(self.notifier)
        order.detach(self.notifier)
        order.confirm()
        self.assertEqual(self.notifier.notification_count, 0)

    def test_notification_message_content(self):
        order = Order(self.customer)
        order.add_dish(self.dish)
        order.attach(self.notifier)
        order.confirm()
        msg = self.notifier.get_notifications()[0]
        self.assertIn("Ярослав", msg)
        self.assertIn("160", msg)


class TestFactoryPattern(unittest.TestCase):

    def setUp(self):
        self.customer = Customer("Корпоративний клієнт")
        self.dishes = [Dish(f"Страва {i}", 50.0) for i in range(6)]

    def test_regular_factory_creates_regular_order(self):
        factory = RegularOrderFactory()
        order = factory.create_order(self.customer, [self.dishes[0]])
        self.assertEqual(order.order_type, "regular")

    def test_bulk_factory_creates_bulk_order(self):
        factory = BulkOrderFactory()
        order = factory.create_order(self.customer, self.dishes)
        self.assertEqual(order.order_type, "bulk")

    def test_bulk_factory_requires_min_5_dishes(self):
        factory = BulkOrderFactory()
        with self.assertRaises(ValueError):
            factory.create_order(self.customer, self.dishes[:3])

    def test_factory_provider_regular(self):
        factory = OrderFactoryProvider.get_factory("regular")
        self.assertIsInstance(factory, RegularOrderFactory)

    def test_factory_provider_bulk(self):
        factory = OrderFactoryProvider.get_factory("bulk")
        self.assertIsInstance(factory, BulkOrderFactory)

    def test_factory_provider_unknown_raises(self):
        with self.assertRaises(ValueError):
            OrderFactoryProvider.get_factory("unknown_type")

    def test_factory_attaches_dishes_to_order(self):
        factory = RegularOrderFactory()
        order = factory.create_order(self.customer, [self.dishes[0], self.dishes[1]])
        self.assertEqual(len(order.dishes), 2)

    def test_factory_invalid_customer_raises(self):
        factory = RegularOrderFactory()
        with self.assertRaises(TypeError):
            factory.create_order("not a customer", [])



class TestIntegrationFlow(unittest.TestCase):

    def setUp(self):
        OrderDatabase.reset()
        self.db = OrderDatabase()
        self.notifier = KitchenNotifier()

    def test_full_order_flow(self):
        menu = Menu()
        menu.add_dish(Dish("Борщ", 90.0, "soup"))
        menu.add_dish(Dish("Вареники", 110.0, "main"))

        customer = Customer("Петро Сидоренко", "+380671234567")
        factory = RegularOrderFactory()
        order = factory.create_order(customer, menu.get_all_dishes())

        order.attach(self.notifier)
        self.db.save_order(order)
        order.confirm()

        self.assertEqual(len(self.db), 1)
        self.assertEqual(self.notifier.notification_count, 1)
        self.assertEqual(order.status, OrderStatus.CONFIRMED)
        self.assertAlmostEqual(order.total_price(), 200.0)

    def test_empty_menu_order(self):
        customer = Customer("Тест")
        factory = RegularOrderFactory()
        order = factory.create_order(customer, [])
        self.assertEqual(order.total_price(), 0.0)

    def test_bulk_order_full_flow(self):
        customer = Customer("ТОВ Ромашка")
        dishes = [Dish(f"Комплекс {i}", 100.0) for i in range(10)]
        factory = BulkOrderFactory()
        order = factory.create_order(customer, dishes)
        order.attach(self.notifier)
        self.db.save_order(order)
        order.confirm()
        self.assertEqual(order.order_type, "bulk")
        self.assertAlmostEqual(order.total_price(), 1000.0)
        self.assertEqual(self.notifier.notification_count, 1)


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
