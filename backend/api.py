# backend/api.py

import os
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Carica variabili da .env
load_dotenv()
DB_PATH = os.getenv("DB_PATH", "database.db")  # di default 'database.db'

app = FastAPI()

# Abilitiamo il CORS per tutte le origini (in produzione specifica solo la tua MiniApp)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

def get_user_balance(user_id: int):
    """Restituisce il balance da SQLite, o None se non esiste."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None
    except Exception as e:
        print(f"Errore recupero bilancio: {e}")
        return None
    finally:
        conn.close()

@app.get("/balance/{user_id}")
def balance(user_id: int):
    bal = get_user_balance(user_id)
    if bal is None:
        # Se non trovi l'utente, ritorniamo 404 o un errore strutturato
        return {"error": "Utente non trovato"}
    return {"balance": bal}
