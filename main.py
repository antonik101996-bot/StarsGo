# StarsGo main.py
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import os

TOKEN=os.getenv("BOT_TOKEN")
PRICE=1.38

def main_menu():
    return ReplyKeyboardMarkup([["⭐ Купить Stars"],["👤 Профиль","📈 Курс Stars"],["💬 Поддержка"]],resize_keyboard=True)

async def start(u,c):
    c.user_data.clear()
    await u.message.reply_text("✨ Добро пожаловать в StarsGo!",reply_markup=main_menu())

async def buy(u,c):
    kb=InlineKeyboardMarkup([
      [InlineKeyboardButton("100 ⭐",callback_data="p100"),InlineKeyboardButton("300 ⭐",callback_data="p300")],
      [InlineKeyboardButton("500 ⭐",callback_data="p500")],
      [InlineKeyboardButton("✏️ Ввести своё количество",callback_data="custom")],
      [InlineKeyboardButton("◀️ Назад",callback_data="back")]])
    await u.message.reply_text("Выберите пакет Stars:",reply_markup=kb)

async def profile(u,c):
    me=u.effective_user
    kb=InlineKeyboardMarkup([
      [InlineKeyboardButton("💎 Купить Premium StarsGo",callback_data="premium")],
      [InlineKeyboardButton("◀️ Назад",callback_data="back")]])
    await u.message.reply_text(f"""👤 Профиль

Имя: {me.first_name}
Username: @{me.username or "нет"}
ID: {me.id}
Premium Telegram: Нет

💎 Premium StarsGo
Скидка 25% на все покупки Stars.
Стоимость: 999 ₽ единоразово.""",reply_markup=kb)

async def rate(u,c):
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад",callback_data="back")]])
    await u.message.reply_text("📈 Курс Stars\n\n100 ⭐ = 138 ₽\n\nКурс периодически меняется.",reply_markup=kb)

async def support(u,c):
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад",callback_data="back")]])
    await u.message.reply_text("💬 Поддержка\n\n@Lakizyx",reply_markup=kb)

async def text(u,c):
    t=u.message.text
    st=c.user_data.get("st")
    if t=="⭐ Купить Stars": return await buy(u,c)
    if t=="👤 Профиль": c.user_data["st"]=None; return await profile(u,c)
    if t=="📈 Курс Stars": c.user_data["st"]=None; return await rate(u,c)
    if t=="💬 Поддержка": c.user_data["st"]=None; return await support(u,c)
    if st=="amount":
        if not t.isdigit(): return await u.message.reply_text("Введите число.")
        s=int(t); c.user_data["stars"]=s
        p=round(s*PRICE)
        kb=InlineKeyboardMarkup([
          [InlineKeyboardButton("💳 СПБ",callback_data="spb"),InlineKeyboardButton("💎 Криптовалюта",callback_data="crypto")],
          [InlineKeyboardButton("◀️ Назад",callback_data="back")]])
        c.user_data["st"]=None
        return await u.message.reply_text(f"🛒 Заказ\n\nПолучатель: @{u.effective_user.username or u.effective_user.id}\nКоличество: {s} ⭐\nСумма: {p} ₽",reply_markup=kb)

async def cb(u,c):
    q=u.callback_query; await q.answer(); d=q.data
    if d=="back":
        c.user_data.clear()
        return await q.edit_message_text("◀️ Возврат в главное меню. Используйте кнопки снизу.")
    if d=="custom":
        c.user_data["st"]="amount"
        return await q.edit_message_text("Введите количество Stars:")
    if d.startswith("p"):
        s=int(d[1:]); p=round(s*PRICE)
        kb=InlineKeyboardMarkup([
          [InlineKeyboardButton("💳 СПБ",callback_data="spb"),InlineKeyboardButton("💎 Криптовалюта",callback_data="crypto")],
          [InlineKeyboardButton("◀️ Назад",callback_data="back")]])
        c.user_data["stars"]=s
        return await q.edit_message_text(f"🛒 Подтверждение\n\nКоличество: {s} ⭐\nСтоимость: {p} ₽",reply_markup=kb)
    if d=="premium":
        kb=InlineKeyboardMarkup([
          [InlineKeyboardButton("💳 Оплатить 999 ₽",callback_data="premium_spb")],
          [InlineKeyboardButton("◀️ Назад",callback_data="back")]])
        return await q.edit_message_text("💎 Premium StarsGo\n\nСтоимость: 999 ₽\nВыгода: скидка 25% на покупку Stars.",reply_markup=kb)
    if d=="premium_spb":
        return await q.edit_message_text("💳 Оплата Premium\n\nСумма: 999 ₽\nПосле оплаты отправьте чек @Lakizyx")
    if d=="spb":
        s=c.user_data.get("stars",0); p=round(s*PRICE)
        return await q.edit_message_text(f"💳 Оплата по СБП\n\nК оплате: {p} ₽\n\nПосле оплаты отправьте чек @Lakizyx")
    if d=="crypto":
        s=c.user_data.get("stars",0); p=round(s*PRICE)
        return await q.edit_message_text(f"💎 Оплата криптовалютой\n\nК оплате: {p} ₽\nUSDT (TON) / TON\n\nРеквизиты выдаёт @Lakizyx")

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text))
app.add_handler(CallbackQueryHandler(cb))
app.run_polling()
