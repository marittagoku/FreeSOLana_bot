import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0,
    last_bonus INTEGER DEFAULT 0,
    last_open INTEGER DEFAULT 0,
    referrals TEXT DEFAULT ''
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    fee REAL,
    address TEXT,
    timestamp INTEGER DEFAULT (strftime('%s','now'))
)
""")

conn.commit()
conn.close()
print("✅ Database inizializzato correttamente.")
