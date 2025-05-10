import aiosqlite
import asyncio

async def create_user():
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, balance, last_bonus, referred_by) VALUES (?, ?, ?, ?)",
            (999999, 1.2345, 0, None)
        )
        await db.commit()
        print("Utente di test inserito")

asyncio.run(create_user())
