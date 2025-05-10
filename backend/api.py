# backend/api.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import sqlite3
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "database.db"
BONUS_AMOUNT = 5
BONUS_INTERVAL_MINUTES = 30
INCOME_INTERVAL_MINUTES = 15
INCOME_PER_INTERVAL = 1
WITHDRAW_MIN_REFERRALS = 10
WITHDRAW_MIN_AMOUNT = 100

class WithdrawRequest(BaseModel):
    user_id: int
    amount: float

class ReferralRequest(BaseModel):
    user_id: int
    referral_id: int

@app.post("/add_user/{user_id}")
async def add_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().timestamp()
    cur.execute(
        "INSERT OR IGNORE INTO users (id, balance, last_bonus, last_open) VALUES (?, 0, 0, ?)",
        (user_id, now),
    )
    conn.commit()
    conn.close()
    return {"added": user_id}

@app.get("/balance/{user_id}")
async def get_balance(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT balance, last_open FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    balance, last_open = row
    now = datetime.utcnow().timestamp()
    minutes_passed = int((now - last_open) // 60)
    intervals = minutes_passed // INCOME_INTERVAL_MINUTES
    extra_income = intervals * INCOME_PER_INTERVAL

    if extra_income > 0:
        balance += extra_income
        cur.execute(
            "UPDATE users SET balance = ?, last_open = ? WHERE id = ?",
            (balance, now, user_id),
        )
        conn.commit()

    conn.close()
    return {"balance": round(balance, 2)}

@app.post("/bonus/{user_id}")
async def post_bonus(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().timestamp()

    cur.execute("SELECT balance, last_bonus FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    balance, last_bonus = row
    if now - last_bonus < BONUS_INTERVAL_MINUTES * 60:
        raise HTTPException(status_code=400, detail="⏳ Attendi 30 minuti prima del prossimo bonus.")

    balance += BONUS_AMOUNT
    cur.execute(
        "UPDATE users SET balance = ?, last_bonus = ? WHERE id = ?",
        (balance, now, user_id),
    )
    conn.commit()
    conn.close()
    return {"bonus": BONUS_AMOUNT}

@app.post("/add_referral")
async def add_referral(req: ReferralRequest):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE id = ?", (req.referral_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Referral non trovato")

    cur.execute(
        "INSERT OR IGNORE INTO referrals (user_id, referral_id) VALUES (?, ?)",
        (req.user_id, req.referral_id),
    )
    conn.commit()
    conn.close()
    return {"added": req.referral_id}

@app.get("/referrals/{user_id}")
async def get_referrals(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT referral_id FROM referrals WHERE user_id = ?", (user_id,)
    )
    invitees = [row[0] for row in cur.fetchall()]
    valid_referrals = 0
    for rid in invitees:
        cur.execute("SELECT balance FROM users WHERE id = ?", (rid,))
        rrow = cur.fetchone()
        if rrow and rrow[0] >= BONUS_AMOUNT:
            valid_referrals += 1

    conn.close()
    return {"invitees": invitees, "valid_referrals": valid_referrals}

@app.post("/withdraw")
async def post_withdraw(req: WithdrawRequest):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT balance FROM users WHERE id = ?", (req.user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Utente non trovato")

    balance = row[0]

    cur.execute("SELECT referral_id FROM referrals WHERE user_id = ?", (req.user_id,))
    invitees = [row[0] for row in cur.fetchall()]
    valid = 0
    for rid in invitees:
        cur.execute("SELECT balance FROM users WHERE id = ?", (rid,))
        rrow = cur.fetchone()
        if rrow and rrow[0] >= BONUS_AMOUNT:
            valid += 1
    if valid < WITHDRAW_MIN_REFERRALS:
        raise HTTPException(status_code=400, detail="Ti servono 10 referral validi per prelevare")

    if req.amount < WITHDRAW_MIN_AMOUNT:
        raise HTTPException(status_code=400, detail="Importo minimo per il prelievo: 100€")

    fee = req.amount * 0.10
    if balance < req.amount + fee:
        raise HTTPException(status_code=400, detail="Saldo insufficiente per la fee")

    cur.execute(
        "UPDATE users SET balance = balance - ? WHERE id = ?",
        (req.amount + fee, req.user_id),
    )
    conn.commit()
    conn.close()
    return {
        "withdraw": round(req.amount, 2),
        "fee": round(fee, 2),
        "address": "28PcebiAMStX..."  # Placeholder
    }
