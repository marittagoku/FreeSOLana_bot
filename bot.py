import os
import logging
import requests
from dotenv import load_dotenv
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Configurazione logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv()
TOKEN      = os.getenv("BOT_TOKEN")
API_BASE   = os.getenv("API_BASE")
WEBAPP_URL = os.getenv("WEBAPP_URL")

# /start: mostra i pulsanti principali
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("💰 Saldo", callback_data="balance"),
            InlineKeyboardButton("🎁 Bonus", callback_data="bonus"),
        ],
        [
            InlineKeyboardButton("👥 Referral", callback_data="referrals"),
            InlineKeyboardButton("💸 Prelievo", callback_data="withdraw"),
        ],
        [
            InlineKeyboardButton(
                "🌐 Apri MiniApp",
                web_app=WebAppInfo(f"{WEBAPP_URL}?id={user.id}")
            )
        ]
    ]
    await update.message.reply_text(
        f"👋 Ciao, *{user.first_name}*!\nScegli un’opzione:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN,
    )

# Gestione CallbackQuery
async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    uid  = q.from_user.id
    data = q.data
    await q.answer()

    try:
        if data == "balance":
            r = requests.get(f"{API_BASE}/balance/{uid}").json()
            await q.message.reply_text(f"💰 Saldo: {r['balance']:.2f} €")

        elif data == "bonus":
            r = requests.post(f"{API_BASE}/bonus/{uid}")
            if r.status_code == 200:
                bonus = r.json()["bonus"]
                await q.message.reply_text(f"🎁 Bonus ricevuto: {bonus} €")
            else:
                await q.message.reply_text(f"⚠️ {r.json().get('detail', r.text)}")

        elif data == "referrals":
            r = requests.get(f"{API_BASE}/referrals/{uid}").json()
            invites = r["invitees"]
            valid   = r["valid_referrals"]
            text = (
                f"👥 Invitati totali: {len(invites)}\n"
                f"✅ Invitati validi: {valid}\n"
                "Lista invitati:\n" +
                ("\n".join(str(i) for i in invites) if invites else "_nessuno ancora_")
            )
            await q.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

        elif data == "withdraw":
            # apri la WebApp per l'input importo
            await q.message.reply_text(
                "➔ Clicca *Apri MiniApp* per inserire importo e confermare prelievo.",
                parse_mode=ParseMode.MARKDOWN,
            )

    except Exception as e:
        logging.error(e)
        await q.message.reply_text("❌ Si è verificato un errore. Riprova.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))

    logging.info("🤖 Bot avviato…")
    app.run_polling()

if __name__ == "__main__":
    main()
