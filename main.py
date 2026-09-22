from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")
PRICE_PER_STAR = 1.38
PREMIUM_USERS = {"Lakizyx"}

def is_premium(username):
    return (username or "") in PREMIUM_USERS

def calc_price(stars, username):
    price = round(stars * PRICE_PER_STAR)
    return round(price * 0.75) if is_premium(username) else price

MAIN_MENU = ReplyKeyboardMarkup(
    [["⭐ Купить Stars"],
     ["👤 Профиль", "📈 Курс Stars"],
     ["💬 Поддержка"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "✨ Добро пожаловать в StarsGo!\n\nБыстрая покупка Telegram Stars.",
        reply_markup=MAIN_MENU
    )

async def show_profile(update, context):
    user = update.effective_user
    premium_text = "🔥 У ВАС УЖЕ ЕСТЬ PREMIUM ПОДПИСКА" if is_premium(user.username) else "Premium не активен"
    text = (
        f"👤 Профиль\n\n"
        f"Имя: {user.first_name}\n"
        f"Username: @{user.username or 'нет'}\n"
        f"Telegram ID: {user.id}\n"
        f"Premium Telegram: {'Да' if user.is_premium else 'Нет'}\n\n"
        f"{premium_text}"
    )
    if is_premium(user.username):
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_profile")]])
    else:
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Купить Premium StarsGo", callback_data="premium")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_profile")]
        ])
    await update.message.reply_text(text, reply_markup=kb)

async def buy_menu(update, context):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("100 ⭐", callback_data="buy_100"),
         InlineKeyboardButton("300 ⭐", callback_data="buy_300")],
        [InlineKeyboardButton("500 ⭐", callback_data="buy_500")],
        [InlineKeyboardButton("✏️ Ввести своё количество", callback_data="custom_amount")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_buy")]
    ])
    await update.message.reply_text("⭐ Выберите пакет Stars:", reply_markup=kb)

async def support(update, context):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_support")]])
    await update.message.reply_text("💬 Поддержка\n\n@Lakizyx", reply_markup=kb)

async def rate(update, context):
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="back_rate")]])
    await update.message.reply_text(
        "📈 Курс Stars\n\n100 ⭐ = 138 ₽\n\nКурс периодически меняется.",
        reply_markup=kb
    )

async def messages(update, context):
    txt = update.message.text
    if txt == "⭐ Купить Stars":
        return await buy_menu(update, context)
    if txt == "👤 Профиль":
        return await show_profile(update, context)
    if txt == "💬 Поддержка":
        return await support(update, context)
    if txt == "📈 Курс Stars":
        return await rate(update, context)
    if context.user_data.get("state") == "amount":
        if not txt.isdigit():
            return await update.message.reply_text("Введите только число.")
        stars = int(txt)
        context.user_data["stars"] = stars
        context.user_data["state"] = None
        return await payment_choice(update, context)

async def payment_choice(update, context):
    stars = context.user_data["stars"]
    username = update.effective_user.username
    price = calc_price(stars, username)
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 СПБ", callback_data="pay_spb"),
         InlineKeyboardButton("💎 Криптовалюта", callback_data="pay_crypto")],
        [InlineKeyboardButton("◀️ Назад", callback_data="back_payment")]
    ])
    await update.message.reply_text(
        f"🛒 Подтверждение покупки\n\nКоличество: {stars} ⭐\nСтоимость: {price} ₽",
        reply_markup=kb
    )

async def callbacks(update, context):
    q = update.callback_query
    await q.answer()
    d = q.data
    user = q.from_user

    if d == "back_buy":
        return await q.edit_message_text("⭐ Вернулись к выбору Stars.")
    if d == "back_profile":
        return await q.edit_message_text("👤 Вернулись к профилю.")
    if d == "back_support":
        return await q.edit_message_text("💬 Вернулись в поддержку.")
    if d == "back_rate":
        return await q.edit_message_text("📈 Вернулись к курсу.")
    if d == "back_payment":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("100 ⭐", callback_data="buy_100"),
             InlineKeyboardButton("300 ⭐", callback_data="buy_300")],
            [InlineKeyboardButton("500 ⭐", callback_data="buy_500")],
            [InlineKeyboardButton("✏️ Ввести своё количество", callback_data="custom_amount")]
        ])
        return await q.edit_message_text("⭐ Выберите пакет Stars:", reply_markup=kb)

    if d.startswith("buy_"):
        stars = int(d.split("_")[1])
        context.user_data["stars"] = stars
        price = calc_price(stars, user.username)
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 СПБ", callback_data="pay_spb"),
             InlineKeyboardButton("💎 Криптовалюта", callback_data="pay_crypto")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_payment")]
        ])
        return await q.edit_message_text(
            f"🛒 Подтверждение покупки\n\nКоличество: {stars} ⭐\nСтоимость: {price} ₽",
            reply_markup=kb
        )

    if d == "custom_amount":
        context.user_data["state"] = "amount"
        return await q.edit_message_text("✏️ Введите нужное количество Stars:")

    if d == "premium":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 СПБ", callback_data="premium_spb"),
             InlineKeyboardButton("💎 Криптовалюта", callback_data="premium_crypto")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_profile")]
        ])
        return await q.edit_message_text(
            "💎 Premium StarsGo\n\n999 ₽\n\nДаёт скидку 25% на все покупки Stars.",
            reply_markup=kb
        )

    if d == "premium_spb":
        return await q.edit_message_text("💳 Оплата Premium\n\nСумма: 999 ₽")
    if d == "premium_crypto":
        return await q.edit_message_text("💎 Оплата Premium\n\nUSDT (TON) / TON\n999 ₽")
    if d == "pay_spb":
        price = calc_price(context.user_data["stars"], user.username)
        return await q.edit_message_text(f"💳 СПБ\n\nК оплате: {price} ₽")
    if d == "pay_crypto":
        price = calc_price(context.user_data["stars"], user.username)
        return await q.edit_message_text(f"💎 Криптовалюта\n\nК оплате: {price} ₽\nUSDT (TON) / TON")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))
app.add_handler(CallbackQueryHandler(callbacks))
app.run_polling()
