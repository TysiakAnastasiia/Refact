"""
Юніт-тести для системи обліку замовлень магазину.
Запуск: python -m pytest tests/test_cases.py -v
або:    python tests/test_cases.py
"""
import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from refactored_code import (
    Product, Customer, Supplier, PromoCode, OrderItem, Order,
    CustomerType, OrderStatus, RatingLevel,
    ProductRepository, CustomerRepository, SupplierRepository,
    PromoRepository, OrderRepository,
    OrderService, PromoService, SupplierService, RatingService,
    calculate_discount_rate, calculate_rating,
    build_default_store, DiscountThreshold, RatingThreshold,
)


#  Хелпер 
def make_services():
    prod_repo, cust_repo, supp_repo, promo_repo = build_default_store()
    order_repo = OrderRepository()
    order_svc    = OrderService(prod_repo, cust_repo, order_repo, promo_repo)
    promo_svc    = PromoService(promo_repo)
    supplier_svc = SupplierService(supp_repo, prod_repo)
    rating_svc   = RatingService(cust_repo, order_repo)
    return order_svc, promo_svc, supplier_svc, rating_svc, prod_repo, cust_repo, order_repo, promo_repo, supp_repo


# Product — тести 1–7
class TestProduct(unittest.TestCase):

    def setUp(self):
        self.p = Product(1, "Яблуко", 15.0, 100)

    def test_01_has_stock_true(self):
        self.assertTrue(self.p.has_stock(100))

    def test_02_has_stock_false(self):
        self.assertFalse(self.p.has_stock(101))

    def test_03_deduct_reduces_stock(self):
        self.p.deduct(10)
        self.assertEqual(self.p.stock, 90)

    def test_04_restock_increases_stock(self):
        self.p.restock(50)
        self.assertEqual(self.p.stock, 150)

    def test_05_restock_zero_raises(self):
        with self.assertRaises(ValueError):
            self.p.restock(0)

    def test_06_update_price_valid(self):
        self.p.update_price(20.0)
        self.assertEqual(self.p.price, 20.0)

    def test_07_update_price_negative_raises(self):
        with self.assertRaises(ValueError):
            self.p.update_price(-1.0)

    def test_08_is_low_stock_false(self):
        self.assertFalse(self.p.is_low_stock())

    def test_09_is_low_stock_true(self):
        p = Product(2, "Банан", 8.0, 5)
        self.assertTrue(p.is_low_stock())


# OrderItem — тести 10–12
class TestOrderItem(unittest.TestCase):

    def test_10_line_total_basic(self):
        item = OrderItem(1, "Яблуко", 4, 15.0)
        self.assertAlmostEqual(item.line_total, 60.0)

    def test_11_line_total_zero_qty(self):
        item = OrderItem(1, "Яблуко", 0, 15.0)
        self.assertEqual(item.line_total, 0.0)

    def test_12_line_total_fractional(self):
        item = OrderItem(2, "Сир", 3, 120.0)
        self.assertAlmostEqual(item.line_total, 360.0)


# PromoCode — тести 13–16
class TestPromoCode(unittest.TestCase):

    def setUp(self):
        self.pr = PromoCode("SAVE10", 0.10, 200)

    def test_13_applicable_above_min(self):
        self.assertTrue(self.pr.is_applicable(300))

    def test_14_not_applicable_below_min(self):
        self.assertFalse(self.pr.is_applicable(100))

    def test_15_not_applicable_when_inactive(self):
        self.pr.deactivate()
        self.assertFalse(self.pr.is_applicable(500))

    def test_16_deactivate_sets_flag(self):
        self.pr.deactivate()
        self.assertFalse(self.pr.active)


# Discount calculation — тести 17–24
class TestDiscountCalculation(unittest.TestCase):

    def test_17_vip_below_low(self):
        self.assertAlmostEqual(calculate_discount_rate(CustomerType.VIP, 300), 0.05)

    def test_18_vip_above_low(self):
        self.assertAlmostEqual(calculate_discount_rate(CustomerType.VIP, 750), 0.10)

    def test_19_vip_above_medium(self):
        self.assertAlmostEqual(calculate_discount_rate(CustomerType.VIP, 1500), 0.15)

    def test_20_vip_above_high(self):
        self.assertAlmostEqual(calculate_discount_rate(CustomerType.VIP, 2500), 0.20)

    def test_21_regular_below_low(self):
        self.assertAlmostEqual(calculate_discount_rate(CustomerType.REGULAR, 200), 0.00)

    def test_22_regular_above_low(self):
        self.assertAlmostEqual(calculate_discount_rate(CustomerType.REGULAR, 600), 0.05)

    def test_23_regular_above_medium(self):
        self.assertAlmostEqual(calculate_discount_rate(CustomerType.REGULAR, 1200), 0.07)

    def test_24_regular_above_high(self):
        self.assertAlmostEqual(calculate_discount_rate(CustomerType.REGULAR, 3000), 0.10)


# Rating calculation — тести 25–28
class TestRatingCalculation(unittest.TestCase):

    def test_25_bronze(self):
        self.assertEqual(calculate_rating(100), RatingLevel.BRONZE)

    def test_26_silver(self):
        self.assertEqual(calculate_rating(1000), RatingLevel.SILVER)

    def test_27_gold(self):
        self.assertEqual(calculate_rating(3000), RatingLevel.GOLD)

    def test_28_platinum(self):
        self.assertEqual(calculate_rating(6000), RatingLevel.PLATINUM)


# OrderService — тести 29–42
class TestOrderService(unittest.TestCase):

    def setUp(self):
        self.order_svc, self.promo_svc, self.supplier_svc, self.rating_svc, \
        self.prod_repo, self.cust_repo, self.order_repo, self.promo_repo, self.supp_repo \
            = make_services()

    def test_29_place_order_creates_order(self):
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 2}])
        self.assertIsNotNone(o)
        self.assertEqual(o.order_id, 1)

    def test_30_place_order_deducts_stock(self):
        before = self.prod_repo.find(1).stock
        self.order_svc.place_order(1, [{"product_id": 1, "quantity": 5}])
        self.assertEqual(self.prod_repo.find(1).stock, before - 5)

    def test_31_place_order_correct_subtotal(self):
        # Яблуко 15 × 4 = 60
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 4}])
        self.assertAlmostEqual(o.subtotal, 60.0)

    def test_32_place_order_no_discount_small_regular(self):
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 4}])
        self.assertAlmostEqual(o.discount_amount, 0.0)

    def test_33_place_order_vip_gets_discount(self):
        # Марія VIP, Сир 120 × 5 = 600 > 500 → 10%
        o = self.order_svc.place_order(2, [{"product_id": 5, "quantity": 5}])
        self.assertGreater(o.discount_amount, 0)

    def test_34_place_order_unknown_customer_raises(self):
        with self.assertRaises(ValueError):
            self.order_svc.place_order(999, [{"product_id": 1, "quantity": 1}])

    def test_35_place_order_unknown_product_raises(self):
        with self.assertRaises(ValueError):
            self.order_svc.place_order(1, [{"product_id": 999, "quantity": 1}])

    def test_36_place_order_insufficient_stock_raises(self):
        with self.assertRaises(ValueError):
            self.order_svc.place_order(1, [{"product_id": 1, "quantity": 9999}])

    def test_37_place_order_with_valid_promo(self):
        # SAVE10: 10% від суми >= 200
        # Яблуко 15 × 20 = 300, regular - знижки немає, promo = 10% від 300 = 30
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 20}], "SAVE10")
        self.assertEqual(o.promo_code, "SAVE10")
        self.assertAlmostEqual(o.promo_discount_amount, 30.0)

    def test_38_place_order_inactive_promo_not_applied(self):
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 20}], "SUMMER")
        self.assertIsNone(o.promo_code)

    def test_39_place_order_promo_below_min_not_applied(self):
        # SAVE10 вимагає >= 200, Яблуко 15 × 5 = 75
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 5}], "SAVE10")
        self.assertIsNone(o.promo_code)

    def test_40_cancel_order_changes_status(self):
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 1}])
        self.order_svc.cancel_order(o.order_id)
        self.assertEqual(self.order_repo.find(o.order_id).status, OrderStatus.CANCELLED)

    def test_41_cancel_order_restores_stock(self):
        before = self.prod_repo.find(1).stock
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 5}])
        self.order_svc.cancel_order(o.order_id)
        self.assertEqual(self.prod_repo.find(1).stock, before)

    def test_42_cancel_nonexistent_raises(self):
        with self.assertRaises(ValueError):
            self.order_svc.cancel_order(999)

    def test_43_cancel_already_cancelled_raises(self):
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 1}])
        self.order_svc.cancel_order(o.order_id)
        with self.assertRaises(ValueError):
            self.order_svc.cancel_order(o.order_id)

    def test_44_get_orders_returns_only_own(self):
        self.order_svc.place_order(1, [{"product_id": 1, "quantity": 1}])
        self.order_svc.place_order(2, [{"product_id": 2, "quantity": 1}])
        orders = self.order_svc.get_orders(1)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].customer.customer_id, 1)

    def test_45_revenue_excludes_cancelled(self):
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 10}])
        rev_before = self.order_svc.get_revenue()
        self.order_svc.cancel_order(o.order_id)
        self.assertAlmostEqual(self.order_svc.get_revenue(), rev_before - o.total)

    def test_46_customer_summary_correct(self):
        self.order_svc.place_order(1, [{"product_id": 1, "quantity": 10}])  # 150 грн
        summary = self.order_svc.get_customer_summary(1)
        self.assertEqual(summary["order_count"], 1)
        self.assertAlmostEqual(summary["total_spent"], 150.0)


# PromoService — тести 47–50
class TestPromoService(unittest.TestCase):

    def setUp(self):
        self.promo_repo = PromoRepository()
        self.svc = PromoService(self.promo_repo)

    def test_47_add_promo_success(self):
        pr = self.svc.add("TEST", 0.10, 100)
        self.assertEqual(pr.code, "TEST")

    def test_48_add_duplicate_raises(self):
        self.svc.add("TEST", 0.10, 100)
        with self.assertRaises(ValueError):
            self.svc.add("TEST", 0.05, 50)

    def test_49_add_invalid_rate_raises(self):
        with self.assertRaises(ValueError):
            self.svc.add("BAD", 1.5, 100)

    def test_50_deactivate_success(self):
        self.svc.add("ACT", 0.10, 0)
        self.svc.deactivate("ACT")
        self.assertFalse(self.promo_repo.find("ACT").active)

    def test_51_deactivate_already_inactive_raises(self):
        self.svc.add("ACT", 0.10, 0)
        self.svc.deactivate("ACT")
        with self.assertRaises(ValueError):
            self.svc.deactivate("ACT")

    def test_52_deactivate_missing_raises(self):
        with self.assertRaises(ValueError):
            self.svc.deactivate("NONE")


# SupplierService — тести 53–56
class TestSupplierService(unittest.TestCase):

    def setUp(self):
        _, _, self.supp_repo, _ = build_default_store()
        prod_repo, _, _, _ = build_default_store()
        self.prod_repo = prod_repo
        self.svc = SupplierService(self.supp_repo, self.prod_repo)

    def test_53_add_supplier(self):
        s = self.svc.add_supplier("Новий", "000-000-00-00")
        self.assertEqual(s.name, "Новий")

    def test_54_restock_increases_stock(self):
        before = self.prod_repo.find(1).stock
        self.svc.restock(1, 50, 1)
        self.assertEqual(self.prod_repo.find(1).stock, before + 50)

    def test_55_restock_unknown_product_raises(self):
        with self.assertRaises(ValueError):
            self.svc.restock(999, 10, 1)

    def test_56_restock_unknown_supplier_raises(self):
        with self.assertRaises(ValueError):
            self.svc.restock(1, 10, 999)

    def test_57_restock_low_items_restocks_all_low(self):
        # Зменшуємо запас до low stock
        self.prod_repo.find(1).stock = 3
        self.prod_repo.find(2).stock = 5
        low = self.svc.restock_low_items(1, 20)
        self.assertEqual(len(low), 2)
        self.assertEqual(self.prod_repo.find(1).stock, 23)


# RatingService — тести 58–60
class TestRatingService(unittest.TestCase):

    def setUp(self):
        prod_repo, cust_repo, _, promo_repo = build_default_store()
        self.order_repo  = OrderRepository()
        self.order_svc   = OrderService(prod_repo, cust_repo, self.order_repo, promo_repo)
        self.rating_svc  = RatingService(cust_repo, self.order_repo)

    def test_58_rating_bronze_no_orders(self):
        r = self.rating_svc.get_rating(1)
        self.assertEqual(r["rating"], "Bronze")

    def test_59_rating_updates_after_orders(self):
        # Яблуко 15 × 40 = 600 → Silver
        self.order_svc.place_order(1, [{"product_id": 1, "quantity": 40}])
        r = self.rating_svc.get_rating(1)
        self.assertEqual(r["rating"], "Silver")

    def test_60_cancelled_orders_not_counted(self):
        o = self.order_svc.place_order(1, [{"product_id": 1, "quantity": 40}])
        self.order_svc.cancel_order(o.order_id)
        r = self.rating_svc.get_rating(1)
        self.assertEqual(r["rating"], "Bronze")

    def test_61_all_ratings_sorted_descending(self):
        self.order_svc.place_order(1, [{"product_id": 1, "quantity": 40}])
        self.order_svc.place_order(2, [{"product_id": 5, "quantity": 5}])
        ratings = self.rating_svc.all_ratings_sorted()
        totals = [r["total_spent"] for r in ratings]
        self.assertEqual(totals, sorted(totals, reverse=True))

    def test_62_unknown_customer_raises(self):
        with self.assertRaises(ValueError):
            self.rating_svc.get_rating(999)


# Repository — тести 63–65
class TestRepositories(unittest.TestCase):

    def test_63_product_repo_find_existing(self):
        repo = ProductRepository()
        repo.add(Product(1, "Test", 10.0, 5))
        self.assertIsNotNone(repo.find(1))

    def test_64_product_repo_find_missing_returns_none(self):
        repo = ProductRepository()
        self.assertIsNone(repo.find(999))

    def test_65_order_repo_next_id_increments(self):
        repo = OrderRepository()
        self.assertEqual(repo.next_id(), 1)
        self.assertEqual(repo.next_id(), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
