# backend/api.py

import os
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Carica variabili da .env
load_dotenv()
DB_PATH = os.getenv("DB_PATH", "database.db")

app = FastAPI()

# Abilitiamo il CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

def init_db():
    """Crea tabella users e inserisce utente di test."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Crea tabella
    cur.execute("""
      CREATE TABLE IF NOT EXISTS users (
        user_id    INTEGER PRIMARY KEY,
        balance    REAL DEFAULT 0,
        last_bonus INTEGER,
        last_mine  INTEGER
      )
    """)
    # Inserisci utente di test con ID fisso e balance 100 se non esiste
    TEST_ID = 867950891
    cur.execute("""
      INSERT OR IGNORE INTO users (user_id, balance, last_bonus, last_mine)
      VALUES (?, ?, strftime('%s','now'), strftime('%s','now'))
    """, (TEST_ID, 100.0))
    conn.commit()
    conn.close()

def get_user_balance(user_id: int):
    """Ritorna float balance o None."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None

# All’avvio, inizializza il DB
init_db()

@app.get("/balance/{user_id}")
def balance(user_id: int):
    bal = get_user_balance(user_id)
    if bal is None:
        return {"error": "Utente non trovato"}
    return {"balance": bal}
