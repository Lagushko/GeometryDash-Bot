import sqlite3
from database import userDB

LEVELS_DB_PATH = "data/levels.db"

with sqlite3.connect(LEVELS_DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute("SELECT level_id, sender FROM levels")
    rows = cur.fetchall()

for level_id, sender in rows:
    sender_id = int(sender)

    userDB.ensure(sender_id)
    user_data = userDB.get(sender_id)

    creations = user_data.get("creations", [])
    if level_id not in creations:
        creations.append(level_id)
        userDB.update_field(sender_id, "creations", creations)

print("✔ Done: all levels spreaded on lists 'creations' theirs submitters.")