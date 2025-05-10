require('dotenv').config();
const express = require('express');
const cors = require('cors');
const Database = require('better-sqlite3');
const axios = require('axios');

const app = express();
app.use(cors());
app.use(express.json());

const db = new Database(process.env.DB_PATH || 'database.db');
const MIN_WITHDRAW_EUR = 100;
const COINGECKO_URL = 'https://api.coingecko.com/api/v3/simple/price';

// Creazione tabelle
db.prepare(`
  CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0.0,
    last_bonus INTEGER DEFAULT 0,
    referred_by INTEGER
  )
`).run();

db.prepare(`
  CREATE TABLE IF NOT EXISTS withdrawals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    timestamp INTEGER
  )
`).run();

// Prezzo in tempo reale
async function getSolPriceEur() {
  const resp = await axios.get(COINGECKO_URL, {
    params: { ids: 'solana', vs_currencies: 'eur' }
  });
  return resp.data.solana.eur || 0;
}

// Middleware utente fittizio (mock)
app.use((req, res, next) => {
  req.user_id = 12345;
  next();
});

app.get('/api/balance', async (req, res) => {
  const row = db.prepare('SELECT balance FROM users WHERE user_id = ?').get(req.user_id);
  const balance = row ? row.balance : 0;
  const price = await getSolPriceEur();
  res.json({ balance, price, eurValue: balance * price });
});

app.post('/api/bonus', async (req, res) => {
  const now = Math.floor(Date.now() / 1000);
  let user = db.prepare('SELECT balance, last_bonus FROM users WHERE user_id = ?').get(req.user_id);
  if (!user) {
    db.prepare(`INSERT INTO users (user_id, balance, last_bonus) VALUES (?, ?, ?)`)
      .run(req.user_id, 0, 0);
    user = { balance: 0, last_bonus: 0 };
  }
  if (now - user.last_bonus < 1800) {
    return res.status(429).json({ error: '⏳ Attendi 30 minuti prima del prossimo bonus.' });
  }
  const bonus = 0.01;
  const newBal = user.balance + bonus;
  db.prepare('UPDATE users SET balance = ?, last_bonus = ? WHERE user_id = ?')
    .run(newBal, now, req.user_id);
  const price = await getSolPriceEur();
  res.json({ balance: newBal, eurValue: newBal * price, price });
});

app.get('/api/referral', (req, res) => {
  const link = `${process.env.BASE_URL || 'http://localhost:3000'}/?ref=${req.user_id}`;
  res.json({ link });
});

app.post('/api/withdraw', async (req, res) => {
  const user = db.prepare('SELECT balance FROM users WHERE user_id = ?').get(req.user_id) || { balance: 0 };
  const price = await getSolPriceEur();
  const minSol = MIN_WITHDRAW_EUR / price;
  if (user.balance < minSol) {
    return res.status(400).json({
      error: `⚠️ Minimo prelievo: ${MIN_WITHDRAW_EUR}€ (~${minSol.toFixed(4)} SOL). Hai ${user.balance.toFixed(4)} SOL.`
    });
  }
  const commission = user.balance * 0.1;
  const net = user.balance - commission;
  db.prepare('UPDATE users SET balance = 0 WHERE user_id = ?').run(req.user_id);
  db.prepare('INSERT INTO withdrawals (user_id, amount, timestamp) VALUES (?, ?, ?)').run(req.user_id, net, Math.floor(Date.now() / 1000));
  res.json({ gross: user.balance, commission, net, price });
});

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`✅ Backend avviato su http://localhost:${PORT}`));
