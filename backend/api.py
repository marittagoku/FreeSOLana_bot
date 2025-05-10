from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

# Abilita CORS da qualunque origine (necessario per chiamate fetch dal frontend Surge)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "freesolana.db"

def get_user_balance(user_id: int):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"Errore nel recupero del bilancio: {e}")
        return None

@app.get("/balance/{user_id}")
def balance(user_id: int):
    bal = get_user_balance(user_id)
    if bal is None:
        return {"error": "Utente non trovato"}
    return {"balance": bal}
