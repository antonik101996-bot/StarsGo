import os
import telebot
from telebot import types

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

PRICES = {
    100: 138,
    200: 276,
    300: 414,
    400: 552,
    500: 690,
    1000: 1380
}

def menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("⭐ Купить Stars")
    kb.row("👤 Профиль", "💬 Поддержка")
    kb.row("📈 Курс Stars")
    return kb

@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "✨ Добро пожаловать в StarsGo!",
        reply_markup=menu()
    )

@bot.message_handler(func=lambda m: m.text == "👤 Профиль")
def profile(msg):
    bot.send_message(msg.chat.id, f"👤 Ваш Telegram ID: {msg.from_user.id}")

@bot.message_handler(func=lambda m: m.text == "💬 Поддержка")
def support(msg):
    bot.send_message(msg.chat.id, "💬 Поддержка: @Lakizyx")

@bot.message_handler(func=lambda m: m.text == "📈 Курс Stars")
def rate(msg):
    bot.send_message(msg.chat.id, "📈 Актуальный курс:\\n100 ⭐ = 138 ₽")

@bot.message_handler(func=lambda m: m.text == "⭐ Купить Stars")
def buy(msg):
    kb = types.InlineKeyboardMarkup(row_width=2)
    for s in [100,200,300,400,500,1000]:
        kb.add(types.InlineKeyboardButton(f"{s} ⭐", callback_data=f"buy_{s}"))
    bot.send_message(msg.chat.id, "⭐ Выберите пакет:", reply_markup=kb)

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def confirm(call):
    stars = int(call.data.split("_")[1])
    price = PRICES[stars]
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("✅ Подтвердить покупку", callback_data=f"ok_{stars}"))
    kb.add(types.InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    bot.edit_message_text(
        f"🛒 Вы покупаете {stars} ⭐ за {price} ₽.\\n\\nНажмите подтвердить.",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda c: c.data.startswith("ok_"))
def done(call):
    stars = int(call.data.split("_")[1])
    price = PRICES[stars]
    bot.edit_message_text(
        f"✅ Заявка создана!\\n\\nПакет: {stars} ⭐\\nСумма: {price} ₽\\n\\nДля оплаты напишите @Lakizyx",
        call.message.chat.id,
        call.message.message_id
    )

@bot.callback_query_handler(func=lambda c: c.data == "cancel")
def cancel(call):
    bot.edit_message_text("❌ Покупка отменена.", call.message.chat.id, call.message.message_id)

bot.infinity_polling()
