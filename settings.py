import json
import os
import math
import time

# ==БД пользователей==
DATA_FILE = "users.json"


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=3, ensure_ascii=False)


users = load_users()


def init_user(user_id):
    if str(user_id) not in users:
        users[str(user_id)] = {
            "balance": 0,
            "hives": 0,
            "bees": 0,
            "cells": 0,
            "honey": 0,
            "referrals": [],
            "referrer": None,
            "craft_end": 0,
            "pending_honey": 0,
            "last_feed": 0,
        }
        save_users(users)


def get_user(user_id):
    return users.get(str(user_id))


# защита от отрицательных значений
def fix_user_values(user):
    for key in [
        "honey",
        "cells",
        "balance",
        "bees",
        "hives",
        "pending_honey",
        "craft_end",
        "last_feed",
    ]:
        if key in user and user[key] < 0:
            user[key] = 0


# ==referals==
def referral(message):
    text = message.text.split()

    user_id = str(message.chat.id)
    user = users[user_id]
    if len(text) < 2:
        return

    arg = text[1]
    if not arg.startswith("ref"):
        return

    ref_id = arg[3:]
    if ref_id == user_id:
        return

    if user["referrer"] is not None:
        return

    user["referrer"] = ref_id
    users[ref_id]["referrals"].append(user_id)
    users[ref_id]["balance"] += 1
    fix_user_values(user)
    save_users(users)


# ==bee_price==
def bee_price(bees):
    if bees == 0:
        return 0

    base = 30
    scale = 0.3
    price = base * math.log(bees * scale + 1)
    return int(price)


# ==hive_price==
def hive_price(hives):
    if hives == 0:
        return 0

    d = 80
    base_price = 80 + (hives - 1) * d
    return base_price


# ==buys==
def bee_buy(user_id):
    user = users[str(user_id)]
    price = bee_price(user["bees"])
    max_bees = user["hives"] * 8

    if user["balance"] < price:
        return False, "money"

    if max_bees <= user["bees"]:
        return False, "capacity"

    user["balance"] -= price
    user["bees"] += 1
    fix_user_values(user)
    save_users(users)
    return True, price


def hive_buy(user_id):
    user = users[str(user_id)]
    price = hive_price(user["hives"])

    if user["balance"] < price:
        return False

    user["balance"] -= price
    user["hives"] += 1
    fix_user_values(user)
    save_users(users)
    return True


# ==honey_craft==
def is_crafting(user_id):
    user = users[str(user_id)]
    now = time.time()
    if user["craft_end"] > now:
        remaining = int(user["craft_end"] - now)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        return True, hours, minutes
    return False, 0, 0


def calc_craft(user_id, amount):
    user = users[str(user_id)]
    cells = amount * 5
    time_needed = amount * 3 * 60

    if amount > 100:
        return False, "too_big", 0, 0, 0

    if user["cells"] < cells:
        return False, "not_cells", 0, 0, 0

    hours = time_needed // 3600
    minutes = (time_needed % 3600) // 60
    return True, cells, hours, minutes, time_needed


def start_craft(user_id, amount, time_needed, cells):
    user = users[str(user_id)]

    if amount > 100:
        return False

    if user["cells"] < cells:
        return False

    user["cells"] -= cells
    user["craft_end"] = time.time() + time_needed
    user["pending_honey"] = amount

    fix_user_values(user)
    save_users(users)


def finish_craft(user_id):
    user = users[str(user_id)]
    now = time.time()

    if not isinstance(user["craft_end"], (int, float)):
        user["craft_end"] = 0
        save_users(users)
        return 0

    if user["craft_end"] != 0 and user["craft_end"] <= now:
        amount = user.get("pending_honey", 0)

        if amount > 0:
            user["honey"] += amount
            user["pending_honey"] = 0

        user["craft_end"] = 0
        fix_user_values(user)
        save_users(users)
        return amount

    return 0


# ==buy_honey==
def buy_honey(user_id, amount):
    user = users[str(user_id)]

    if amount > 100:
        return False, 0

    if user["honey"] < amount:
        return False, 0

    if amount <= 0:
        return False, 0

    money = amount * 0.5
    user["honey"] -= amount
    user["balance"] += money

    fix_user_values(user)
    save_users(users)
    return True, money


# ==начисление сот==
def bees_income():
    for user_id, user in users.items():
        bees = user.get("bees", 0)
        income = bees * 5
        user["cells"] += income
        fix_user_values(user)

    save_users(users)
    return True


# ==кормление==
def feed_bees(user_id):
    user = users[str(user_id)]
    user["last_feed"] = time.time()
    save_users(users)


def check_bees_flight():
    now = time.time()
    for user_id, user in users.items():
        last = user.get("last_feed", 0)
        if last != 0 and now - last > 86400:
            user["bees"] = 0
            save_users(users)
