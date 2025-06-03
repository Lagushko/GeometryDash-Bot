import sqlite3
import json

conn = sqlite3.connect("data/users.db")
cursor = conn.cursor()

cursor.execute("SELECT user_id FROM users")
user_ids = [row[0] for row in cursor.fetchall()]

for user_id in user_ids:
    new_value = json.dumps([0, 0])
    cursor.execute(
        "UPDATE users SET last_reward_time = ? WHERE user_id = ?",
        (new_value, user_id)
    )

conn.commit()
conn.close()

print("Done")
