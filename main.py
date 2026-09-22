# StarsGo V2 - main.py
# python-telegram-bot 20+
import os, sqlite3, uuid, time
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")
ADMIN = "Lakizyx"
PRICE_PER_STAR = 1.35
db = sqlite3.connect("starsgo.db", check_same_thread=False)
cur = db.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS premium(username TEXT PRIMARY KEY)")
db.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    stars INTEGER NOT NULL,
    rub_amount REAL NOT NULL,
    usdt_amount REAL NOT NULL,
    memo TEXT UNIQUE NOT NULL,
    wallet TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at INTEGER,
    paid_at INTEGER
)
""")
db.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    stars INTEGER NOT NULL,
    rub_amount REAL NOT NULL,
    usdt_amount REAL NOT NULL,
    memo TEXT NOT NULL UNIQUE,
    wallet TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP
)
""")
db.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS balances (
    username TEXT PRIMARY KEY,
    balance REAL DEFAULT 0
)
""")
db.commit()
def is_premium(username):
    if not username: return False
    return cur.execute("SELECT 1 FROM premium WHERE username=?",(username.lower(),)).fetchone() is not None
def give_premium(username):
    cur.execute("INSERT OR IGNORE INTO premium VALUES(?)",(username.lower(),)); db.commit()
def remove_premium(username):
    cur.execute("DELETE FROM premium WHERE username=?",(username.lower(),)); db.commit()
def calc(stars, username):
    p = round(stars * PRICE_PER_STAR)
    return round(p * 0.80) if is_premium(username) else p

MENU = ReplyKeyboardMarkup([["⭐ Купить Stars"],["👤 Профиль","📈 Курс Stars"],["💬 Поддержка"]], resize_keyboard=True)

async def start(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("✨ Добро пожаловать в StarsGo!", reply_markup=MENU)

async def profile(update:Update,ctx):
    u=update.effective_user
    txt=f"👤 Профиль\n\nИмя: {u.first_name}\nUsername: @{u.username or 'нет'}\nID: {u.id}\nPremium Telegram: {'Да' if u.is_premium else 'Нет'}\n\n"
    if is_premium(u.username):
        txt += "🔥 У ВАС УЖЕ ЕСТЬ PREMIUM ПОДПИСКА\nСкидка 20% активна."
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад",callback_data="back_profile")]])
    else:
        txt += "💎 Premium StarsGo\n999 ₽ • Скидка 20%"
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Купить Premium",callback_data="premium")],[InlineKeyboardButton("◀️ Назад",callback_data="back_profile")]])
    await update.message.reply_text(txt, reply_markup=kb)

async def buy(update:Update,ctx):
    kb=InlineKeyboardMarkup([
      [InlineKeyboardButton("100 ⭐",callback_data="s100"),InlineKeyboardButton("300 ⭐",callback_data="s300")],
      [InlineKeyboardButton("500 ⭐",callback_data="s500")],
      [InlineKeyboardButton("✏️ Ввести своё количество",callback_data="custom")]])
    await update.message.reply_text("⭐ Выберите количество Stars:", reply_markup=kb)

async def rate(update,ctx):
    await update.message.reply_text("📈 Курс Stars\n\n100 ⭐ = 138 ₽\nКурс периодически меняется.")

async def support(update,ctx):
    await update.message.reply_text("💬 Поддержка\n\n@Lakizyx")

async def pay_menu(update,ctx):
    stars=ctx.user_data["stars"]; price=calc(stars, update.effective_user.username)
    kb=InlineKeyboardMarkup([
      [InlineKeyboardButton("💳 СПБ",callback_data="pay_spb"),InlineKeyboardButton("💎 TON / USDT",callback_data="pay_crypto")],
      [InlineKeyboardButton("◀️ Назад",allback_data="back_buy")]])
    await update.message.reply_text(f"🛒 Подтверждение\n\nКоличество: {stars} ⭐\nСтоимость: {price} ₽", reply_markup=kb)

async def text(update,ctx):
    t=update.message.text
    if t=="⭐ Купить Stars": return await buy(update,ctx)
    if t=="👤 Профиль": return await profile(update,ctx)
    if t=="📈 Курс Stars": return await rate(update,ctx)
    if t=="💬 Поддержка": return await support(update,ctx)
    st=ctx.user_data.get("state")
    if st=="custom_amount":
        if not t.isdigit(): return await update.message.reply_text("Введите число.")
        ctx.user_data["stars"]=int(t); ctx.user_data["state"]=None
        return await pay_menu(update,ctx)
async def admin_give(update, ctx):
    if update.effective_user.username != ADMIN:
        return

    if len(ctx.args) != 2:
        return await update.message.reply_text(
            "❌ Формат:\n/give username сумма"
        )

    username = ctx.args[0].lstrip("@").lower()

    try:
        amount = float(ctx.args[1])
    except ValueError:
        return await update.message.reply_text(
            "❌ Сумма должна быть числом."
        )

    cur.execute(
        "INSERT OR IGNORE INTO balances (username, balance) VALUES (?, 0)",
        (username,)
    )

    cur.execute(
        "UPDATE balances SET balance = balance + ? WHERE username = ?",
        (amount, username)
    )

    db.commit()

    cur.execute(
        "SELECT balance FROM balances WHERE username = ?",
        (username,)
    )

    balance = cur.fetchone()[0]

    await update.message.reply_text(
        f"➕ Баланс пополнен\n\n"
        f"Пользователь: @{username}\n"
        f"Начислено: {amount:g}\n"
        f"Баланс: {balance:g}"
    )
async def admin_take(update, ctx):
    if update.effective_user.username != ADMIN:
        return

    if len(ctx.args) != 2:
        return await update.message.reply_text(
            "❌ Формат:\n/take username сумма"
        )

    username = ctx.args[0].lstrip("@").lower()

    try:
        amount = float(ctx.args[1])
    except ValueError:
        return await update.message.reply_text(
            "❌ Сумма должна быть числом."
        )

    if amount <= 0:
        return await update.message.reply_text(
            "❌ Сумма должна быть больше 0."
        )

    cur.execute(
        "SELECT balance FROM balances WHERE username = ?",
        (username,)
    )

    row = cur.fetchone()

    if not row:
        return await update.message.reply_text(
            f"❌ Пользователь @{username} не найден."
        )

    balance = row[0]

    if amount > balance:
        return await update.message.reply_text(
            f"❌ Недостаточно средств.\n\n"
            f"Пользователь: @{username}\n"
            f"Баланс: {balance:g}\n"
            f"Запрошено: {amount:g}"
        )

    cur.execute(
        "UPDATE balances SET balance = balance - ? WHERE username = ?",
        (amount, username)
    )

    db.commit()

    cur.execute(
        "SELECT balance FROM balances WHERE username = ?",
        (username,)
    )

    new_balance = cur.fetchone()[0]

    await update.message.reply_text(
        f"➖ Баланс уменьшен\n\n"
        f"Пользователь: @{username}\n"
        f"Снято: {amount:g}\n"
        f"Баланс: {new_balance:g}"
    )
async def admin_premium(update, ctx):
    if update.effective_user.username != ADMIN:
        return

    if len(ctx.args) != 1:
        return await update.message.reply_text(
            "❌ Формат:\n/premium username"
        )

    username = ctx.args[0].lstrip("@").lower()

    give_premium(username)

    await update.message.reply_text(
        f"👑 Premium выдан\n\n"
        f"Пользователь: @{username}\n"
        f"Скидка: 20%"
    )

def create_order(username, stars, rub_amount, usdt_amount, wallet):
    order_id = str(uuid.uuid4())
    memo = str(uuid.uuid4())

    cur.execute("""
    INSERT INTO orders (
        order_id,
        username,
        stars,
        rub_amount,
        usdt_amount,
        memo,
        wallet,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_id,
        username.lower(),
        stars,
        rub_amount,
        usdt_amount,
        memo,
        wallet,
        int(time.time())
    ))

    db.commit()

    return order_id, memo

async def cb(update,ctx):
    q=update.callback_query; await q.answer(); d=q.data
    if d == "admin_users":
        cur.execute("SELECT COUNT(*) FROM premium")
        count = cur.fetchone()[0]
        return await q.message.reply_text(f"👤 Пользователи\n\nВсего: {count}")
    if d == "admin_balances":
        return await q.message.reply_text("💰 Раздел балансов открыт")
    if d == "admin_stars":
        return await q.message.reply_text("⭐ Раздел Stars открыт")
        
    if d=="back_profile": return await q.edit_message_text("👤 Закройте сообщение и используйте меню снизу.")
    if d=="back_buy":
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("100 ⭐",callback_data="s100"),InlineKeyboardButton("300 ⭐",callback_data="s300")],[InlineKeyboardButton("500 ⭐",callback_data="s500")],[InlineKeyboardButton("✏️ Ввести своё количество",callback_data="custom")]])
        return await q.edit_message_text("⭐ Выберите количество Stars:", reply_markup=kb)
    if d=="custom":
        ctx.user_data["state"]="custom_amount"
        return await q.edit_message_text("✏️ Введите количество Stars:")
    if d.startswith("s"):
        ctx.user_data["stars"]=int(d[1:])
        price=calc(ctx.user_data["stars"], q.from_user.username)
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("💳 СПБ",callback_data="pay_spb"),InlineKeyboardButton("💎 TON / USDT",callback_data="pay_crypto")],[InlineKeyboardButton("◀️ Назад",callback_data="back_buy")]])
        return await q.edit_message_text(f"🛒 Подтверждение\n\nКоличество: {ctx.user_data['stars']} ⭐\nСтоимость: {price} ₽", reply_markup=kb)
        
    if d=="premium":
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("💳 СПБ",callback_data="prem_spb"),InlineKeyboardButton("💎 TON / USDT",callback_data="prem_crypto")],[InlineKeyboardButton("◀️ Назад",callback_data="back_profile")]])
        return await q.edit_message_text("💎 Premium StarsGo\n\n999 ₽\nСкидка 20% на все покупки.", reply_markup=kb)
    if d=="prem_spb": return await q.edit_message_text("💳 Premium\n999 ₽\nПосле оплаты: @Lakizyx")
    if d=="prem_crypto": return await q.edit_message_text("💎 Premium\n999 ₽\nUSDT (TON) / TON")
    if d=="pay_spb":
        return await q.edit_message_text(f"💳 СПБ\nК оплате: {calc(ctx.user_data['stars'], q.from_user.username)} ₽")
    if d=="pay_crypto":
        return await q.edit_message_text(f"💎 TON / USDT\nК оплате: {calc(ctx.user_data['stars'], q.from_user.username)} ₽")
async def cmd_premium(update,ctx):
    if update.effective_user.username!=ADMIN: return
    p=update.message.text.split()
    if len(p)!=2: return await update.message.reply_text("Используй: /premium @user")
    give_premium(p[1].replace("@","")); await update.message.reply_text("👑 Premium выдан")
async def cmd_unpremium(update,ctx):
    if update.effective_user.username!=ADMIN: return
    p=update.message.text.split()
    if len(p)!=2: return await update.message.reply_text("Используй: /unpremium @user")
    remove_premium(p[1].replace("@","")); await update.message.reply_text("❌ Premium снят")
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN:
        return

    keyboard = [
        [InlineKeyboardButton("👤 Пользователи", callback_data="admin_users")],
        [InlineKeyboardButton("💰 Балансы", callback_data="admin_balances")],
        [InlineKeyboardButton("⭐ Stars", callback_data="admin_stars")],
        [InlineKeyboardButton("➕ Выдать баланс", callback_data="admin_give")],
        [InlineKeyboardButton("➖ Снять баланс", callback_data="admin_take")],
        [InlineKeyboardButton("🚫 Блокировка", callback_data="admin_block")],
        [InlineKeyboardButton("🎁 Промокоды", callback_data="admin_promo")],
        [InlineKeyboardButton("📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📝 Логи", callback_data="admin_logs")],
    ]

    await update.message.reply_text(
        "⚙️ Админ-панель StarsGo",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("admin", admin))
app.add_handler(CommandHandler("give", admin_give))
app.add_handler(CommandHandler("take", admin_take))
app.add_handler(CommandHandler("premium", admin_premium))
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("premium",cmd_premium))
app.add_handler(CommandHandler("unpremium",cmd_unpremium))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,text))
app.add_handler(CallbackQueryHandler(cb))
app.run_polling()
