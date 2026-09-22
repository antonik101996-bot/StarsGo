# StarsGo main.py (python-telegram-bot v20+)
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import os

TOKEN=os.getenv("BOT_TOKEN")
PRICE_PER_STAR=1.38

def menu():
    return ReplyKeyboardMarkup(
        [["⭐ Купить Stars"],["👤 Профиль","📈 Курс Stars"],["💬 Поддержка"]],
        resize_keyboard=True)

async def start(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("✨ Добро пожаловать в StarsGo!",reply_markup=menu())

async def profile(update:Update,ctx):
    ctx.user_data["state"]=None
    u=update.effective_user
    await update.message.reply_text(
f"""👤 Профиль

Имя: {u.first_name or '-'}
Фамилия: {u.last_name or '-'}
Username: @{u.username or 'нет'}
Telegram ID: {u.id}
Язык: {u.language_code or '-'}
Premium: {'Да' if u.is_premium else 'Нет'}""")

async def rate(update,ctx):
    ctx.user_data["state"]=None
    await update.message.reply_text("📈 Курс Stars\n\n100 ⭐ = 138 ₽\n\nКурс периодически меняется.")

async def support(update,ctx):
    ctx.user_data["state"]=None
    await update.message.reply_text("💬 Поддержка: @Lakizyx")

async def buy(update,ctx):
    ctx.user_data["state"]=None
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("👤 Для себя",callback_data="self"),InlineKeyboardButton("🎁 Для друга",callback_data="friend")]])
    await update.message.reply_text("Для кого купить Stars?",reply_markup=kb)

async def on_text(update,ctx):
    t=update.message.text
    if t=="⭐ Купить Stars": return await buy(update,ctx)
    if t=="👤 Профиль": return await profile(update,ctx)
    if t=="📈 Курс Stars": return await rate(update,ctx)
    if t=="💬 Поддержка": return await support(update,ctx)
    st=ctx.user_data.get("state")
    if st=="username":
        ctx.user_data["target"]=t.replace("@","")
        ctx.user_data["state"]="amount"
        return await update.message.reply_text("Введите количество Stars (например 750):")
    if st=="amount":
        if not t.isdigit():
            return await update.message.reply_text("Введите только число.")
        stars=int(t); price=round(stars*PRICE_PER_STAR)
        ctx.user_data["stars"]=stars
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("💳 СПБ",callback_data="spb"),InlineKeyboardButton("💎 Криптовалюта",callback_data="crypto")]])
        return await update.message.reply_text(
f"""🛒 Подтверждение заказа

Получатель: @{ctx.user_data['target']}
Количество: {stars} ⭐
К оплате: {price} ₽

Выберите способ оплаты:""",reply_markup=kb)

async def on_callback(update,ctx):
    q=update.callback_query; await q.answer(); d=q.data
    if d=="self":
        ctx.user_data["target"]=q.from_user.username or str(q.from_user.id)
        ctx.user_data["state"]="amount"
        return await q.edit_message_text(f"Получатель: @{ctx.user_data['target']}\n\nВведите количество Stars:")
    if d=="friend":
        ctx.user_data["state"]="username"
        return await q.edit_message_text("Введите @username получателя:")
    stars=ctx.user_data["stars"]; price=round(stars*PRICE_PER_STAR)
    if d=="spb":
        return await q.edit_message_text(
f"""💳 Оплата по СБП

Получатель: @{ctx.user_data['target']}
Сумма: {price} ₽

После оплаты отправьте чек в @Lakizyx""")
    if d=="crypto":
        return await q.edit_message_text(
f"""💎 Оплата криптовалютой

Сумма: {price} ₽

Поддерживаются: USDT (TON), TON.

Реквизиты выдаёт @Lakizyx после подтверждения.""")

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,on_text))
app.add_handler(CallbackQueryHandler(on_callback))
app.run_polling()
