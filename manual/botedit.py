from database import *

# какие паки удалить
REMOVE_PACKS = {"66", "74"}

map_packs = botDB.get("mappacks") or {}

removed = 0
not_found = 0

for pack_id in REMOVE_PACKS:
    if pack_id in map_packs:
        del map_packs[pack_id]
        print(f"🗑️ Removed pack {pack_id}")
        removed += 1
    else:
        print(f"⚠️ Pack {pack_id} not found")
        not_found += 1

botDB.update_field("mappacks", map_packs)

print("\n✅ Done")
print(f"Removed: {removed}")
print(f"Not found: {not_found}")