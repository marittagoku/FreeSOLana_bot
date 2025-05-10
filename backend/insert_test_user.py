# insert_test_user.py

import sqlite3

conn = sqlite3.connect("freesolana.db")
cursor = conn.cursor()

user_id = 867950891
starting_balance = 100.0

cursor.execute("INSERT OR IGNORE INTO users (user_id, balance, last_bonus_time, referral_count, referred_by) VALUES (?, ?, datetime('now'), 0, NULL)", (user_id, starting_balance))
conn.commit()
conn.close()

print("✅ Utente inserito con successo!")
