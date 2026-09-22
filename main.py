from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import os

TOKEN = os.getenv("BOT_TOKEN")

keyboard = ReplyKeyboardMarkup(
    [
        ["⭐ Купить Stars"],
        ["👤 Профиль", "💬 Поддержка"],
        ["📈 Курс Stars"],
    ],
    resize_keyboard=True,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Добро пожаловать в StarsGo!\n\nВыберите действие:",
        reply_markup=keyboard,
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "⭐ Купить Stars":
        await update.message.reply_text(
            "⭐ Доступные пакеты:\n\n"
            "100 ⭐ — 138 ₽\n"
            "250 ⭐ — 345 ₽\n"
            "500 ⭐ — 690 ₽\n"
            "1000 ⭐ — 1380 ₽"
        )

    elif text == "👤 Профиль":
        await update.message.reply_text(
            f"👤 Ваш Telegram ID: {update.effective_user.id}"
        )

    elif text == "💬 Поддержка":
        await update.message.reply_text(
            "💬 Поддержка: @StarsGoSupport"
        )

    elif text == "📈 Курс Stars":
        await update.message.reply_text(
            "📈 Актуальный курс:\n100 ⭐ = 138 ₽"
        )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, buttons)
    )

    print("StarsGo запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
