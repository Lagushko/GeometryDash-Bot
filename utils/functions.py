import random
import colorama
from database import *
from .constants import *
from .config import *

def permission(level: int):
    helpers, moderators, admins, devs, owner = [], [], [], [], []
    if level <= 1: helpers = botDB.get('helpers') or []
    if level <= 2: moderators = botDB.get('moderators') or []
    if level <= 3: admins = botDB.get('admins') or []
    if level <= 4: devs = botDB.get('devs') or []
    if level <= 5: owner = Config.OWNER
    return helpers + moderators + admins + devs + owner

def get_difficulty_visual(user_id, difficulty):
    user_data = userDB.get(user_id)
    if not user_data:
        return EMOJIS["na"]

    visuals = user_data.get("visuals", [0, 0])
    if len(visuals) < 2:
        visuals += [0] * (2 - len(visuals))

    name = DIFFICULTIES[difficulty - 1]

    if difficulty >= 10:
        if visuals[0]:
            return EMOJIS[name]
        else:
            if name in [
                "supremedemon", "ultimatedemon", "legendarydemon",
                "mythicaldemon", "infinitedemon", "grandpademon"
            ]:
                return EMOJIS["extremedemon"]
            return EMOJIS[name]
    else:
        if visuals[1]:
            return EMOJIS[name]
        else:
            fallback_map = {
                "casual": "hard",
                "tough": "harder",
                "cruel": "insane"
            }
            name = fallback_map.get(name, name)
            return EMOJIS[name]

def get_search_difficulties(user_id, name):
    user_data = userDB.get(user_id)
    visuals = user_data.get("visuals", [0, 0])
    name = name.lower()

    result = []

    difficulty_map = {
        "hard": ["hard", "casual"],
        "harder": ["harder", "tough"],
        "insane": ["insane", "cruel"],
        "extremedemon": [
            "extremedemon", "supremedemon", "ultimatedemon",
            "legendarydemon", "mythicaldemon", "infinitedemon", "grandpademon"
        ]
    }

    if name not in DIFFICULTIES:
        return []

    for base, group in difficulty_map.items():
        if name in group:
            if name in ["hard", "harder", "insane"] and visuals[1] == 0:
                names_to_check = group
            elif name == "extremedemon" and visuals[0] == 0:
                names_to_check = group
            else:
                names_to_check = [name]
            break
    else:
        names_to_check = [name]

    for diff in names_to_check:
        if diff in DIFFICULTIES:
            result.append(DIFFICULTIES.index(diff) + 1)

    return result

def level_time(seconds):
    if seconds < 15: return "Tiny"
    if seconds < 30: return "Short"
    if seconds < 60: return "Medium"
    if seconds < 120: return "Long"
    return "XL"

def level_markdown(user_id, played, level_data, remove_details=False, enum=None, custom_id=None):
    emoji_difficulty = get_difficulty_visual(user_id, level_data['difficulty'])

    stars = min(level_data["difficulty"], 10)
    mana = ORBS[stars - 1] if stars > 0 else 0
    rate_emoji = EMOJIS['like'] if level_data['likes'] >= 0 else EMOJIS['dislike']

    record = played.get(level_data['level_id'], {}).get('record')
    if record == 100:
        user_progress = EMOJIS['checkmark']
    elif record is not None:
        user_progress = f"`{record}%`"
    else:
        user_progress = ""

    coin_total = level_data['coins']
    coin_data = played.get(level_data['level_id'], {}).get('coins', [0] * coin_total)
    level_coins = "".join(EMOJIS['usercoin'] if coin else EMOJIS['lockedcoin'] for coin in coin_data) + " " if coin_total else " "

    display_id = custom_id if custom_id is not None else level_data['level_id']
    id_text = f"`#{enum} | ID {display_id}:`\n" if enum else f"`ID {display_id}:`\n"

    text = (
        id_text +
        f"{emoji_difficulty} {level_data['name']} {level_coins}{user_progress}\n"
        f"{TAB*2}{EMOJIS['star']}{stars} {EMOJIS['manaorbs']}{mana}\n"
    )

    if not remove_details:
        text += (
            f"{TAB*2}{EMOJIS['download']}{level_data['downloads']} "
            f"{rate_emoji}{level_data['likes']} {EMOJIS['time']}{level_time(level_data['time'])}"
        )

    return text

def predict_level_completion(level, user, nickname=None):
    final_result = 0

    level_difficulty = level['difficulty']
    max_user_difficulty = user['hardest'][0]
    levels_at_max_difficulty = user['hardest'][1]
    level_id = level.get('level_id')
    edited_level_id = level_id
    if level_id in ['weekly', 'daily']:
        edited_level_id += botDB.get(level_id)[0]
    played_data = user['played'][edited_level_id]
    attempts = played_data['attempts']
    record = played_data['record']
    length = level['time']

    display_name = nickname or user['user_id']

    if level_difficulty == 1:
        final_result = 100

        print(f"\
{colorama.Fore.YELLOW}WP: 1.0000, {colorama.Style.RESET_ALL}\
FM: 1.0000, \
AM: 1.0000, \
LM: 1.0000, \
{colorama.Fore.CYAN}FWP: 1.0000, \
{colorama.Fore.CYAN}FRP: 100, \
{colorama.Fore.GREEN}AA: 1 {colorama.Style.RESET_ALL}\
[{display_name}] [{level['name']}]"
        )
    else:
        def base_attempts(difficulty):
            return 0.14105 * difficulty**4 - 3.65008 * difficulty**3 + 39.1527 * difficulty**2 - 149.3046 * difficulty + 199.5352

        expected_attempts = base_attempts(level_difficulty)
        difficulty_difference = max_user_difficulty - level_difficulty
        skill_factor = max(0.1, 1 - 0.15 * difficulty_difference - 0.05 * levels_at_max_difficulty)
        adjusted_attempts = max(1, expected_attempts * skill_factor)

        length_multiplier = 2 / (1 + length / 90)
        average_atts = int(adjusted_attempts * random.uniform(1.35, 1.65) * length_multiplier)

        win_probability = 1 / (adjusted_attempts * 0.5 + 1)
        fluke_multiplier = max(0.01, record / 100.0) + 0.5 * (1 - record / 100.0) * (attempts / (adjusted_attempts + attempts))

        attempts_multiplier = 1.0
        if average_atts > 0:
            ratio = attempts / average_atts
            if ratio > 1/2:
                attempts_multiplier = ratio*2

        final_win_probability = win_probability * fluke_multiplier * attempts_multiplier

        if random.random() <= final_win_probability:
            final_result = 100
        else:
            skill_gap_penalty = max(0.2, 1 - 0.1 * (level_difficulty - max_user_difficulty))
            experience_bonus = min(1.0, 0.05 * levels_at_max_difficulty)
            max_theoretical_record = int(min(99, 90 * skill_gap_penalty + 10 * experience_bonus))

            roll = random.random()
            max_possible = min(max_theoretical_record, int(40 + attempts * 0.5 + record * 0.5))
            
            raw_progress_chance = 0.3 + (1 - win_probability) * 0.7
            progress_chance = max(0.1, min(0.9, raw_progress_chance))

            difficulty_gap = max(0, level_difficulty - max_user_difficulty)
            min_first_progress = max(1, int(8 - difficulty_gap * 2)) if difficulty_gap <= 1 else 1

            if record > 1 and roll < progress_chance * 0.6:
                percent = max(1, int(record * random.uniform(0.20, 0.60)))
            elif roll < progress_chance or (record >= 95 and random.random() <= 0.95):
                percent = int(record * random.uniform(0.60, 1.00))
            else:
                if difficulty_gap == 0:
                    gain_multiplier = 0.5
                elif difficulty_gap == 1:
                    gain_multiplier = 0.35
                else:
                    gain_multiplier = 0.25
                max_gain = max(min_first_progress + 1, int((max_possible - record) * gain_multiplier))
                percent = record + random.randint(min_first_progress, max_gain)

            if record >= 95 and percent > record:
                clutch_chance = (record - 94) * 0.01
                if random.random() <= clutch_chance:
                    percent = 100

            if percent == 100:
                final_result = 100
            else:
                final_result = max(1, min(percent, max_possible))

        print(f"\
{colorama.Fore.YELLOW}WP: {win_probability:.4f}, {colorama.Style.RESET_ALL}\
FM: {fluke_multiplier:.4f}, \
AM: {attempts_multiplier:.4f}, \
LM: {length_multiplier:.4f}, \
{colorama.Fore.CYAN}FWP: {final_win_probability:.4f}, \
{colorama.Fore.CYAN}FRP: {final_result}, \
{colorama.Fore.GREEN}AA: {average_atts} {colorama.Style.RESET_ALL}\
[{display_name}] [{level['name']}]"
        )

    return final_result

def get_advanced_ranking(top):
    if top <= 10: return 1
    if top <= 50: return 2
    if top <= 100: return 3
    if top <= 200: return 4
    if top <= 500: return 5
    if top <= 1000: return 6
    return 7

def get_ranking(top):
    if top <= 1: return 1
    if top <= 2: return 2
    if top <= 5: return 3
    if top <= 10: return 4
    if top <= 20: return 5
    if top <= 100: return 6
    return 7

HELP_SECTIONS = {
    "📖": {
        "title": "Basic Commands",
        "content": """
`!help` — Show this help message  
`!link` — Link to add bot to your server  
`!profile [@player]` — Show your or another player's profile  
`!leaderboards <global/local>` — View global or server-only leaderboards  
`!visual <extremes/defaults> <on/off>` — Enable or disable additional visuals  
"""
    },
    "🎮": {
        "title": "Levels",
        "content": """
`!main` — View main and official game levels  
`!search <#/name/id> [difficulty]` — Search for a level  
`!recent` — View recent added 25 levels  
`!creator <@player>` — View all levels submitted by user  
`!demonlist` — View list of the hardest extreme demons in bot
"""
    },
    "👍": {
        "title": "Interaction",
        "content": """
`!join <id>` — Join a level  
`!quit` — Leave the level  
`!play [id]` — Play the joined level or specific one  
`!like <id>` — Like a level (must be played)  
`!dislike <id>` — Dislike a level (must be played)  
"""
    },
    "⏳": {
        "title": "Bonuses",
        "content": """
`!map-pack [id] [collect]` — View all the map packs (id for specific map pack, collect to take rewards if completed) 
`!daily` — View the daily level  
`!weekly` — View the weekly level  
`!reward` — Claim Large and Small chests (24h and 4h countdown)
"""
    },
    "🛒": {
        "title": "Icon Shop",
        "content": """
`!shop` — View available icons  
`!buy <id>` — Buy an icon  
`!equip <id>` — Equip an icon  
"""
    },
    "📤": {
        "title": "Submissions",
        "content": lambda ctx: f"""
`!send <id>` — Submit a Geometry Dash level for review {EMOJIS['creatorpoints']}
""" if ctx.author.id not in permission(1) else f"""
`!send <id>` — Submit a Geometry Dash level for review (unlimited use) {EMOJIS['creatorpoints']}  
`!sent-list` — View a list of sent levels  
"""
    },
    "🔧": {
        "title": "Admin Only",
        "condition": lambda ctx: ctx.author.id in permission(2),
        "content": lambda ctx: (
            """
`!delete-user <id>` — Delete a user's data (you can delete only own)
`!cheats <noclip/speedhack/icons> <on/off>` — Toggle cheat modes  
`!manage <user/level/settings> <id/none> <field> <data>` — Edit database values (you can edit only own user data)
""" if ctx.author.id in permission(4) and ctx.author.id not in permission(5) else """
`!add-level <id> <name> <difficulty> <downloads> <likes> <time> <coins> <sender>` — Add a level  
`!add-mappack <id> <name> <difficulty> <listOfLevelIDs>` — Add a map pack
`!delete-user <id>` — Delete a user's data
`!delete-level <id>` — Delete a level's data  
`!delete-sent <id>` — Delete a sent level  
`!demonlist-pos <id> <position>` — Adds/moves the level to position on demonlist (pos 0 to delete)
`!cheats <noclip/speedhack/icons> <on/off>` — Toggle cheat modes  
`!manage <user/level/settings> <id/none> <field> <data>` — Edit database values  
"""
        )
    },
    "🔒": {
        "title": "Bot Control",
        "condition": lambda ctx: ctx.author.id in permission(5),
        "content": """
`!update-db <users/levels> <field> <default> <type>` — Add a new field  
`!set-db <users/levels> <field> <value>` — Set value in all entries  
`!role <role> <add/remove> <id>` — Change permissions  
`!data <name> <default> <type>` — Add global bot setting  
"""
    }
}