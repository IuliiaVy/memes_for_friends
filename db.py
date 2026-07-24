import aiosqlite
import datetime

DB_NAME = 'sheriff.db'

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                free_checks_used INTEGER DEFAULT 0,
                last_check_date TEXT,
                stars_balance INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT free_checks_used, last_check_date, stars_balance FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"free_checks_used": row[0], "last_check_date": row[1], "stars_balance": row[2]}
            return None

async def add_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id, free_checks_used, last_check_date, stars_balance) VALUES (?, 0, "", 0)', (user_id,))
        await db.commit()

async def get_or_create_user(user_id: int):
    user = await get_user(user_id)
    if not user:
        await add_user(user_id)
        user = await get_user(user_id)
    
    # Check if we need to reset daily free checks
    today = datetime.date.today().isoformat()
    if user['last_check_date'] != today:
        async with aiosqlite.connect(DB_NAME) as db:
            await db.execute('UPDATE users SET free_checks_used = 0, last_check_date = ? WHERE user_id = ?', (today, user_id))
            await db.commit()
        user['free_checks_used'] = 0
        user['last_check_date'] = today
        
    return user

async def use_free_check(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET free_checks_used = free_checks_used + 1 WHERE user_id = ?', (user_id,))
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
