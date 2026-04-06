import datetime

d = []
p = []
u = []
promo = []
suppliers = []

def init():
    global d, p, u, promo, suppliers
    p = [
        {"id": 1, "n": "Яблуко", "pr": 15.0, "st": 100},
        {"id": 2, "n": "Банан", "pr": 8.0, "st": 150},
        {"id": 3, "n": "Молоко", "pr": 32.0, "st": 50},
        {"id": 4, "n": "Хліб", "pr": 25.0, "st": 80},
        {"id": 5, "n": "Сир", "pr": 120.0, "st": 30},
        {"id": 6, "n": "Масло", "pr": 85.0, "st": 40},
        {"id": 7, "n": "Яйця", "pr": 60.0, "st": 200},
        {"id": 8, "n": "Кефір", "pr": 28.0, "st": 60},
    ]
    u = [
        {"id": 1, "nm": "Іван Петренко", "em": "ivan@mail.com", "tp": "regular"},
        {"id": 2, "nm": "Марія Коваль", "em": "maria@mail.com", "tp": "vip"},
        {"id": 3, "nm": "Олег Сидоренко", "em": "oleg@mail.com", "tp": "regular"},
        {"id": 4, "nm": "Тетяна Мороз", "em": "tanya@mail.com", "tp": "regular"},
        {"id": 5, "nm": "Василь Гриценко", "em": "vasyl@mail.com", "tp": "vip"},
    ]
    promo = [
        {"code": "SAVE10", "disc": 0.10, "min_total": 200, "active": True},
        {"code": "VIP20", "disc": 0.20, "min_total": 500, "active": True},
        {"code": "WELCOME", "disc": 0.05, "min_total": 0, "active": True},
        {"code": "SUMMER", "disc": 0.15, "min_total": 300, "active": False},
    ]
    suppliers = [
        {"id": 1, "nm": "АгроПостач", "phone": "050-111-22-33"},
        {"id": 2, "nm": "МолокоОпт", "phone": "067-444-55-66"},
        {"id": 3, "nm": "ХлібзаводПостач", "phone": "093-777-88-99"},
    ]


def process_order(uid, items):
    global d, p, u

    cu = None
    for x in u:
        if x["id"] == uid:
            cu = x
            break

    if cu is None:
        print("Error: user not found")
        return None

    t = 0
    oi = []
    for it in items:
        cp = None
        for pp in p:
            if pp["id"] == it["pid"]:
                cp = pp
                break
        if cp is None:
            print("Error: product not found: " + str(it["pid"]))
            return None
        if cp["st"] < it["qty"]:
            print("Error: not enough stock for " + cp["n"])
            return None

        item_total = cp["pr"] * it["qty"]
        t = t + item_total
        oi.append({"pid": cp["id"], "pname": cp["n"], "qty": it["qty"], "price": cp["pr"], "total": item_total})

    disc = 0
    if cu["tp"] == "vip":
        if t > 2000:
            disc = 0.20
        else:
            if t > 1000:
                disc = 0.15
            else:
                if t > 500:
                    disc = 0.10
                else:
                    disc = 0.05
    else:
        if t > 2000:
            disc = 0.10
        else:
            if t > 1000:
                disc = 0.07
            else:
                if t > 500:
                    disc = 0.05
                else:
                    disc = 0

    disc_amt = t * disc
    final = t - disc_amt

    for it in items:
        for pp in p:
            if pp["id"] == it["pid"]:
                pp["st"] = pp["st"] - it["qty"]

    ord_id = len(d) + 1
    ord_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_order = {
        "id": ord_id,
        "uid": uid,
        "uname": cu["nm"],
        "items": oi,
        "subtotal": t,
        "discount_pct": disc * 100,
        "discount_amt": disc_amt,
        "total": final,
        "date": ord_date,
        "status": "new",
        "promo_used": None
    }
    d.append(new_order)

    print("Замовлення #" + str(ord_id) + " створено")
    print("Клієнт: " + cu["nm"])
    print("Сума: " + str(t))
    print("Знижка: " + str(disc * 100) + "% = " + str(disc_amt))
    print("До сплати: " + str(final))

    return new_order


def process_order_with_promo(uid, items, promo_code):
    global d, p, u, promo

    cu = None
    for x in u:
        if x["id"] == uid:
            cu = x
            break

    if cu is None:
        print("Error: user not found")
        return None

    t = 0
    oi = []
    for it in items:
        cp = None
        for pp in p:
            if pp["id"] == it["pid"]:
                cp = pp
                break
        if cp is None:
            print("Error: product not found: " + str(it["pid"]))
            return None
        if cp["st"] < it["qty"]:
            print("Error: not enough stock for " + cp["n"])
            return None

        item_total = cp["pr"] * it["qty"]
        t = t + item_total
        oi.append({"pid": cp["id"], "pname": cp["n"], "qty": it["qty"], "price": cp["pr"], "total": item_total})

    found_promo = None
    for pr in promo:
        if pr["code"] == promo_code:
            found_promo = pr
            break

    disc = 0
    promo_disc = 0
    promo_amt = 0

    if cu["tp"] == "vip":
        if t > 2000:
            disc = 0.20
        else:
            if t > 1000:
                disc = 0.15
            else:
                if t > 500:
                    disc = 0.10
                else:
                    disc = 0.05
    else:
        if t > 2000:
            disc = 0.10
        else:
            if t > 1000:
                disc = 0.07
            else:
                if t > 500:
                    disc = 0.05
                else:
                    disc = 0

    disc_amt = t * disc
    after_disc = t - disc_amt

    if found_promo is None:
        print("Промокод не знайдено: " + promo_code)
    else:
        if found_promo["active"] == False:
            print("Промокод " + promo_code + " не активний")
        else:
            if after_disc < found_promo["min_total"]:
                print("Сума замовлення замала для промокоду " + promo_code)
            else:
                promo_disc = found_promo["disc"]
                promo_amt = after_disc * promo_disc
                print("Промокод " + promo_code + " застосовано: -" + str(promo_amt))

    final = after_disc - promo_amt

    for it in items:
        for pp in p:
            if pp["id"] == it["pid"]:
                pp["st"] = pp["st"] - it["qty"]

    ord_id = len(d) + 1
    ord_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_order = {
        "id": ord_id,
        "uid": uid,
        "uname": cu["nm"],
        "items": oi,
        "subtotal": t,
        "discount_pct": disc * 100,
        "discount_amt": disc_amt,
        "promo_used": promo_code if promo_disc > 0 else None,
        "promo_disc_pct": promo_disc * 100,
        "promo_disc_amt": promo_amt,
        "total": final,
        "date": ord_date,
        "status": "new"
    }
    d.append(new_order)

    print("Замовлення #" + str(ord_id) + " створено")
    print("Клієнт: " + cu["nm"])
    print("Сума: " + str(t))
    print("Знижка клієнта: " + str(disc * 100) + "% = " + str(disc_amt))
    print("Промокод знижка: " + str(promo_disc * 100) + "% = " + str(promo_amt))
    print("До сплати: " + str(final))

    return new_order


def add_promo(code, disc, min_total):
    global promo
    for pr in promo:
        if pr["code"] == code:
            print("Промокод " + code + " вже існує")
            return False
    if disc <= 0 or disc >= 1:
        print("Знижка має бути між 0 і 1")
        return False
    if min_total < 0:
        print("Мінімальна сума не може бути від'ємною")
        return False
    promo.append({"code": code, "disc": disc, "min_total": min_total, "active": True})
    print("Промокод " + code + " додано")
    return True


def deactivate_promo(code):
    global promo
    for pr in promo:
        if pr["code"] == code:
            if pr["active"] == False:
                print("Промокод " + code + " вже неактивний")
                return False
            pr["active"] = False
            print("Промокод " + code + " деактивовано")
            return True
    print("Промокод не знайдено")
    return False


def show_promos():
    global promo
    print("Список промокодів:")
    for pr in promo:
        st = "активний" if pr["active"] else "неактивний"
        print("  " + pr["code"] + " — " + str(pr["disc"] * 100) + "% від " + str(pr["min_total"]) + " грн (" + st + ")")


def get_client_rating(uid):
    global d, u
    cu = None
    for x in u:
        if x["id"] == uid:
            cu = x
            break
    if cu is None:
        print("Користувача не знайдено")
        return None

    total_spent = 0
    order_cnt = 0
    for x in d:
        if x["uid"] == uid and x["status"] != "cancelled":
            total_spent = total_spent + x["total"]
            order_cnt = order_cnt + 1

    if total_spent >= 5000:
        rating = "Platinum"
    else:
        if total_spent >= 2000:
            rating = "Gold"
        else:
            if total_spent >= 500:
                rating = "Silver"
            else:
                rating = "Bronze"

    print("Клієнт: " + cu["nm"])
    print("Замовлень: " + str(order_cnt) + ", витрачено: " + str(total_spent) + " грн")
    print("Рейтинг: " + rating)

    return {"uid": uid, "name": cu["nm"], "total_spent": total_spent, "order_cnt": order_cnt, "rating": rating}


def show_all_ratings():
    global u
    print("Рейтинг клієнтів:")
    results = []
    for x in u:
        r = get_client_rating(x["id"])
        if r is not None:
            results.append(r)
            print("")

    results_sorted = sorted(results, key=lambda x: x["total_spent"], reverse=True)
    print("Топ клієнтів за сумою покупок:")
    pos = 1
    for r in results_sorted:
        print(str(pos) + ". " + r["name"] + " — " + str(r["total_spent"]) + " грн (" + r["rating"] + ")")
        pos = pos + 1


def restock_product(pid, qty, supplier_id):
    global p, suppliers
    cp = None
    for x in p:
        if x["id"] == pid:
            cp = x
            break
    if cp is None:
        print("Товар не знайдено")
        return False

    cs = None
    for x in suppliers:
        if x["id"] == supplier_id:
            cs = x
            break
    if cs is None:
        print("Постачальника не знайдено")
        return False

    if qty <= 0:
        print("Кількість має бути більше 0")
        return False

    old_st = cp["st"]
    cp["st"] = cp["st"] + qty
    print("Поповнення складу: " + cp["n"] + " від " + cs["nm"])
    print("Було: " + str(old_st) + ", додано: " + str(qty) + ", стало: " + str(cp["st"]))
    return True


def add_supplier(nm, phone):
    global suppliers
    new_id = len(suppliers) + 1
    suppliers.append({"id": new_id, "nm": nm, "phone": phone})
    print("Постачальника " + nm + " додано з ID=" + str(new_id))
    return new_id


def show_suppliers():
    global suppliers
    print("Список постачальників:")
    for s in suppliers:
        print("  #" + str(s["id"]) + " " + s["nm"] + " тел: " + s["phone"])


def restock_low_items(supplier_id, qty):
    global p
    low = []
    for x in p:
        if x["st"] < 10:
            low.append(x)
    if len(low) == 0:
        print("Всі товари в достатній кількості")
        return
    print("Поповнення товарів з низьким залишком:")
    for x in low:
        restock_product(x["id"], qty, supplier_id)


def get_order(oid):
    global d
    res = None
    for x in d:
        if x["id"] == oid:
            res = x
            break
    return res


def get_user(uid):
    global u
    res = None
    for x in u:
        if x["id"] == uid:
            res = x
            break
    return res


def get_product(pid):
    global p
    res = None
    for x in p:
        if x["id"] == pid:
            res = x
            break
    return res


def show_user_orders(uid):
    global d
    print("Замовлення користувача " + str(uid))
    cnt = 0
    sm = 0
    for x in d:
        if x["uid"] == uid:
            cnt = cnt + 1
            sm = sm + x["total"]
            print("Замовлення #" + str(x["id"]) + " від " + x["date"] + " на суму " + str(x["total"]))
    print("Всього замовлень: " + str(cnt) + ", загальна сума: " + str(sm))


def send_cancellation_email(uname, oid):
    print("Email надіслано клієнту " + uname + " про скасування замовлення #" + str(oid))


def cancel_order(oid):
    global d, p
    for x in d:
        if x["id"] == oid:
            if x["status"] == "new":
                x["status"] = "cancelled"
                for it in x["items"]:
                    for pp in p:
                        if pp["id"] == it["pid"]:
                            pp["st"] = pp["st"] + it["qty"]
                send_cancellation_email(x["uname"], oid)
                print("Замовлення скасовано, кошти повернуто")
                return True
            else:
                print("Не можна скасувати замовлення зі статусом: " + x["status"])
                return False
    print("Замовлення не знайдено")
    return False


def calc_discount_for_report(tp, total):
    disc = 0
    if tp == "vip":
        if total > 2000:
            disc = 0.20
        else:
            if total > 1000:
                disc = 0.15
            else:
                if total > 500:
                    disc = 0.10
                else:
                    disc = 0.05
    else:
        if total > 2000:
            disc = 0.10
        else:
            if total > 1000:
                disc = 0.07
            else:
                if total > 500:
                    disc = 0.05
                else:
                    disc = 0
    return disc


def generate_report():
    global d, u
    print("ЗВІТ ПО ЗАМОВЛЕННЯХ")
    total_revenue = 0
    for x in d:
        promo_info = ""
        if x.get("promo_used") is not None:
            promo_info = " [промокод: " + x["promo_used"] + "]"
        print("Замовлення #" + str(x["id"]) + " | " + x["uname"] + " | " + str(x["total"]) + " грн | " + x["status"] + promo_info)
        if x["status"] != "cancelled":
            total_revenue = total_revenue + x["total"]
    print("Загальний дохід: " + str(total_revenue) + " грн")


def generate_product_report():
    global p, d
    print("ЗВІТ ПО ТОВАРАХ")
    for pp in p:
        sold = 0
        revenue = 0
        for x in d:
            if x["status"] != "cancelled":
                for it in x["items"]:
                    if it["pid"] == pp["id"]:
                        sold = sold + it["qty"]
                        revenue = revenue + it["total"]
        print(pp["n"] + " | залишок: " + str(pp["st"]) + " | продано: " + str(sold) + " шт | дохід: " + str(revenue) + " грн")


def update_product_price(pid, np):
    global p
    for x in p:
        if x["id"] == pid:
            if np < 0:
                print("Ціна не може бути від'ємною")
                return False
            x["pr"] = np
            return True
    return False


def get_stock_status():
    global p
    low = []
    for x in p:
        if x["st"] < 10:
            low.append(x)
    return low


if __name__ == "__main__":
    init()

    print(" Звичайні замовлення ")
    order1 = process_order(1, [{"pid": 1, "qty": 5}, {"pid": 3, "qty": 2}])
    order2 = process_order(2, [{"pid": 5, "qty": 3}, {"pid": 4, "qty": 10}])
    order3 = process_order(3, [{"pid": 7, "qty": 10}, {"pid": 2, "qty": 5}])

    print("")
    print(" Замовлення з промокодами ")
    order4 = process_order_with_promo(4, [{"pid": 6, "qty": 2}, {"pid": 8, "qty": 3}], "SAVE10")
    order5 = process_order_with_promo(5, [{"pid": 5, "qty": 2}, {"pid": 1, "qty": 20}], "VIP20")
    order6 = process_order_with_promo(1, [{"pid": 4, "qty": 3}], "SUMMER")

    print("")
    print(" Промокоди ")
    show_promos()
    add_promo("AUTUMN", 0.12, 400)
    deactivate_promo("WELCOME")
    show_promos()

    print("")
    print(" Скасування замовлення ")
    cancel_order(1)

    print("")
    print(" Постачальники та поповнення складу ")
    show_suppliers()
    add_supplier("ФермаСвіжа", "066-000-11-22")
    restock_product(3, 100, 2)
    restock_product(5, 50, 1)
    restock_low_items(1, 30)

    print("")
    print(" Рейтинг клієнтів ")
    show_all_ratings()

    print("")
    print(" Звіти ")
    generate_report()
    print("")
    generate_product_report()
    print("")
    show_user_orders(5)