import requests
import random
import time
from database import *

AUTHOR = "1485184950734032927"

DEMON_DIFFICULTY_MAP = {
    1: 10,
    2: 11,
    3: 12,
    4: 13,
    5: 14,
}

# -------------------- CONVERTERS --------------------

def convert_pack_difficulty(stars):
    try:
        stars = int(stars)
    except (ValueError, TypeError):
        return 1

    if stars == 10:
        return 12  # demon pack

    return max(1, min(stars, 9))


def convert_level_difficulty(level):
    if level.get("demon"):
        return DEMON_DIFFICULTY_MAP.get(level.get("demonDifficulty", 1), 10)

    stars = level.get("stars", 1)

    if stars <= 1:
        return 1
    return stars


def convert_length(length):
    # если приходит число (как в GD API)
    if isinstance(length, int):
        ranges = {
            0: (0, 9),      # tiny
            1: (10, 29),    # short
            2: (30, 59),    # medium
            3: (60, 119),   # long
            4: (120, 179),  # xl
        }
        low, high = ranges.get(length, (10, 29))
        return random.randint(low, high)

    # если вдруг строка
    ranges = {
        "tiny":   (0, 9),
        "short":  (10, 29),
        "medium": (30, 59),
        "long":   (60, 119),
        "xl":     (120, 179),
    }

    low, high = ranges.get(str(length).lower(), (10, 29))
    return random.randint(low, high)


# -------------------- API --------------------

def fetch_json(url):
    while True:
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 429:
                print(f"⏳ 429 Rate limit. Waiting 60s... ({url})")
                time.sleep(60)
                continue

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"❌ Request failed: {url} | {e}")
            return None


# -------------------- MAIN --------------------

packs_data = fetch_json("https://gdbrowser.com/api/mappacks")

if not packs_data:
    print("Failed to fetch map packs. Exiting.")
    exit(1)

packs = sorted(packs_data, key=lambda p: int(p.get("id", 0)))

map_packs = botDB.get("mappacks") or {}

# временные хранилища
new_levels = []
new_packs = {}

print("\n========== PREVIEW ==========")

for pack in packs:
    pack_id = str(pack.get("id"))

    name = pack.get("name", "Unknown")

    # ✅ защита от повторного добавления паков
    if pack_id in map_packs:
        print(f"\n📦 Pack {pack_id}: {name} (already exists)")
        continue

    level_ids = []

    print(f"\n📦 Pack {pack_id}: {name}")

    for level_id in pack.get("levels", []):
        level_id = str(level_id)

        # ✅ защита от повторных уровней
        if levelDB.get(level_id):
            print(f"  • {level_id} (already exists)")
            level_ids.append(level_id)
            continue

        lvl = fetch_json(f"https://gdbrowser.com/api/level/{level_id}")

        if not lvl:
            print(f"  ⚠️ {level_id} (invalid)")
            continue

        lvl_name   = lvl.get("name", "Unknown")
        lvl_diff   = convert_level_difficulty(lvl)
        lvl_length = convert_length(lvl.get("length", "short"))
        lvl_coins  = lvl.get("coins", 0)

        print(f"  ➕ {lvl_name} | diff: {lvl_diff} | len: {lvl_length}")

        new_levels.append((
            level_id,
            lvl_name,
            lvl_diff,
            "0",
            "0",
            lvl_length,
            lvl_coins,
            AUTHOR
        ))

        level_ids.append(level_id)

    difficulty = convert_pack_difficulty(pack.get("stars"))

    new_packs[pack_id] = {
        "name": name,
        "difficulty": difficulty,
        "levels": level_ids,
    }

print("\n========== SUMMARY ==========")
print(f"New levels: {len(new_levels)}")
print(f"New packs: {len(new_packs)}")

# -------------------- CONFIRM --------------------

confirm = input("\nApply changes to database? (yes/no): ").strip().lower()

if confirm not in ("yes", "y"):
    print("❌ Cancelled. Nothing was added.")
    exit()

# -------------------- APPLY --------------------

print("\n========== APPLYING ==========")

added_levels_ids = []

for lvl in new_levels:
    level_id, name, difficulty, downloads, likes, length, coins, sender = lvl
    
    levelDB.add(*lvl)
    added_levels_ids.append(int(level_id))

# ✅ обновление автора
data = userDB.get(AUTHOR)
if data:
    current_cp = data.get("creatorpoints", 0)
    creations = data.get("creations", [])

    added = 0

    for level_id in added_levels_ids:
        if level_id not in creations:
            creations.append(level_id)
            added += 1

    if added > 0:
        userDB.update_field(AUTHOR, "creatorpoints", current_cp + added)
        userDB.update_field(AUTHOR, "creations", creations)

        print(f"👤 Author updated: +{added} CP")

# паки как были
map_packs.update(new_packs)
botDB.update_field("mappacks", map_packs)

print("✅ Database updated successfully!")