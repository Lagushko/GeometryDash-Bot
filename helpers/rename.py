import sqlite3

db_path = "data/levels.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT level_id, name FROM levels")
levels = cursor.fetchall()

updated_count = 0

for level_id, name in levels:
    if "-" in name:
        new_name = name.replace("-", " ")
        cursor.execute("UPDATE levels SET name = ? WHERE level_id = ?", (new_name, level_id))
        updated_count += 1

conn.commit()
conn.close()

print(f"\n✅ Names changed in {updated_count} levels.")