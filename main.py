from telegram import (
    Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import os

TOKEN = os.getenv("BOT_TOKEN")

RATES = {100:138,200:276,300:414,400:552,500:690,1000:1380}

MENU = ReplyKeyboardMarkup(
    [["⭐ Купить Stars"],
     ["👤 Профиль","💬 Поддержка"],
     ["📈 Курс Stars"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "друг"
    await update.message.reply_text(
        f"✨ Добро пожаловать в StarsGo, {name}!\n\n"
        "Покупайте Telegram Stars быстро и безопасно.\n"
        "Выберите нужный раздел ниже.",
        reply_markup=MENU
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    txt = (
        "👤 Ваш профиль StarsGo\n\n"
        f"• Имя: {u.first_name or '-'}\n"
        f"• Фамилия: {u.last_name or '-'}\n"
        f"• Username: @{u.username if u.username else 'не указан'}\n"
        f"• Telegram ID: {u.id}\n"
        f"• Язык: {u.language_code or '-'}\n"
        f"• Premium: {'Да' if u.is_premium else 'Нет'}"
    )
    await update.message.reply_text(txt)

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬 Поддержка StarsGo\n\nПо любым вопросам: @Lakizyx"
    )

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📈 Курс Telegram Stars\n\n"
        "100 ⭐ = 138 ₽\n\n"
        "ℹ️ Курс периодически меняется в зависимости от рынка TON."
    )

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Для себя", callback_data="self"),
         InlineKeyboardButton("Для друга", callback_data="friend")]
    ])
    await update.message.reply_text(
        "✨ Для кого приобретаем Telegram Stars?",
        reply_markup=kb
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text

    if context.user_data.get("wait_username"):
        context.user_data["target"] = txt.replace("@","")
        context.user_data["wait_username"] = False
        return await choose_amount(update)

    if context.user_data.get("wait_custom"):
        try:
            s = int(txt)
            if s <= 0:
                raise ValueError
            context.user_data["stars"] = s
            return await confirm(update, s)
        except:
            return await update.message.reply_text("Введите число, например 750.")

    if txt == "⭐ Купить Stars":
        await buy(update, context)
    elif txt == "👤 Профиль":
        await profile(update, context)
    elif txt == "💬 Поддержка":
        await support(update, context)
    elif txt == "📈 Курс Stars":
        await rate(update, context)

async def choose_amount(update_or_query):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("100", callback_data="amt_100"),
         InlineKeyboardButton("200", callback_data="amt_200")],
        [InlineKeyboardButton("300", callback_data="amt_300"),
         InlineKeyboardButton("400", callback_data="amt_400")],
        [InlineKeyboardButton("500", callback_data="amt_500"),
         InlineKeyboardButton("1000", callback_data="amt_1000")],
        [InlineKeyboardButton("✏️ Ввести своё количество", callback_data="custom")]
    ])
    if isinstance(update_or_query, Update):
        await update_or_query.message.reply_text("Выберите количество ⭐:", reply_markup=kb)
    else:
        await update_or_query.edit_message_text("Выберите количество ⭐:", reply_markup=kb)

async def confirm(update: Update, stars: int):
    price = round(stars * 1.38)
    user = context_user(update)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Подтвердить покупку", callback_data=f"ok_{stars}")]
    ])
    await update.message.reply_text(
        f"🛒 Подтверждение покупки\n\n"
        f"Получатель: @{user}\n"
        f"Количество: {stars} ⭐\n"
        f"Стоимость: {price} ₽\n\n"
        "Нажмите кнопку ниже для подтверждения.",
        reply_markup=kb
    )

def context_user(update):
    return update._effective_user.username or "username"

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "self":
        context.user_data["target"] = q.from_user.username or "без username"
        return await choose_amount(q)

    if data == "friend":
        context.user_data["wait_username"] = True
        return await q.edit_message_text("Введите @username получателя одним сообщением.")

    if data == "custom":
        context.user_data["wait_custom"] = True
        return await q.edit_message_text("Введите нужное количество звёзд (например 750).")

    if data.startswith("amt_"):
        s = int(data.split("_")[1])
        context.user_data["stars"] = s
        price = RATES.get(s, round(s*1.38))
        target = context.user_data.get("target","-")
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Подтвердить покупку", callback_data=f"ok_{s}")]])
        return await q.edit_message_text(
            f"🛒 Подтверждение покупки\n\n"
            f"Получатель: @{target}\n"
            f"Количество: {s} ⭐\n"
            f"Стоимость: {price} ₽",
            reply_markup=kb
        )

    if data.startswith("ok_"):
        s = int(data.split("_")[1])
        price = RATES.get(s, round(s*1.38))
        target = context.user_data.get("target","-")
        return await q.edit_message_text(
            "✅ Заказ успешно создан!\n\n"
            f"Получатель: @{target}\n"
            f"Пакет: {s} ⭐\n"
            f"К оплате: {price} ₽\n\n"
            "Следующим шагом здесь появится платёжная ссылка Platega."
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))
    app.add_handler(CallbackQueryHandler(callbacks))
    print("StarsGo запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
