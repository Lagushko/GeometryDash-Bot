import sqlite3
import json

class UserDatabase:
    def __init__(self, db_name="data/users.db"):
        self.db_name = db_name
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    stars INTEGER DEFAULT 0,
                    diamonds INTEGER DEFAULT 0,
                    goldcoins INTEGER DEFAULT 0,
                    usercoins INTEGER DEFAULT 0,
                    demons INTEGER DEFAULT 0,
                    creatorpoints INTEGER DEFAULT 0,
                    orbs INTEGER DEFAULT 0,
                    played TEXT DEFAULT '{}',
                    icons TEXT DEFAULT "[0,0,0,0,0,0,0]",
                    last_send_time INTEGER DEFAULT 0,
                    last_reward_time INTEGER DEFAULT 0,
                    notification TEXT DEFAULT "",
                    hardest TEXT DEFAULT '[1,1]',
                    purchased TEXT DEFAULT "[]",
                    visuals TEXT DEFAULT "[0,0]",
                    creations TEXT DEFAULT "[]"
                )
            """)
            conn.commit()

    def ensure(self, user_id: int):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
                conn.commit()

    def get(self, user_id: int):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "user_id": row[0],
                    "stars": row[1],
                    "diamonds": row[2],
                    "goldcoins": row[3],
                    "usercoins": row[4],
                    "demons": row[5],
                    "creatorpoints": row[6],
                    "orbs": row[7],
                    "played": json.loads(row[8]) if row[8] else {},
                    "icons": json.loads(row[9]) if row[9] else [],
                    "last_send_time": row[10],
                    "last_reward_time": row[11],
                    "notification": row[12],
                    "hardest": json.loads(row[13]) if row[13] else [],
                    "purchased": json.loads(row[14]) if row[14] else [],
                    "visuals": json.loads(row[15]) if row[15] else [],
                    "creations": json.loads(row[16]) if row[16] else []
                }
            return None

    def update_field(self, user_id: int, field: str, value):
        if field in ["played", "icons", "hardest", "purchased", "visuals", "creations"]:
            value = json.dumps(value)
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
            conn.commit()

class LevelDatabase:
    def __init__(self, db_name="data/levels.db"):
        self.db_name = db_name
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS levels (
                    level_id INTEGER PRIMARY KEY,
                    name TEXT,
                    difficulty INTEGER,
                    downloads INTEGER,
                    likes INTEGER,
                    time INTEGER,
                    coins INTEGER,
                    sender INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def add(self, level_id: int, name: str, difficulty: int, downloads: int, likes: int, time: int, coins: int, sender: int):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO levels (level_id, name, difficulty, downloads, likes, time, coins, sender)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (level_id, name, difficulty, downloads, likes, time, coins, sender))
            conn.commit()

    def get(self, level_id: int):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM levels WHERE level_id = ?", (level_id,))
            row = cursor.fetchone()
            if row:
                return {
                    "level_id": row[0],
                    "name": row[1],
                    "difficulty": row[2],
                    "downloads": row[3],
                    "likes": row[4],
                    "time": row[5],
                    "coins": row[6],
                    "sender": row[7]
                }
            return None

    def update_field(self, level_id: int, field: str, value):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"UPDATE levels SET {field} = ? WHERE level_id = ?", (value, level_id))
            conn.commit()

class BotDatabase:
    def __init__(self, db_name="data/settings.db"):
        self.db_name = db_name
        self._create_table()

    def _connect(self):
        return sqlite3.connect(self.db_name)

    def _create_table(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    setting_name TEXT PRIMARY KEY,
                    setting_value TEXT
                )
            """)
            conn.commit()

    def add(self, setting_name: str, default_value):
        if self.get(setting_name) is None:
            self.update_field(setting_name, default_value)

    def get(self, setting_name: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = ?", (setting_name,))
            row = cursor.fetchone()
            if not row:
                return None
            value = row[0]
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value

    def update_field(self, setting_name: str, new_value):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (setting_name, setting_value)
                VALUES (?, ?)
                ON CONFLICT(setting_name) DO UPDATE SET setting_value = excluded.setting_value
            """, (setting_name, json.dumps(new_value)))
            conn.commit()

    def get_raw(self, setting_name: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM settings WHERE setting_name = ?", (setting_name,))
            row = cursor.fetchone()
            return row[0] if row else None

    def delete(self, setting_name: str):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM settings WHERE setting_name = ?", (setting_name,))
            conn.commit()

userDB = UserDatabase()
levelDB = LevelDatabase()
botDB = BotDatabase()