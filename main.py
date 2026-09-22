from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")

PRICES = {100:138,200:276,300:414,400:552,500:690,1000:1380}

menu = ReplyKeyboardMarkup(
    [["⭐ Купить Stars"],
     ["👤 Профиль","💬 Поддержка"],
     ["📈 Курс Stars"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Добро пожаловать в StarsGo!\n\nВыберите действие:",
        reply_markup=menu
    )

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👤 Ваш Telegram ID: {update.effective_user.id}")

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💬 Поддержка: @Lakizyx")

async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Актуальный курс\n\n100 ⭐ = 138 ₽")

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("100 ⭐", callback_data="100"), InlineKeyboardButton("200 ⭐", callback_data="200")],
        [InlineKeyboardButton("300 ⭐", callback_data="300"), InlineKeyboardButton("400 ⭐", callback_data="400")],
        [InlineKeyboardButton("500 ⭐", callback_data="500"), InlineKeyboardButton("1000 ⭐", callback_data="1000")]
    ])
    await update.message.reply_text("⭐ Выберите пакет звёзд:", reply_markup=kb)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if txt == "⭐ Купить Stars":
        await buy(update, context)
    elif txt == "👤 Профиль":
        await profile(update, context)
    elif txt == "💬 Поддержка":
        await support(update, context)
    elif txt == "📈 Курс Stars":
        await rate(update, context)

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    if data.startswith("ok_"):
        stars = int(data.split("_")[1])
        price = PRICES[stars]
        await q.edit_message_text(
            f"✅ Заявка создана!\n\nПакет: {stars} ⭐\nСумма: {price} ₽\n\nДля оплаты напишите @Lakizyx"
        )
        return
    stars = int(data)
    price = PRICES[stars]
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Подтвердить покупку", callback_data=f"ok_{stars}")
    ]])
    await q.edit_message_text(
        f"🛒 Подтверждение покупки\n\nВы покупаете {stars} ⭐ за {price} ₽.\n\nНажмите кнопку ниже для подтверждения.",
        reply_markup=kb
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, buttons))
    app.add_handler(CallbackQueryHandler(callbacks))
    print("StarsGo запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
