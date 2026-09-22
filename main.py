# StarsGo V3 (skeleton)
# Features: Premium, Admin panel, History, Promo, Referrals, Platega hooks
# Replace BOT_TOKEN in Railway Variables.
from telegram import *
from telegram.ext import *
import sqlite3, os

TOKEN=os.getenv("BOT_TOKEN")
ADMIN="Lakizyx"
PRICE=1.38
db=sqlite3.connect("starsgo.db",check_same_thread=False)
c=db.cursor()
c.executescript("""
CREATE TABLE IF NOT EXISTS premium(username TEXT PRIMARY KEY);
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, ref TEXT);
CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, stars INT, price INT, status TEXT);
CREATE TABLE IF NOT EXISTS promos(code TEXT PRIMARY KEY, discount INT);
""")
db.commit()

# TODO: Full handlers
# /admin -> 👑 Premium ❌ Remove 📈 Rate 📦 Orders 💰 Stats 📢 Broadcast
# /premium @user
# /unpremium @user
# Buy Stars + Platega webhook
print("StarsGo V3 scaffold")
