import telebot
from telebot import types
import settings
import threading
import time

bot = telebot.TeleBot("7625863678:AAG8WGCmaoCLjw-LEWznLSBFdKW-S9BAJ6M")


# == Менюшка ==
markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
btn1 = types.KeyboardButton("магазин🛍️")
btn2 = types.KeyboardButton("фабрика меда🍯")
btn3 = types.KeyboardButton("правила📜")
btn4 = types.KeyboardButton("профиль🍀")
btn5 = types.KeyboardButton("банк💰")
btn6 = types.KeyboardButton("рефералка🔗")
btn7 = types.KeyboardButton("тех.поддержка👨‍💻")
btn8 = types.KeyboardButton("сообщество💬")

# магазин
btn1_1 = types.KeyboardButton("купить пчелу🐝")
btn1_2 = types.KeyboardButton("купить улей🏵️")
# фабрика меда
btn2_1 = types.KeyboardButton("сделать мед🍯✨")
btn2_2 = types.KeyboardButton("продать мед🍯💸️")
# банк
btn5_1 = types.KeyboardButton("пополнить баланс💵")
btn5_2 = types.KeyboardButton("вывести деньги💸")
# дополнительно
btn_nach = types.KeyboardButton("покормить пчел🌸")
btn_back = types.KeyboardButton("⬅️назад")
btn_buy = types.KeyboardButton("купить")
btn_craft = types.KeyboardButton("начать")

state = {}  # buy_state
craft_state = {}
sale_state = {}


# ==Старт==
@bot.message_handler(commands=["start"])
def main(message):
    settings.init_user(message.chat.id)
    settings.referral(message)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn1, btn2)
    markup.row(btn4, btn5)
    markup.row(btn3, btn6)
    markup.row(btn7, btn8)
    try:
        bot.send_message(
            message.chat.id,
            f"Привет, {message.from_user.first_name} \nДобро пожаловать в игру, где ты можешь заработать денег. Перейди в магазин и получи бесплатный первый улей с пчелой!",
            reply_markup=markup,
        )
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")


# ==Магазин==
@bot.message_handler(func=lambda msg: msg.text == "магазин🛍️")
def shoping(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn1_1, btn1_2)
    markup.row(btn_back)
    bot.send_message(
        message.chat.id,
        "🛍️Вы находитесь в меню магазина. \nИспользуйте кнопки.",
        reply_markup=markup,
    )


# покупка пчелы
@bot.message_handler(func=lambda msg: msg.text == "купить пчелу🐝")
def buy_bee(message):
    user = settings.get_user(message.chat.id)
    bee_price = settings.bee_price(user["bees"])
    state[message.chat.id] = "bee"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn_buy, btn_back)
    bot.send_message(
        message.chat.id,
        f"Пчела приносит 5 сот 🔶(0,50₽) \nЦена пчелы: {float(bee_price)}₽  \nВаш баланс: {float(user['balance'])}₽",
        reply_markup=markup,
    )


# покупка улея
@bot.message_handler(func=lambda msg: msg.text == "купить улей🏵️")
def buy_hive(message):
    user = settings.get_user(message.chat.id)
    hive_price = settings.hive_price(user["hives"])
    state[message.chat.id] = "hive"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn_buy, btn_back)
    bot.send_message(
        message.chat.id,
        f"Улей позволяет хранить 8 пчел \nЦена улея: {hive_price}₽ \nВаш баланс: {float(user['balance'])}₽",
        reply_markup=markup,
    )


# покупка
@bot.message_handler(func=lambda msg: msg.text == "купить")
def buy(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn_back)

    buy_state = state.get(message.chat.id)

    if buy_state == "bee":
        success, info = settings.bee_buy(message.chat.id)
        if success:
            user = settings.get_user(message.chat.id)
            bot.send_message(
                message.chat.id,
                f"✅Покупка совершена \nКоличество пчел: {user['bees']}  \nОстаток баланса: {float(user['balance'])}₽ ",
                reply_markup=markup,
            )
        else:
            if info == "money":
                bot.send_message(
                    message.chat.id,
                    "❌Покупка не совершена. \nНедостаточно средств",
                    reply_markup=markup,
                )
            elif info == "capacity":
                bot.send_message(
                    message.chat.id,
                    "❌Покупка не совершена. \nНедостаточно ульев",
                    reply_markup=markup,
                )

    elif buy_state == "hive":
        success = settings.hive_buy(message.chat.id)
        if success:
            user = settings.get_user(message.chat.id)
            bot.send_message(
                message.chat.id,
                f"✅Покупка совершена \nКоличество ульев: {user['hives']}  \nОстаток баланса: {float(user['balance'])}₽",
                reply_markup=markup,
            )
        else:
            bot.send_message(
                message.chat.id,
                "❌Покупка не совершена. \nНедостаточно средств ",
                reply_markup=markup,
            )

    else:
        bot.send_message(
            message.chat.id,
            "неизвестная команда",
            reply_markup=markup,
        )


# ==Фабрика==
@bot.message_handler(func=lambda msg: msg.text == "фабрика меда🍯")
def fabrik(message):
    user = settings.get_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn2_1, btn2_2)
    markup.row(btn_back)
    bot.send_message(
        message.chat.id,
        "🍯Вы находитесь на фабрике меда. \nЗдесь ваш мед превращается в деньги. \nИспользуйте кнопки."
        "\n\nПеределка позволяет обменять: \n5 сот 🔶 = 1 горшочек мёда 🍯. \n"
        f"\nКоличество сот: {user['cells']}"
        f"\nКоличество мёда: {user['honey']}",
        reply_markup=markup,
    )


# сделать мед
@bot.message_handler(func=lambda msg: msg.text == "сделать мед🍯✨")
def craft(message):
    user_id = message.chat.id
    user = settings.get_user(user_id)
    crafting, hours, minutes = settings.is_crafting(user_id)

    if crafting:
        bot.send_message(
            message.chat.id,
            f"⏳ Переработка уже идёт! \
            \nОставшееся время: {hours} часов {minutes} минут",
        )
        return

    craft_state[message.chat.id] = "waiting_amount"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn_back)

    bot.send_message(
        message.chat.id,
        f"Допустимое количество горшочков мёда: {user['cells'] // 5} \
        \nВведите количество горшочков для переработки: ",
        reply_markup=markup,
    )


@bot.message_handler(
    func=lambda msg: (
        msg.chat.id in craft_state and craft_state[msg.chat.id] == "waiting_amount"
    )
)
def craft_process(message):
    user_id = message.chat.id

    try:
        amount = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Введите число.")
        return
    if amount < 0:
        bot.send_message(message.chat.id, "Введите положительное число.")
        return

    success, cells, hours, minutes, time_needed = settings.calc_craft(user_id, amount)

    if amount > 100:
        bot.send_message(message.chat.id, "Слишком большое число.")
        return

    if not success:
        bot.send_message(user_id, "❌ Недостаточно сот!")
        return

    craft_state[user_id] = {
        "amount": amount,
        "cells": cells,
        "time_needed": time_needed,
    }

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn_craft, btn_back)

    bot.send_message(
        message.chat.id,
        f"\nКоличество мёда по итогу: {amount} 🍯"
        f"\nЗабираемое количество сот: {cells} 🔶"
        f"\nВремя на переработку: {hours} часа {minutes} мин",
        reply_markup=markup,
    )


@bot.message_handler(func=lambda msg: msg.text == "начать")
def process_go(message):
    user_id = message.chat.id

    if user_id not in craft_state:
        bot.send_message(user_id, "Ошибка: нет данных для переработки")
        return

    data = craft_state[user_id]

    settings.start_craft(user_id, data["amount"], data["time_needed"], data["cells"])
    del craft_state[user_id]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn_back)

    bot.send_message(message.chat.id, "✨Переработка запущена!", reply_markup=markup)


def craft_watcher():
    while True:
        for uid in list(settings.users.keys()):
            amount = settings.finish_craft(uid)
            if amount > 0:
                bot.send_message(uid, f"✨ Ваш мёд готов!\nПолучено: {amount} 🍯")
        time.sleep(5)


threading.Thread(target=craft_watcher, daemon=True).start()


# продать мёд
@bot.message_handler(func=lambda msg: msg.text == "продать мед🍯💸️")
def sale(message):
    user = settings.get_user(message.chat.id)
    sale_state[message.chat.id] = "waiting_amount"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn_back)

    bot.send_message(
        message.chat.id,
        "Продажа мёда: \n1 горшочек мёда 🍯 = 0,5₽. \n"
        f"\nКоличество мёда: {user['honey']}"
        "\nВведите количество для продажи: ",
        reply_markup=markup,
    )


@bot.message_handler(
    func=lambda msg: (
        msg.chat.id in sale_state and sale_state[msg.chat.id] == "waiting_amount"
    )
)
def sale_process(message):
    try:
        amount = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Введите число.")
        return
    if amount < 0:
        bot.send_message(message.chat.id, "Введите положительное число.")
        return

    success, money = settings.buy_honey(message.chat.id, amount)

    if not success:
        bot.send_message(message.chat.id, "❌Недостаточно мёда")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn_back)

    bot.send_message(
        message.chat.id,
        f"\n✅Мёд продан!\nПродано: {amount} 🍯\nПолучено: {money}₽",
        reply_markup=markup,
    )

    del sale_state[message.chat.id]


# ==Правила==
@bot.message_handler(func=lambda msg: msg.text == "правила📜")
def roots(message):
    bot.send_message(
        message.chat.id,
        "📜 Как играть в HoneyMoney?"
        "\n"
        "\n🎁 Старт:  "
        "\nПри регистрации вы получаете 1 бесплатный улей 🏵️ и 1 пчелу 🐝, чтобы сразу начать зарабатывать."
        "\n"
        "\n🐝 Пчёлы и доход:  "
        "\n• В одном улее живёт до 8 пчёл."
        "\n• Когда места заканчиваются — покупайте новый улей."
        "\n• 1 пчела приносит 5 сот 🔶 в день.  "
        "\n• 1 сота = 0,1 ₽.  "
        "\nБольше пчёл — выше ежедневный доход."
        "\n"
        "\n🍯 Переработка сот в мёд:  "
        "\n• 5 сот 🔶 → 1 горшочек мёда 🍯 = 0,5 ₽  "
        "\n• Переработка занимает время."
        "\n• Пока предыдущая переработка не завершена — новую запустить нельзя."
        "\nПодробнее — в разделе «сделать мёд🍯✨»."
        "\n"
        "\n💸 Продажа мёда:  "
        "\n• После переработки мёд можно продать."
        "\n• Деньги можно оставить на игровом балансе для развития пасеки"
        "\n• Или вывести на реальный счёт.",
    )


# ==Портфолио==
@bot.message_handler(func=lambda msg: msg.text == "профиль🍀")
def profile(message):
    user = settings.get_user(message.chat.id)
    bot.send_message(
        message.chat.id,
        f"📔Ваш профиль\
                     \n💰Баланс: {float(user['balance'])} ₽\
                     \n🏵️Ульи: {user['hives']} \
                     \n🐝Пчелы: {user['bees']}\
                     \n🔶Соты: {user['cells']}\
                     \n🍯Мед: {user['honey']}",
    )


# ==Банк==
@bot.message_handler(func=lambda msg: msg.text == "банк💰")
def bank(message):
    user = settings.get_user(message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn5_1, btn5_2)
    markup.row(btn_back)
    bot.send_message(
        message.chat.id, f"Ваш баланс: {float(user['balance'])} ₽", reply_markup=markup
    )


# пополнить баланс
# вывести деньги


# ==Рефералка==
@bot.message_handler(func=lambda msg: msg.text == "рефералка🔗")
def reff(message):
    user = settings.get_user(message.chat.id)
    user_id = message.chat.id
    ref_link = f"https://t.me/HoneyMoney0_0_bot?start=ref{user_id}"

    bot.send_message(
        message.chat.id,
        f"🔗Реферальная система \
        \nСписок приглашённых: {len(user['referrals'])} \
        \nНаграды за активных друзей: {float(len(user['referrals']))}₽ \
        \n\nВаша рефральная ссылка: \n{ref_link}",
        disable_web_page_preview=True,
    )


# ==Тех.поддержка==
@bot.message_handler(func=lambda msg: msg.text == "тех.поддержка👨‍💻")
def support(message):
    bot.send_message(message.chat.id, "Тех.поддержка: \n@ProstoKirka")


# ==Сообщество==
@bot.message_handler(func=lambda msg: msg.text == "сообщество💬")
def community(message):
    bot.send_message(
        message.chat.id, "Наше сообщество: \nhttps://t.me/honeymoney_community"
    )


# Назад
@bot.message_handler(func=lambda msg: msg.text == "⬅️назад")
def back(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn1, btn2)
    markup.row(btn4, btn5)
    markup.row(btn3, btn6)
    markup.row(btn7, btn8)
    bot.send_message(
        message.chat.id, "🏡Вы вернулись в главное меню", reply_markup=markup
    )


# ==ежедневная награда==
def daily_income_sender():
    while True:
        now = time.localtime()

        if now.tm_hour == 6 and now.tm_min == 0:
            settings.bees_income()

            for user_id, user in settings.users.items():
                bees = user.get("bees", 0)
                income = bees * 5
                try:
                    bot.send_message(user_id, f"🐝 Ваши пчёлы принесли: {income} сот")
                except:
                    pass

            time.sleep(60)

        time.sleep(1)


threading.Thread(target=daily_income_sender, daemon=True).start()


# покормить пчел
@bot.message_handler(func=lambda msg: msg.text == "покормить пчел🌸")
def feeding(message):
    settings.feed_bees(message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(btn1, btn2)
    markup.row(btn4, btn5)
    markup.row(btn3, btn6)
    markup.row(btn7, btn8)
    bot.send_message(message.chat.id, "Все пчелы покормлены🌸", reply_markup=markup)


def daily_feed_warning():
    while True:
        now = time.localtime()
        if now.tm_hour == 0 and now.tm_min == 0:
            for user_id in settings.users.keys():
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.row(types.KeyboardButton("покормить пчел🌸"))
                try:
                    bot.send_message(
                        int(user_id),
                        "⚠️ Покормите пчёл своих, иначе они улетят",
                        reply_markup=markup,
                    )
                except:
                    pass
            time.sleep(60)
        time.sleep(1)


threading.Thread(target=daily_feed_warning, daemon=True).start()


bot.polling(none_stop=True)
