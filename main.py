# StarsGo V5 - main.py
# python-telegram-bot 20+
import os, sqlite3, uuid, time
import requests
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

TOKEN = "8622886894:AAHbUeDjhOkpPOH2rsQFQcNWgMRlQm2IPZk"
ADMIN = "Lakizyx"

GRAM_WALLET = "UQDCNwjGlMioMvMqB8uKuBFyN202Zny9V4i_SOesSyCfydmb"
USDT_WALLET = "UQD6Naq0pdI-ea4_P2U1tAgj7rSHHLwJtEiHmXuXJSYK6L7l"
TONCENTER_API = "fe4563f7b2b573f4091b2b89c2ceaf3a1f7c0e3666abcedcd0dc1b951ea3c82f"
USDT_RATE = 84.50

PRICE_PER_STAR = 1.35

STARS_OPEN=True
PREMIUM_OPEN=True
db = sqlite3.connect("starsgo.db", check_same_thread=False)
cur = db.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS premium(username TEXT PRIMARY KEY)")
db.commit()

cur.execute(""" CREATE TABLE IF NOT EXISTS orders ( order_id TEXT PRIMARY KEY, username TEXT NOT NULL, stars INTEGER NOT NULL, rub_amount REAL NOT NULL, usdt_amount REAL NOT NULL, memo TEXT UNIQUE NOT NULL, wallet TEXT NOT NULL, status TEXT DEFAULT 'pending', created_at INTEGER, paid_at INTEGER ) """)
db.commit()

cur.execute(""" CREATE TABLE IF NOT EXISTS orders ( order_id TEXT PRIMARY KEY, username TEXT NOT NULL, stars INTEGER NOT NULL, rub_amount REAL NOT NULL, usdt_amount REAL NOT NULL, memo TEXT NOT NULL UNIQUE, wallet TEXT NOT NULL, status TEXT DEFAULT 'pending', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, paid_at TIMESTAMP ) """)
db.commit()

cur.execute(""" CREATE TABLE IF NOT EXISTS balances ( username TEXT PRIMARY KEY, balance REAL DEFAULT 0 ) """)
db.commit()
cur.execute(""" CREATE TABLE IF NOT EXISTS settings ( k TEXT PRIMARY KEY, v TEXT ) """)
db.commit()
row=cur.execute("SELECT v FROM settings WHERE k='price'").fetchone()
if row:
    PRICE_PER_STAR=float(row[0])

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

def get_menu(username):
    rows=[["в­ђ РљСѓРїРёС‚СЊ Stars"],["рџ‘‘ Telegram Premium"],["рџ‘¤ РџСЂРѕС„РёР»СЊ","рџ“€ РљСѓСЂСЃ Stars"],["рџ“¦ РњРѕРё Р·Р°РєР°Р·С‹","рџ’¬ РџРѕРґРґРµСЂР¶РєР°"]]
    if username==ADMIN:
        rows.append(["вљ™пёЏ РђРґРјРёРЅ"])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

async def start(update:Update,ctx:ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text("вњЁ *StarsGo V4 PRO*\nв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓ\nв­ђ РџРѕРєСѓРїРєР° Stars\nрџ‘‘ Telegram Premium\nрџ’Ћ GRAM / USDT\nв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓв”Ѓ\nР’С‹Р±РµСЂРёС‚Рµ СЂР°Р·РґРµР» РІ РјРµРЅСЋ РЅРёР¶Рµ.", reply_markup=get_menu(update.effective_user.username), parse_mode="Markdown")

async def profile(update:Update,ctx):
    u=update.effective_user
    bal=cur.execute("SELECT balance FROM balances WHERE username=?",( (u.username or "").lower(),)).fetchone()
    balance=bal[0] if bal else 0
    cnt=cur.execute("SELECT COUNT(*) FROM orders WHERE username=?",( (u.username or "").lower(),)).fetchone()[0]
    txt=f"рџЊџ *РџСЂРѕС„РёР»СЊ StarsGo*\n\nРРјСЏ: {u.first_name}\nUsername: @{u.username or 'РЅРµС‚'}\nID: {u.id}\nPremium Telegram: {'Р”Р°' if u.is_premium else 'РќРµС‚'}\nР‘Р°Р»Р°РЅСЃ: {balance:g} в‚Ѕ\nР—Р°РєР°Р·РѕРІ: {cnt}\n\n"
    if is_premium(u.username):
        txt += "рџ”Ґ РЈ Р’РђРЎ РЈР–Р• Р•РЎРўР¬ PREMIUM РџРћР”РџРРЎРљРђ\nРЎРєРёРґРєР° 20% Р°РєС‚РёРІРЅР°."
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("в—ЂпёЏ РќР°Р·Р°Рґ",callback_data="back_profile")]])
    else:
        txt += "рџ‘‘ Premium StarsGo\n\nвЂў РџРѕРґРїРёСЃРєР°: 1 РјРµСЃСЏС†\nвЂў РЎРєРёРґРєР° 20% РЅР° РІСЃРµ Stars\nвЂў Р‘РµР·Р»РёРјРёС‚РЅР°СЏ РїРѕРєСѓРїРєР° Stars"
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("рџ‘‘ Premium StarsGo",callback_data="premium")],[InlineKeyboardButton("в—ЂпёЏ РќР°Р·Р°Рґ",callback_data="back_profile")]])
    await update.message.reply_text(txt, reply_markup=kb)

async def buy(update:Update,ctx):
    kb=InlineKeyboardMarkup([
      [InlineKeyboardButton("100 в­ђ",callback_data="s100"),InlineKeyboardButton("200 в­ђ",callback_data="s200")],
      [InlineKeyboardButton("300 в­ђ",callback_data="s300"),InlineKeyboardButton("400 в­ђ",callback_data="s400")],
      [InlineKeyboardButton("500 в­ђ",callback_data="s500"),InlineKeyboardButton("1000 в­ђ",callback_data="s1000")],
      [InlineKeyboardButton("вњЏпёЏ Р”СЂСѓРіРѕРµ РєРѕР»РёС‡РµСЃС‚РІРѕ",callback_data="custom")]])
    await update.message.reply_text("в­ђ Р’С‹Р±РµСЂРёС‚Рµ РєРѕР»РёС‡РµСЃС‚РІРѕ Stars:", reply_markup=kb)

async def rate(update,ctx):
    await update.message.reply_text(
        f"рџ“€ РљСѓСЂСЃ Stars\n\n1 в­ђ = {PRICE_PER_STAR:.2f} в‚Ѕ"
    )

async def support(update,ctx):
    await update.message.reply_text("рџ’¬ РџРѕРґРґРµСЂР¶РєР°\n\n@Lakizyx")


async def my_orders(update,ctx):
    u=(update.effective_user.username or "").lower()
    rows=cur.execute("SELECT stars,status,created_at FROM orders WHERE username=? ORDER BY created_at DESC LIMIT 10",(u,)).fetchall()
    if not rows:
        return await update.message.reply_text("рџ“¦ РЈ РІР°СЃ РїРѕРєР° РЅРµС‚ Р·Р°РєР°Р·РѕРІ.")
    txt="рџ“¦ РџРѕСЃР»РµРґРЅРёРµ Р·Р°РєР°Р·С‹\n\n"
    for s,st,_ in rows:
        dt=time.strftime('%d.%m.%Y', time.localtime(_)); txt+=f"в­ђ {s} вЂў {'вњ… РћРїР»Р°С‡РµРЅ' if st=='paid' else 'вЏі РћР¶РёРґР°РµС‚'}\nрџ“… {dt}\n\n"
    await update.message.reply_text(txt)

async def pay_menu(update,ctx):
    stars=ctx.user_data["stars"]; price=calc(stars, update.effective_user.username)
    kb=InlineKeyboardMarkup([
      [InlineKeyboardButton("рџ’і РЎРџР‘",callback_data="pay_spb"),InlineKeyboardButton("рџ’Ћ РљСЂРёРїС‚РѕРІР°Р»СЋС‚Р°",callback_data="pay_crypto")],
      [InlineKeyboardButton("в—ЂпёЏ РќР°Р·Р°Рґ",callback_data="back_buy"),InlineKeyboardButton("рџЏ  РњРµРЅСЋ",callback_data="home")]])
    await update.message.reply_text(f"рџ›’ РџРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ\n\nРљРѕР»РёС‡РµСЃС‚РІРѕ: {stars} в­ђ\nРЎС‚РѕРёРјРѕСЃС‚СЊ: {price} в‚Ѕ", reply_markup=kb)

async def text(update,ctx):
    t = update.message.text

    if ctx.user_data.get("state")=="change_rate":
        try:
            global PRICE_PER_STAR
            PRICE_PER_STAR=float(t.replace(",", "."))
            cur.execute("INSERT OR REPLACE INTO settings VALUES(?,?)",("price",str(PRICE_PER_STAR))); db.commit(); ctx.user_data["state"]=None
            return await update.message.reply_text(f"вњ… РќРѕРІС‹Р№ РєСѓСЂСЃ: {PRICE_PER_STAR} в‚Ѕ")
        except:
            return await update.message.reply_text("Р’РІРµРґРёС‚Рµ С‡РёСЃР»Рѕ, РЅР°РїСЂРёРјРµСЂ 1.35")

    if t == "в­ђ РљСѓРїРёС‚СЊ Stars":
        if not STARS_OPEN:
            return await update.message.reply_text("вќЊ РџСЂРѕРґР°Р¶Р° Stars Р·Р°РєСЂС‹С‚Р°")
        return await buy(update,ctx)

    if t == "рџ‘¤ РџСЂРѕС„РёР»СЊ":
        return await profile(update,ctx)

    if t == "рџ“€ РљСѓСЂСЃ Stars":
        return await rate(update,ctx)

    if t == "рџ“¦ РњРѕРё Р·Р°РєР°Р·С‹":
        return await my_orders(update,ctx)

    if t == "рџ’¬ РџРѕРґРґРµСЂР¶РєР°":
        return await support(update,ctx)

    if t == "вљ™пёЏ РђРґРјРёРЅ" and update.effective_user.username==ADMIN:
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"в­ђ Stars: {'рџџў' if STARS_OPEN else 'рџ”ґ'}",callback_data="toggle_stars")],
            [InlineKeyboardButton(f"рџ‘‘ Premium: {'рџџў' if PREMIUM_OPEN else 'рџ”ґ'}",callback_data="toggle_premium")],
            [InlineKeyboardButton("рџ’І РР·РјРµРЅРёС‚СЊ РєСѓСЂСЃ", callback_data="admin_rate")]
        ])
        return await update.message.reply_text("вљ™пёЏ РђРґРјРёРЅ-РїР°РЅРµР»СЊ",reply_markup=kb)

    if t == "рџ‘‘ Telegram Premium":
        if not PREMIUM_OPEN:
            return await update.message.reply_text("вќЊ РџСЂРѕРґР°Р¶Р° Premium Р·Р°РєСЂС‹С‚Р°")
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("3 РјРµСЃСЏС†Р° вЂў 999 в‚Ѕ", callback_data="tg3")],
            [InlineKeyboardButton("6 РјРµСЃСЏС†РµРІ вЂў 1299 в‚Ѕ", callback_data="tg6")],
            [InlineKeyboardButton("12 РјРµСЃСЏС†РµРІ вЂў 2299 в‚Ѕ", callback_data="tg12")]
        ])
        return await update.message.reply_text(
            "рџ‘‘ Telegram Premium\n\nР’С‹Р±РµСЂРёС‚Рµ СЃСЂРѕРє:",
            reply_markup=kb
        )

    if ctx.user_data.get("state") == "custom_amount":
        if not t.isdigit():
            return await update.message.reply_text("Р’РІРµРґРёС‚Рµ С‡РёСЃР»Рѕ.")

        stars = int(t)

        if stars < 50 or stars > 5000:
            return await update.message.reply_text(
                "вќЊ РњРѕР¶РЅРѕ РєСѓРїРёС‚СЊ РѕС‚ 50 РґРѕ 5000 в­ђ Р·Р° РѕРґРЅСѓ С‚СЂР°РЅР·Р°РєС†РёСЋ."
            )

        ctx.user_data["stars"] = stars
        ctx.user_data["state"] = None

        price = calc(stars, update.effective_user.username)

        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("рџ’і РЎРџР‘", callback_data="pay_spb"),
                InlineKeyboardButton("рџ’Ћ РљСЂРёРїС‚РѕРІР°Р»СЋС‚Р°", callback_data="pay_crypto")
            ],
            [
                InlineKeyboardButton("в—ЂпёЏ РќР°Р·Р°Рґ", callback_data="back_buy")
            ]
        ])

        return await update.message.reply_text(
            f"рџ›’ РџРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ\n\n"
            f"РљРѕР»РёС‡РµСЃС‚РІРѕ: {stars} в­ђ\n"
            f"РЎС‚РѕРёРјРѕСЃС‚СЊ: {price} в‚Ѕ",
            reply_markup=kb
        )
async def admin_give(update, ctx):
    if update.effective_user.username != ADMIN:
        return

    if len(ctx.args) != 2:
        return await update.message.reply_text(
            "вќЊ Р¤РѕСЂРјР°С‚:\n/give username СЃСѓРјРјР°"
        )

    username = ctx.args[0].lstrip("@").lower()

    try:
        amount = float(ctx.args[1])
    except ValueError:
        return await update.message.reply_text(
            "вќЊ РЎСѓРјРјР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ С‡РёСЃР»РѕРј."
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
        f"вћ• Р‘Р°Р»Р°РЅСЃ РїРѕРїРѕР»РЅРµРЅ\n\n"
        f"РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ: @{username}\n"
        f"РќР°С‡РёСЃР»РµРЅРѕ: {amount:g}\n"
        f"Р‘Р°Р»Р°РЅСЃ: {balance:g}"
    )
async def admin_take(update, ctx):
    if update.effective_user.username != ADMIN:
        return

    if len(ctx.args) != 2:
        return await update.message.reply_text(
            "вќЊ Р¤РѕСЂРјР°С‚:\n/take username СЃСѓРјРјР°"
        )

    username = ctx.args[0].lstrip("@").lower()

    try:
        amount = float(ctx.args[1])
    except ValueError:
        return await update.message.reply_text(
            "вќЊ РЎСѓРјРјР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ С‡РёСЃР»РѕРј."
        )

    if amount <= 0:
        return await update.message.reply_text(
            "вќЊ РЎСѓРјРјР° РґРѕР»Р¶РЅР° Р±С‹С‚СЊ Р±РѕР»СЊС€Рµ 0."
        )

    cur.execute(
        "SELECT balance FROM balances WHERE username = ?",
        (username,)
    )

    row = cur.fetchone()

    if not row:
        return await update.message.reply_text(
            f"вќЊ РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ @{username} РЅРµ РЅР°Р№РґРµРЅ."
        )

    balance = row[0]

    if amount > balance:
        return await update.message.reply_text(
            f"вќЊ РќРµРґРѕСЃС‚Р°С‚РѕС‡РЅРѕ СЃСЂРµРґСЃС‚РІ.\n\n"
            f"РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ: @{username}\n"
            f"Р‘Р°Р»Р°РЅСЃ: {balance:g}\n"
            f"Р—Р°РїСЂРѕС€РµРЅРѕ: {amount:g}"
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
        f"вћ– Р‘Р°Р»Р°РЅСЃ СѓРјРµРЅСЊС€РµРЅ\n\n"
        f"РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ: @{username}\n"
        f"РЎРЅСЏС‚Рѕ: {amount:g}\n"
        f"Р‘Р°Р»Р°РЅСЃ: {new_balance:g}"
    )
async def admin_premium(update, ctx):
    if update.effective_user.username != ADMIN:
        return

    if len(ctx.args) != 1:
        return await update.message.reply_text(
            "вќЊ Р¤РѕСЂРјР°С‚:\n/premium username"
        )

    username = ctx.args[0].lstrip("@").lower()

    give_premium(username)

    await update.message.reply_text(
        f"рџ‘‘ Premium РІС‹РґР°РЅ\n\n"
        f"РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ: @{username}\n"
        f"РЎРєРёРґРєР°: 20%"
    )

def create_order(username, stars, rub_amount, usdt_amount, wallet):
    order_id = str(uuid.uuid4())
    memo = str(uuid.uuid4())

    cur.execute(""" INSERT INTO orders ( order_id, username, stars, rub_amount, usdt_amount, memo, wallet, created_at ) VALUES (?, ?, ?, ?, ?, ?, ?, ?) """, (
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
    
def check_payment(memo, usdt_amount):
    url = "https://toncenter.com/api/v3/jetton/transfers"

    params = {
        "account": GRAM_WALLET,
        "limit": 30,
        "direction": "in"
    }

    headers = {"X-API-Key": TONCENTER_API}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
    except:
        return False

    for tx in data.get("jetton_transfers", []):
        comment = tx.get("comment", "")
        amount = int(tx.get("amount", 0)) / 1000000

        if comment == memo and abs(amount - usdt_amount) < 0.01:
            return True

    return False

async def cb(update,ctx):
    global STARS_OPEN, PREMIUM_OPEN
    q=update.callback_query
    d=q.data
    if d=="toggle_stars":
        STARS_OPEN=not STARS_OPEN
        kb=InlineKeyboardMarkup([[InlineKeyboardButton(f"в­ђ Stars: {'рџџў' if STARS_OPEN else 'рџ”ґ'}",callback_data="toggle_stars")],[InlineKeyboardButton(f"рџ‘‘ Premium: {'рџџў' if PREMIUM_OPEN else 'рџ”ґ'}",callback_data="toggle_premium")]])
        return await q.edit_message_text("вљ™пёЏ РђРґРјРёРЅ-РїР°РЅРµР»СЊ",reply_markup=kb)

    if d=="toggle_premium":
        PREMIUM_OPEN=not PREMIUM_OPEN
        kb=InlineKeyboardMarkup([[InlineKeyboardButton(f"в­ђ Stars: {'рџџў' if STARS_OPEN else 'рџ”ґ'}",callback_data="toggle_stars")],[InlineKeyboardButton(f"рџ‘‘ Premium: {'рџџў' if PREMIUM_OPEN else 'рџ”ґ'}",callback_data="toggle_premium")]])
        return await q.edit_message_text("вљ™пёЏ РђРґРјРёРЅ-РїР°РЅРµР»СЊ",reply_markup=kb)

    if d == "admin_users":
        cur.execute("SELECT COUNT(*) FROM premium")
        count = cur.fetchone()[0]
        return await q.message.reply_text(f"рџ‘¤ РџРѕР»СЊР·РѕРІР°С‚РµР»Рё\n\nР’СЃРµРіРѕ: {count}")
    if d == "admin_balances":
        return await q.message.reply_text("рџ’° Р Р°Р·РґРµР» Р±Р°Р»Р°РЅСЃРѕРІ РѕС‚РєСЂС‹С‚")
    if d == "admin_stars":
        return await q.message.reply_text("в­ђ Р Р°Р·РґРµР» Stars РѕС‚РєСЂС‹С‚")
    if d=="admin_rate":
        ctx.user_data["state"]="change_rate"
        return await q.message.reply_text(f"рџ’І РўРµРєСѓС‰РёР№ РєСѓСЂСЃ: {PRICE_PER_STAR}\n\nР’РІРµРґРёС‚Рµ РЅРѕРІС‹Р№ РєСѓСЂСЃ (РЅР°РїСЂРёРјРµСЂ 1.38)")
        
    if d=="home":
        return await q.edit_message_text("рџЏ  Р“Р»Р°РІРЅРѕРµ РјРµРЅСЋ\n\nРСЃРїРѕР»СЊР·СѓР№С‚Рµ РєРЅРѕРїРєРё СЃРЅРёР·Сѓ РґР»СЏ РІС‹Р±РѕСЂР° СЂР°Р·РґРµР»Р°.")

    if d=="back_profile": return await q.edit_message_text("рџ‘¤ Р—Р°РєСЂРѕР№С‚Рµ СЃРѕРѕР±С‰РµРЅРёРµ Рё РёСЃРїРѕР»СЊР·СѓР№С‚Рµ РјРµРЅСЋ СЃРЅРёР·Сѓ.")
    if d=="back_buy":
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("100 в­ђ",callback_data="s100"),InlineKeyboardButton("200 в­ђ",callback_data="s200")],
            [InlineKeyboardButton("300 в­ђ",callback_data="s300"),InlineKeyboardButton("400 в­ђ",callback_data="s400")],
            [InlineKeyboardButton("500 в­ђ",callback_data="s500"),InlineKeyboardButton("1000 в­ђ",callback_data="s1000")],
            [InlineKeyboardButton("вњЏпёЏ Р”СЂСѓРіРѕРµ РєРѕР»РёС‡РµСЃС‚РІРѕ",callback_data="custom")]
        ])
        return await q.edit_message_text("в­ђ Р’С‹Р±РµСЂРёС‚Рµ РєРѕР»РёС‡РµСЃС‚РІРѕ Stars:", reply_markup=kb)
    if d=="custom":
        ctx.user_data["state"]="custom_amount"
        return await q.edit_message_text("вњЏпёЏ Р’РІРµРґРёС‚Рµ РєРѕР»РёС‡РµСЃС‚РІРѕ Stars:")
    if d.startswith("s"):
        ctx.user_data["stars"]=int(d[1:])
        price=calc(ctx.user_data["stars"], q.from_user.username)
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("рџ’і РЎРџР‘",callback_data="pay_spb"),InlineKeyboardButton("рџ’Ћ РљСЂРёРїС‚РѕРІР°Р»СЋС‚Р°",callback_data="pay_crypto")],[InlineKeyboardButton("в—ЂпёЏ РќР°Р·Р°Рґ",callback_data="back_buy"),InlineKeyboardButton("рџЏ  РњРµРЅСЋ",callback_data="home")]])
        return await q.edit_message_text(f"рџ›’ РџРѕРґС‚РІРµСЂР¶РґРµРЅРёРµ\n\nРљРѕР»РёС‡РµСЃС‚РІРѕ: {ctx.user_data['stars']} в­ђ\nРЎС‚РѕРёРјРѕСЃС‚СЊ: {price} в‚Ѕ", reply_markup=kb)


    if d=="pay_crypto":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("рџЄ™ GRAM (TON)", callback_data="pay_grm")],
            [InlineKeyboardButton("рџ’µ USDT (TON)", callback_data="pay_usdt")],
            [InlineKeyboardButton("в—ЂпёЏ РќР°Р·Р°Рґ", callback_data="back_buy"),InlineKeyboardButton("рџЏ  РњРµРЅСЋ",callback_data="home")]
        ])
        return await q.edit_message_text(
            "рџ’Ћ РљСЂРёРїС‚РѕРІР°Р»СЋС‚Р°\n\nР’С‹Р±РµСЂРёС‚Рµ РІР°Р»СЋС‚Сѓ:",
            reply_markup=kb
        )

    if d=="pay_grm" or d=="pay_usdt":
        stars = ctx.user_data.get("stars")

        if not stars:
            return await q.edit_message_text("вќЊ РќРµ РІС‹Р±СЂР°РЅРѕ РєРѕР»РёС‡РµСЃС‚РІРѕ Stars.")

        rub_amount = calc(stars, q.from_user.username)
        usdt_amount = round(rub_amount / USDT_RATE, 2)

        wallet = GRAM_WALLET if d=="pay_grm" else USDT_WALLET
        order_id, memo = create_order(
            q.from_user.username or str(q.from_user.id),
            stars,
            rub_amount,
            usdt_amount,
            wallet
        )

        coin = "GRAM (TON)" if d=="pay_grm" else "USDT (TON)"

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("рџ”„ РџСЂРѕРІРµСЂРёС‚СЊ РѕРїР»Р°С‚Сѓ", callback_data=f"check_{order_id}")]
        ])

        await q.edit_message_text("вЏі РЎРѕР·РґР°СЋ СЃС‡С‘С‚...")
        return await q.edit_message_text(
            f"в­ђ РџРѕРєСѓРїРєР° Stars\n\n"
            f"рџЋЃ РўРѕРІР°СЂ: {stars} в­ђ\n"
            f"рџ’Ћ Р’Р°Р»СЋС‚Р°: {coin}\n\n"
            f"РЎСѓРјРјР°: {usdt_amount}\n\n"
            f"РљРѕС€РµР»С‘Рє:\n`{wallet}`\n\n"
            f"MEMO:\n`{memo}`",
            reply_markup=kb,
            parse_mode="Markdown"
        )

    if d in ["tg3","tg6","tg12"]:
        ctx.user_data["tg_months"] = {"tg3":"3 РјРµСЃСЏС†Р°","tg6":"6 РјРµСЃСЏС†РµРІ","tg12":"12 РјРµСЃСЏС†РµРІ"}[d]
        ctx.user_data["tg_price"] = {"tg3":999,"tg6":1299,"tg12":2299}[d]

        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("рџ’і РЎРџР‘", callback_data="tg_spb"),
             InlineKeyboardButton("рџ’Ћ РљСЂРёРїС‚РѕРІР°Р»СЋС‚Р°", callback_data="tg_crypto")],
            [InlineKeyboardButton("в—ЂпёЏ РќР°Р·Р°Рґ", callback_data="back_profile"),InlineKeyboardButton("рџЏ  РњРµРЅСЋ",callback_data="home")]
        ])

        return await q.edit_message_text(
            f"рџ‘‘ Telegram Premium\n\n{ctx.user_data['tg_months']}\nР¦РµРЅР°: {ctx.user_data['tg_price']} в‚Ѕ",
            reply_markup=kb
        )

    if d=="tg_spb":
        return await q.edit_message_text(
            f"рџ’і Telegram Premium\n\n{ctx.user_data['tg_months']}\nРљ РѕРїР»Р°С‚Рµ: {ctx.user_data['tg_price']} в‚Ѕ"
        )

    if d=="tg_crypto":
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("рџЄ™ GRAM (TON)", callback_data="tg_grm"),
             InlineKeyboardButton("рџ’µ USDT (TON)", callback_data="tg_usdt")]
        ])
        return await q.edit_message_text("рџ’Ћ РљСЂРёРїС‚РѕРІР°Р»СЋС‚Р°\n\nР’С‹Р±РµСЂРёС‚Рµ РІР°Р»СЋС‚Сѓ:", reply_markup=kb)

    if d=="tg_grm" or d=="tg_usdt":
        coin="GRAM (TON)" if d=="tg_grm" else "USDT (TON)"
        wallet = GRAM_WALLET if d=="tg_grm" else USDT_WALLET
        memo=str(uuid.uuid4())
        usdt=round(ctx.user_data["tg_price"]/USDT_RATE,2)
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("рџ”„ РџСЂРѕРІРµСЂРёС‚СЊ РѕРїР»Р°С‚Сѓ",callback_data="check_premium")],[InlineKeyboardButton("рџЏ  РњРµРЅСЋ",callback_data="home")]])
        await q.edit_message_text("вЏі РЎРѕР·РґР°СЋ СЃС‡С‘С‚...")
        return await q.edit_message_text(f"рџ‘‘ Telegram Premium\n\n{ctx.user_data['tg_months']}\nрџ’Ћ {coin}\n\nРЎСѓРјРјР°: {usdt}\n\nРљРѕС€РµР»С‘Рє:\n`{wallet}`\n\nMEMO:\n`{memo}`",reply_markup=kb,parse_mode="Markdown")

    if d.startswith("check_"):
        await q.answer()

    order_id = d.split("_", 1)[1]

    row = cur.execute(
        "SELECT memo, usdt_amount, stars, status FROM orders WHERE order_id=?",
        (order_id,)
    ).fetchone()

    if not row:
        return await q.answer("Р—Р°РєР°Р· РЅРµ РЅР°Р№РґРµРЅ", show_alert=True)

    memo, usdt, stars, status = row

    if status == "paid":
        return await q.answer("РЈР¶Рµ РѕРїР»Р°С‡РµРЅРѕ вњ…", show_alert=True)

    if check_payment(memo, usdt):
        cur.execute(
            "UPDATE orders SET status='paid', paid_at=? WHERE order_id=?",
            (int(time.time()), order_id)
        )
        db.commit()

        return await q.edit_message_text(
            f"вњ… РћРїР»Р°С‚Р° РїРѕРґС‚РІРµСЂР¶РґРµРЅР°!\n\nР’С‹РґР°РЅРѕ: {stars} в­ђ"
        )

    return await q.answer("РћРїР»Р°С‚Р° РµС‰С‘ РЅРµ РЅР°Р№РґРµРЅР°", show_alert=True)

    if d=="premium":
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("рџ’і РЎРџР‘", callback_data="prem_spb"),
                InlineKeyboardButton("рџ’Ћ РљСЂРёРїС‚РѕРІР°Р»СЋС‚Р°", callback_data="prem_crypto")
            ],
            [InlineKeyboardButton("в—ЂпёЏ РќР°Р·Р°Рґ", callback_data="back_profile"),InlineKeyboardButton("рџЏ  РњРµРЅСЋ",callback_data="home")]
        ])
        return await q.edit_message_text(
            "рџ‘‘ Premium StarsGo\n\nРџРѕРґРїРёСЃРєР°: 1 РјРµСЃСЏС†\nРЎРєРёРґРєР°: 20%\n\nР’С‹Р±РµСЂРёС‚Рµ СЃРїРѕСЃРѕР± РѕРїР»Р°С‚С‹:",
            reply_markup=kb
        )
    if d=="prem_spb": return await q.edit_message_text("вљ пёЏ РЎРїРѕСЃРѕР± РѕРїР»Р°С‚С‹ РІСЂРµРјРµРЅРЅРѕ РЅРµРґРѕСЃС‚СѓРїРµРЅ")
    if d=="prem_crypto":
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("рџЄ™ GRAM (TON)",callback_data="prem_grm")],
            [InlineKeyboardButton("рџ’µ USDT (TON)",callback_data="prem_usdt")],
            [InlineKeyboardButton("в—ЂпёЏ РќР°Р·Р°Рґ",callback_data="premium")]
        ])
        return await q.edit_message_text("рџ’Ћ РљСЂРёРїС‚РѕРІР°Р»СЋС‚Р°\n\nР’С‹Р±РµСЂРёС‚Рµ РІР°Р»СЋС‚Сѓ:",reply_markup=kb)



    if d=="prem_grm" or d=="prem_usdt":
        coin="GRAM (TON)" if d=="prem_grm" else "USDT (TON)"
        wallet=GRAM_WALLET if d=="prem_grm" else USDT_WALLET
        memo=str(uuid.uuid4())
        usdt=round(999/USDT_RATE,2)
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("рџ”„ РџСЂРѕРІРµСЂРёС‚СЊ РѕРїР»Р°С‚Сѓ",callback_data="check_premium")]])
        await q.edit_message_text("вЏі РЎРѕР·РґР°СЋ СЃС‡С‘С‚...")
        await __import__("asyncio").sleep(1)
        return await q.edit_message_text(
            f"рџ‘‘ Premium StarsGo\n\nрџ’Ћ {coin}\nРЎСѓРјРјР°: {usdt}\n\nРљРѕС€РµР»С‘Рє:\n`{wallet}`\n\nMEMO:\n`{memo}`",
            reply_markup=kb,parse_mode="Markdown")

    if d=="pay_spb":
        return await q.edit_message_text("вљ пёЏ РЎРїРѕСЃРѕР± РѕРїР»Р°С‚С‹ РІСЂРµРјРµРЅРЅРѕ РЅРµРґРѕСЃС‚СѓРїРµРЅ")
async def cmd_premium(update,ctx):
    if update.effective_user.username!=ADMIN: return
    p=update.message.text.split()
    if len(p)!=2: return await update.message.reply_text("РСЃРїРѕР»СЊР·СѓР№: /premium @user")
    give_premium(p[1].replace("@","")); await update.message.reply_text("рџ‘‘ Premium РІС‹РґР°РЅ")
async def cmd_unpremium(update,ctx):
    if update.effective_user.username!=ADMIN: return
    p=update.message.text.split()
    if len(p)!=2: return await update.message.reply_text("РСЃРїРѕР»СЊР·СѓР№: /unpremium @user")
    remove_premium(p[1].replace("@","")); await update.message.reply_text("вќЊ Premium СЃРЅСЏС‚")
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN:
        return

    keyboard = [
        [InlineKeyboardButton("рџ‘¤ РџРѕР»СЊР·РѕРІР°С‚РµР»Рё", callback_data="admin_users")],
        [InlineKeyboardButton("рџ’° Р‘Р°Р»Р°РЅСЃС‹", callback_data="admin_balances")],
        [InlineKeyboardButton("в­ђ Stars", callback_data="admin_stars")],
        [InlineKeyboardButton("рџ’І РР·РјРµРЅРёС‚СЊ РєСѓСЂСЃ", callback_data="admin_rate")],
        [InlineKeyboardButton("вћ• Р’С‹РґР°С‚СЊ Р±Р°Р»Р°РЅСЃ", callback_data="admin_give")],
        [InlineKeyboardButton("вћ– РЎРЅСЏС‚СЊ Р±Р°Р»Р°РЅСЃ", callback_data="admin_take")],
        [InlineKeyboardButton("рџљ« Р‘Р»РѕРєРёСЂРѕРІРєР°", callback_data="admin_block")],
        [InlineKeyboardButton("рџЋЃ РџСЂРѕРјРѕРєРѕРґС‹", callback_data="admin_promo")],
        [InlineKeyboardButton("рџ“Љ РЎС‚Р°С‚РёСЃС‚РёРєР°", callback_data="admin_stats")],
        [InlineKeyboardButton("рџ“ў Р Р°СЃСЃС‹Р»РєР°", callback_data="admin_broadcast")],
        [InlineKeyboardButton("рџ“ќ Р›РѕРіРё", callback_data="admin_logs")],
    ]

    await update.message.reply_text(
        "вљ™пёЏ РђРґРјРёРЅ-РїР°РЅРµР»СЊ StarsGo",
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
app.run_polling(drop_pending_updates=True)
