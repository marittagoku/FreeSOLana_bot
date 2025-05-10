import sqlite3
import sys
import time

if len(sys.argv) < 2:
    print("❌ Usa: python insert_user.py <user_id>")
    exit()

user_id = int(sys.argv[1])
conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("INSERT OR IGNORE INTO users (id, balance, last_bonus, last_open, referrals, withdraw_history) VALUES (?, ?, ?, ?, '', '')", (user_id, 0.0, 0, int(time.time())))
conn.commit()
conn.close()
print(f"✅ Utente {user_id} inserito/già esistente.")
