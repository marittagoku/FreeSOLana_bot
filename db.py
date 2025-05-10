import sqlite3
import time

DB_PATH = "database.db"

def init_db():
    """Crea (o ricrea) le tabelle con le nuove colonne."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Tabella utenti
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            first_name  TEXT,
            balance     REAL DEFAULT 0,
            last_mine   INTEGER,
            last_bonus  INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id: int, first_name: str):
    """Registra utente: imposta balance=0.1 e timestamps a ora."""
    now = int(time.time())
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO users (user_id, first_name, balance, last_mine, last_bonus)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, first_name, 0.1, now, now - 1800))
    # se c’è già, non tocca nulla
    conn.commit()
    conn.close()

def get_user(user_id: int):
    """Restituisce il record utente come dict, o None."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, first_name, balance, last_mine, last_bonus FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "user_id": row[0],
        "first_name": row[1],
        "balance": row[2],
        "last_mine": row[3],
        "last_bonus": row[4]
    }

def update_user_field(user_id: int, field: str, value):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()
