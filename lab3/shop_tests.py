# -*- coding: utf-8 -*-
"""
Модульні тести для системи "Інтернет-магазин"
Лабораторна робота 3
"""

import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from shop import Product, CartItem, Order, User, Admin, Catalog


class TestProduct(unittest.TestCase):

    def setUp(self):
        self.product = Product(1, "Ноутбук", 25000.0, 10)

    # Тест 1: базові атрибути товару
    def test_product_attributes(self):
        self.assertEqual(self.product.get_id(), 1)
        self.assertEqual(self.product.get_name(), "Ноутбук")
        self.assertEqual(self.product.get_price(), 25000.0)
        self.assertEqual(self.product.get_stock(), 10)

    # Тест 2: товар доступний коли є на складі
    def test_product_is_available(self):
        self.assertTrue(self.product.is_available())

    # Тест 3: товар недоступний коли склад 0
    def test_product_not_available_when_no_stock(self):
        empty = Product(2, "Мишка", 500.0, 0)
        self.assertFalse(empty.is_available())

    # Тест 4: зміна ціни
    def test_set_price(self):
        self.product.set_price(22000.0)
        self.assertEqual(self.product.get_price(), 22000.0)

    # Тест 5: від'ємна ціна — виняток
    def test_set_negative_price_raises(self):
        with self.assertRaises(ValueError):
            self.product.set_price(-100)

    # Тест 6: оновлення складу
    def test_update_stock(self):
        self.product.update_stock(-3)
        self.assertEqual(self.product.get_stock(), 7)

    # Тест 7: списання більше ніж є — виняток
    def test_update_stock_below_zero_raises(self):
        with self.assertRaises(ValueError):
            self.product.update_stock(-100)


class TestOrder(unittest.TestCase):

    def setUp(self):
        self.user = User(1, "anna", "anna@test.com", "pass123")
        self.user.login("pass123")
        self.product1 = Product(1, "Ноутбук", 25000.0, 5)
        self.product2 = Product(2, "Мишка", 500.0, 10)
        self.order = self.user.place_order()

    # Тест 8: новий замовлення має статус pending
    def test_new_order_status_is_pending(self):
        self.assertEqual(self.order.get_status(), Order.STATUS_PENDING)

    # Тест 9: додавання товару і підрахунок суми
    def test_add_product_and_calculate_total(self):
        self.order.add_product(self.product1, 2)
        self.order.add_product(self.product2, 3)
        expected = 25000.0 * 2 + 500.0 * 3
        self.assertAlmostEqual(self.order.calculate_total(), expected)

    # Тест 10: видалення товару із замовлення
    def test_remove_product(self):
        self.order.add_product(self.product1)
        self.order.add_product(self.product2)
        self.order.remove_product(1)
        ids = [i.get_product().get_id() for i in self.order.get_items()]
        self.assertNotIn(1, ids)
        self.assertIn(2, ids)

    # Тест 11: підтвердження замовлення
    def test_confirm_order(self):
        self.order.add_product(self.product1)
        self.order.confirm()
        self.assertEqual(self.order.get_status(), Order.STATUS_CONFIRMED)

    # Тест 12: не можна підтвердити порожнє замовлення
    def test_confirm_empty_order_raises(self):
        with self.assertRaises(ValueError):
            self.order.confirm()

    # Тест 13: скасування замовлення
    def test_cancel_order(self):
        self.order.add_product(self.product1)
        self.order.cancel()
        self.assertEqual(self.order.get_status(), Order.STATUS_CANCELLED)

    # Тест 14: додавання недоступного товару — виняток
    def test_add_unavailable_product_raises(self):
        out_of_stock = Product(3, "Планшет", 8000.0, 0)
        with self.assertRaises(ValueError):
            self.order.add_product(out_of_stock)


class TestUser(unittest.TestCase):

    def setUp(self):
        self.user = User(1, "anna", "anna@test.com", "pass123")

    # Тест 15: реєстрація повертає повідомлення
    def test_register_returns_message(self):
        msg = self.user.register()
        self.assertIn("anna", msg)

    # Тест 16: успішний вхід
    def test_login_success(self):
        result = self.user.login("pass123")
        self.assertTrue(result)
        self.assertTrue(self.user.is_logged_in())

    # Тест 17: невірний пароль
    def test_login_wrong_password(self):
        result = self.user.login("wrongpass")
        self.assertFalse(result)
        self.assertFalse(self.user.is_logged_in())

    # Тест 18: вихід із системи
    def test_logout(self):
        self.user.login("pass123")
        self.user.logout()
        self.assertFalse(self.user.is_logged_in())

    # Тест 19: створення замовлення без входу — виняток
    def test_place_order_without_login_raises(self):
        with self.assertRaises(PermissionError):
            self.user.place_order()

    # Тест 20: замовлення прив'язане до користувача
    def test_order_linked_to_user(self):
        self.user.login("pass123")
        order = self.user.place_order()
        self.assertEqual(order.get_user(), self.user)
        self.assertIn(order, self.user.view_orders())


class TestCatalog(unittest.TestCase):

    def setUp(self):
        self.catalog = Catalog()
        self.catalog.add_product(Product(1, "Ноутбук Apple", 45000.0, 3))
        self.catalog.add_product(Product(2, "Ноутбук Lenovo", 25000.0, 5))
        self.catalog.add_product(Product(3, "Мишка", 500.0, 20))

    # Тест 21: пошук за назвою
    def test_search_by_name(self):
        results = self.catalog.search("ноутбук")
        self.assertEqual(len(results), 2)

    # Тест 22: пошук без результатів
    def test_search_no_results(self):
        results = self.catalog.search("телефон")
        self.assertEqual(len(results), 0)

    # Тест 23: отримання товару за id
    def test_get_by_id(self):
        p = self.catalog.get_by_id(3)
        self.assertEqual(p.get_name(), "Мишка")

    # Тест 24: видалення товару з каталогу (адмін)
    def test_admin_remove_product(self):
        admin = Admin(99, "admin", "admin@shop.com", "admin123")
        admin.login("admin123")
        admin.remove_product(self.catalog, 1)
        self.assertIsNone(self.catalog.get_by_id(1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
