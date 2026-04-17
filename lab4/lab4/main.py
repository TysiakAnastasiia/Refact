
from src import (
    Dish, Menu, Customer, Order,
    OrderDatabase, KitchenNotifier,
    RegularOrderFactory, BulkOrderFactory, OrderFactoryProvider,
)


def main():
    
    print(" СИСТЕМА УПРАВЛІННЯ РЕСТОРАНОМ")
    

    print("\n Формуємо меню...")
    menu = Menu()
    menu.add_dish(Dish("Борщ", 90.0, "soup"))
    menu.add_dish(Dish("Вареники з картоплею", 110.0, "main"))
    menu.add_dish(Dish("Піца Маргарита", 160.0, "pizza"))
    menu.add_dish(Dish("Кола 0.5л", 40.0, "drink"))
    print(f"   Страв у меню: {len(menu)}")

    customer1 = Customer("Олена Коваленко", "+380671234567")
    customer2 = Customer("ТОВ Смачна їжа", "+380441234567")

    db = OrderDatabase()
    notifier = KitchenNotifier()

    print(f"\n Замовлення від '{customer1.name}'...")
    factory = OrderFactoryProvider.get_factory("regular")
    dishes = menu.get_all_dishes()[:2]
    order1 = factory.create_order(customer1, dishes)
    order1.attach(notifier)
    db.save_order(order1)
    order1.confirm()
    print(f"   Сума: {order1.total_price():.2f} грн")

    print(f"\n Масове замовлення від '{customer2.name}'...")
    bulk_factory = OrderFactoryProvider.get_factory("bulk")
    bulk_dishes = [Dish(f"Комплекс {i}", 120.0) for i in range(1, 8)]
    order2 = bulk_factory.create_order(customer2, bulk_dishes)
    order2.attach(notifier)
    db.save_order(order2)
    order2.confirm()
    print(f"   Сума: {order2.total_price():.2f} грн")

    print(f"\n Підсумок:")
    print(f"   Замовлень у БД:       {len(db)}")
    print(f"   Сповіщень на кухні:   {notifier.notification_count}")
    print(f"   Singleton DB : {OrderDatabase() is db}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
