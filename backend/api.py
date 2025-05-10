from fastapi import FastAPI
import sqlite3

app = FastAPI()

DB_NAME = "freesolana.db"

def get_user_balance(user_id: int):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return None
    except Exception as e:
        print(f"Errore nel recupero del bilancio: {e}")
        return None

@app.get("/balance/{user_id}")
def balance(user_id: int):
    balance = get_user_balance(user_id)
    if balance is None:
        return {"error": "Utente non trovato"}
    return {"balance": balance}
