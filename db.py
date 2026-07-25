import aiosqlite
import datetime

DB_NAME = 'sheriff.db'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                free_checks_used INTEGER DEFAULT 0,
                free_roasts_used INTEGER DEFAULT 0,
                free_brigada_used INTEGER DEFAULT 0,
                free_vibe_used INTEGER DEFAULT 0,
                last_check_date TEXT,
                stars_balance INTEGER DEFAULT 0
            )
        ''')
        # Добавим колонки для старых БД, если их не было
        for col in ['free_roasts_used', 'free_brigada_used', 'free_vibe_used']:
            try:
                await db.execute(f'ALTER TABLE users ADD COLUMN {col} INTEGER DEFAULT 0')
            except Exception:
                pass
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT free_roasts_used, free_brigada_used, free_vibe_used, last_check_date, stars_balance FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "free_roasts_used": row[0] or 0,
                    "free_brigada_used": row[1] or 0,
                    "free_vibe_used": row[2] or 0,
                    "last_check_date": row[3],
                    "stars_balance": row[4] or 0
                }
            return None

async def add_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id, free_roasts_used, free_brigada_used, free_vibe_used, last_check_date, stars_balance) VALUES (?, 0, 0, 0, "", 0)', (user_id,))
        await db.commit()

async def get_or_create_user(user_id: int):
    user = await get_user(user_id)
    if not user:
        await add_user(user_id)
        user = await get_user(user_id)
    
    today = datetime.date.today().isoformat()
    if user['last_check_date'] != today:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('UPDATE users SET free_roasts_used = 0, free_brigada_used = 0, free_vibe_used = 0, last_check_date = ? WHERE user_id = ?', (today, user_id))
            await db.commit()
        user['free_roasts_used'] = 0
        user['free_brigada_used'] = 0
        user['free_vibe_used'] = 0
        user['last_check_date'] = today
        
    return user

async def use_free_action(user_id: int, action_type: str):
    col = f"free_{action_type}_used"
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(f'UPDATE users SET {col} = {col} + 1 WHERE user_id = ?', (user_id,))
        await db.commit()

async def use_star(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET stars_balance = stars_balance - 1 WHERE user_id = ?', (user_id,))
        await db.commit()

async def add_stars(user_id: int, amount: int):
    await get_or_create_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET stars_balance = stars_balance + ? WHERE user_id = ?', (amount, user_id))
        await db.commit()

