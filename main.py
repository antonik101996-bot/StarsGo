from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import os

bot = Bot(os.getenv("BOT_TOKEN"))
dp = Dispatcher()

kb = ReplyKeyboardBuilder()
kb.button(text="⭐ Купить Stars")
kb.button(text="👤 Профиль")
kb.button(text="💬 Поддержка")
kb.button(text="📈 Курс Stars")
kb.adjust(1, 2, 1)
@dp.message(CommandStart())
async def start(msg: types.Message):
    await msg.answer(
        "Добро пожаловать в StarsGo! 🚀",
        reply_markup=kb.as_markup(resize_keyboard=True)
