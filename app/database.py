"""SQLite orqali har bir guruh uchun sozlamalarni saqlash."""
import aiosqlite
from app.config import DB_PATH

_db: aiosqlite.Connection | None = None


async def init_db():
    global _db
    _db = await aiosqlite.connect(DB_PATH)
    await _db.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            chat_id INTEGER PRIMARY KEY,
            required_channel TEXT,
            filter_swear INTEGER NOT NULL DEFAULT 1,
            filter_links INTEGER NOT NULL DEFAULT 1,
            filter_ads INTEGER NOT NULL DEFAULT 1,
            block_bots INTEGER NOT NULL DEFAULT 1,
            require_subscribe INTEGER NOT NULL DEFAULT 1,
            filter_phone INTEGER NOT NULL DEFAULT 1
        )
        """
    )
    # Eski (allaqachon yaratilgan) bazalarga yangi ustunni qo'shib qo'yamiz -
    # CREATE TABLE IF NOT EXISTS mavjud jadvalga yangi ustun qo'shmaydi.
    try:
        await _db.execute("ALTER TABLE chats ADD COLUMN filter_phone INTEGER NOT NULL DEFAULT 1")
    except Exception:
        pass  # ustun allaqachon mavjud
    await _db.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            chat_id INTEGER,
            user_id INTEGER,
            PRIMARY KEY (chat_id, user_id)
        )
        """
    )
    await _db.execute(
        """
        CREATE TABLE IF NOT EXISTS bot_allowlist (
            chat_id INTEGER,
            bot_id INTEGER,
            PRIMARY KEY (chat_id, bot_id)
        )
        """
    )
    await _db.execute(
        """
        CREATE TABLE IF NOT EXISTS custom_words (
            chat_id INTEGER,
            word TEXT,
            PRIMARY KEY (chat_id, word)
        )
        """
    )
    await _db.commit()


def db() -> aiosqlite.Connection:
    assert _db is not None, "DB hali init qilinmagan"
    return _db


async def ensure_chat(chat_id: int):
    await db().execute(
        "INSERT OR IGNORE INTO chats (chat_id, required_channel) VALUES (?, ?)",
        (chat_id, None),
    )
    await db().commit()


async def get_chat_settings(chat_id: int) -> dict:
    await ensure_chat(chat_id)
    cur = await db().execute(
        "SELECT required_channel, filter_swear, filter_links, filter_ads, block_bots, require_subscribe, filter_phone "
        "FROM chats WHERE chat_id = ?",
        (chat_id,),
    )
    row = await cur.fetchone()
    return {
        "required_channel": row[0],
        "filter_swear": bool(row[1]),
        "filter_links": bool(row[2]),
        "filter_ads": bool(row[3]),
        "block_bots": bool(row[4]),
        "require_subscribe": bool(row[5]),
        "filter_phone": bool(row[6]),
    }


async def set_required_channel(chat_id: int, channel: str | None):
    await ensure_chat(chat_id)
    await db().execute(
        "UPDATE chats SET required_channel = ? WHERE chat_id = ?", (channel, chat_id)
    )
    await db().commit()


async def toggle_setting(chat_id: int, field: str, value: bool):
    assert field in {"filter_swear", "filter_links", "filter_ads", "block_bots", "require_subscribe", "filter_phone"}
    await ensure_chat(chat_id)
    await db().execute(
        f"UPDATE chats SET {field} = ? WHERE chat_id = ?", (int(value), chat_id)
    )
    await db().commit()


async def add_admin(chat_id: int, user_id: int):
    await db().execute(
        "INSERT OR IGNORE INTO admins (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id)
    )
    await db().commit()


async def is_bot_admin_managed(chat_id: int, user_id: int) -> bool:
    cur = await db().execute(
        "SELECT 1 FROM admins WHERE chat_id = ? AND user_id = ?", (chat_id, user_id)
    )
    return await cur.fetchone() is not None


async def allow_bot(chat_id: int, bot_id: int):
    await db().execute(
        "INSERT OR IGNORE INTO bot_allowlist (chat_id, bot_id) VALUES (?, ?)", (chat_id, bot_id)
    )
    await db().commit()


async def is_bot_allowed(chat_id: int, bot_id: int) -> bool:
    cur = await db().execute(
        "SELECT 1 FROM bot_allowlist WHERE chat_id = ? AND bot_id = ?", (chat_id, bot_id)
    )
    return await cur.fetchone() is not None


async def add_custom_word(chat_id: int, word: str):
    await db().execute(
        "INSERT OR IGNORE INTO custom_words (chat_id, word) VALUES (?, ?)",
        (chat_id, word.lower().strip()),
    )
    await db().commit()


async def remove_custom_word(chat_id: int, word: str):
    await db().execute(
        "DELETE FROM custom_words WHERE chat_id = ? AND word = ?",
        (chat_id, word.lower().strip()),
    )
    await db().commit()


async def get_custom_words(chat_id: int) -> list[str]:
    cur = await db().execute(
        "SELECT word FROM custom_words WHERE chat_id = ?", (chat_id,)
    )
    rows = await cur.fetchall()
    return [r[0] for r in rows]
