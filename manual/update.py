import sqlite3
import json

conn = sqlite3.connect("data/users.db")
cursor = conn.cursor()

# дефолты
defaults = {
    "purchased": [],
    "visuals": [0, 0],
    "creations": [],
    "collected": [],
    "icons": [0,0,0,0,0,0,0,0]
}

cursor.execute("""
SELECT user_id, purchased, visuals, creations, collected, icons
FROM users
""")
rows = cursor.fetchall()

def is_valid_list(value):
    try:
        parsed = json.loads(value)

        # двойной json → невалид
        if isinstance(parsed, str):
            return False

        return isinstance(parsed, list)
    except:
        return False

fixed_count = 0

for row in rows:
    user_id = row[0]

    purchased, visuals, creations, collected, icons = row[1:]

    updates = {}

    # --- обычные поля ---
    for field, raw_value in zip(
        ["purchased", "visuals", "creations", "collected"],
        [purchased, visuals, creations, collected]
    ):
        if not is_valid_list(raw_value):
            updates[field] = json.dumps(defaults[field])

    # --- icons ---
    if not is_valid_list(icons):
        updates["icons"] = json.dumps(defaults["icons"])
    else:
        parsed_icons = json.loads(icons)

        if len(parsed_icons) == 7:
            parsed_icons.append(0)
            updates["icons"] = json.dumps(parsed_icons)

        elif len(parsed_icons) != 8:
            updates["icons"] = json.dumps(defaults["icons"])

    # --- обновление ---
    if updates:
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values())
        values.append(user_id)

        cursor.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = ?",
            values
        )

        fixed_count += 1

conn.commit()
conn.close()

print(f"Done. Fixed users: {fixed_count}")