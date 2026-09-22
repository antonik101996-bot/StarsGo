from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")
PRICE = 1.38

def menu():
    return ReplyKeyboardMarkup(
        [["⭐ Купить Stars"],
         ["👤 Профиль","📈 Курс Stars"],
         ["💬 Поддержка"]],
        resize_keyboard=True)

async def start(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("✨ Добро пожаловать в StarsGo!",reply_markup=menu())

async def profile(update,ctx):
    u=update.effective_user
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Купить Premium StarsGo",callback_data="premium")],
        [InlineKeyboardButton("◀️ Назад",callback_data="back")]
    ])
    await update.message.reply_text(
        f"👤 Профиль\n\nИмя: {u.first_name}\nUsername: @{u.username or 'нет'}\nID: {u.id}\nPremium Telegram: {'Да' if u.is_premium else 'Нет'}\n\n💎 Premium StarsGo\nСкидка 25% на все Stars\nСтоимость: 999 ₽",
        reply_markup=kb)

async def rate(update,ctx):
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад",callback_data="back")]])
    await update.message.reply_text("📈 Курс Stars\n\n100 ⭐ = 138 ₽\n\nКурс периодически меняется.",reply_markup=kb)

async def support(update,ctx):
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад",callback_data="back")]])
    await update.message.reply_text("💬 Поддержка\n\n@Lakizyx",reply_markup=kb)

async def buy(update,ctx):
    kb=InlineKeyboardMarkup([
        [InlineKeyboardButton("100 ⭐",callback_data="p100"),InlineKeyboardButton("300 ⭐",callback_data="p300")],
        [InlineKeyboardButton("500 ⭐",callback_data="p500")],
        [InlineKeyboardButton("✏️ Ввести своё количество",callback_data="custom")],
        [InlineKeyboardButton("◀️ Назад",callback_data="back")]
    ])
    await update.message.reply_text("⭐ Выберите пакет Stars:",reply_markup=kb)

async def text(update,ctx):
    t=update.message.text
    if t=="⭐ Купить Stars": return await buy(update,ctx)
    if t=="👤 Профиль": return await profile(update,ctx)
    if t=="📈 Курс Stars": return await rate(update,ctx)
    if t=="💬 Поддержка": return await support(update,ctx)
    if ctx.user_data.get("state")=="amount":
        if not t.isdigit():
            return await update.message.reply_text("Введите число.")
        s=int(t); ctx.user_data["stars"]=s
        p=round(s*PRICE)
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 СПБ",callback_data="spb"),InlineKeyboardButton("💎 Криптовалюта",callback_data="crypto")],
            [InlineKeyboardButton("◀️ Назад",callback_data="back")]
        ])
        await update.message.reply_text(f"🛒 Подтверждение\n\nКоличество: {s} ⭐\nСтоимость: {p} ₽",reply_markup=kb)
        ctx.user_data["state"]=None

async def cb(update,ctx):
    q=update.callback_query
    await q.answer()
    d=q.data

    if d=="back":
        ctx.user_data.clear()
        await q.edit_message_text("◀️ Возврат в главное меню.\nИспользуйте кнопки снизу.")
        return

    if d=="custom":
        ctx.user_data["state"]="amount"
        await q.edit_message_text("✏️ Введите количество Stars:")
        return

    if d.startswith("p"):
        s=int(d[1:]); ctx.user_data["stars"]=s
        p=round(s*PRICE)
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 СПБ",callback_data="spb"),InlineKeyboardButton("💎 Криптовалюта",callback_data="crypto")],
            [InlineKeyboardButton("◀️ Назад",callback_data="back")]
        ])
        await q.edit_message_text(f"🛒 Подтверждение\n\nКоличество: {s} ⭐\nСтоимость: {p} ₽",reply_markup=kb)
        return

    if d=="premium":
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 СПБ",callback_data="premium_spb"),InlineKeyboardButton("💎 Криптовалюта",callback_data="premium_crypto")],
            [InlineKeyboardButton("◀️ Назад",callback_data="back")]
        ])
        await q.edit_message_text(
            "💎 Premium StarsGo\n\nСтоимость: 999 ₽\n\n🎁 Что входит:\n• Скидка 25% на покупку Stars\n• Приоритетная поддержка\n\nВыберите способ оплаты:",
            reply_markup=kb)
        return

    if d=="premium_spb":
        await q.edit_message_text("💳 Оплата Premium\n\nСумма: 999 ₽\n\nПосле оплаты отправьте чек @Lakizyx")
        return

    if d=="premium_crypto":
        await q.edit_message_text("💎 Оплата Premium криптовалютой\n\nСтоимость: 999 ₽\n\nПоддерживаются:\n• USDT (TON)\n• TON\n\nРеквизиты выдаёт @Lakizyx")
        return

    if d=="spb":
        s=ctx.user_data.get("stars",0); p=round(s*PRICE)
        await q.edit_message_text(f"💳 Оплата по СБП\n\nКоличество: {s} ⭐\nК оплате: {p} ₽\n\nПосле оплаты отправьте чек @Lakizyx")
        return

    if d=="crypto":
        s=ctx.user_data.get("stars",0); p=round(s*PRICE)
        await q.edit_message_text(f"💎 Оплата криптовалютой\n\nКоличество: {s} ⭐\nК оплате: {p} ₽\n\nUSDT (TON) / TON\n\nРеквизиты выдаёт @Lakizyx")

# StarsGo - only modified fragments
# Add these changes into your current main.py

PRICE = 1.38
PREMIUM_USERS = {"Lakizyx"}  # Premium accounts

def calc_price(stars, username):
    total = round(stars * PRICE)
    if username in PREMIUM_USERS:
        total = round(total * 0.75)
    return total

# In profile():
# Premium StarsGo: АКТИВЕН if username == Lakizyx

# Replace every price calculation:
# price = round(stars * PRICE)
# with:
# price = calc_price(stars, target_username)

# Premium purchase button stays for other users,
# but for Lakizyx show:
# "💎 Premium StarsGo — Активен (скидка 25%)"

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text))
app.add_handler(CallbackQueryHandler(cb))
app.run_polling()
