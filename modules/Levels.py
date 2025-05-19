from .__utils__ import *
from bot import bot

async def main(ctx):
    user_id = ctx.author.id
    played = userDB.get(user_id)['played']
    levels = []
    for i, level_id in enumerate(MAIN_LEVELS, start=1):
        data = levelDB.get(level_id)
        if not data:
            continue

        emoji_difficulty = get_difficulty_visual(user_id, data['difficulty'])

        stars = min(data["difficulty"], 10)
        mana = ORBS[stars - 1] if stars > 0 else 0

        users_level_progress = (played[i]['record']) if i in played else ""
        if users_level_progress == 100:
            users_level_progress = EMOJIS['checkmark']
        elif users_level_progress:
            users_level_progress = f"`{str(users_level_progress)}%`"
        else:
            users_level_progress = ""

        count_coins = (played[i]['coins']) if i in played else [0 for _ in range(data['coins'])]
        level_coins = " "
        if len(count_coins) > 0:
            level_coins = "".join(EMOJIS['goldcoin'] if coin else EMOJIS['lockedcoin'] for coin in count_coins) + " "

        level_str = (
            f"`ID {i}:`\n"
            f"{emoji_difficulty} {data['name']} {level_coins}{users_level_progress}\n"
            f"{EMOJIS['star']}{stars} {EMOJIS['manaorbs']}{mana}"
        )
        levels.append(level_str)

    pages = [levels[i:i+5] for i in range(0, len(levels), 5)]
    total_pages = len(pages)
    if total_pages == 0:
        await ctx.send("No main levels found.")
        return

    current = 0

    def create_embed(index):
        embed = discord.Embed(
            title="📘 Main Levels",
            description="\n\n".join(pages[index]),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {index + 1}/{total_pages}")
        return embed

    message = await ctx.send(embed=create_embed(current))

    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return (
            user == ctx.author and
            reaction.message.id == message.id and
            str(reaction.emoji) in ["⬅️", "➡️"]
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "⬅️" and current > 0:
                current -= 1
                await message.edit(embed=create_embed(current))
            elif str(reaction.emoji) == "➡️" and current < total_pages - 1:
                current += 1
                await message.edit(embed=create_embed(current))
            await message.remove_reaction(reaction.emoji, user)
        except asyncio.TimeoutError:
            break

async def search(ctx, *, args=None):
    user_id = ctx.author.id
    played = userDB.get(user_id)['played']

    data = None
    difficulty_filter = None

    if args:
        parts = args.split()
        if len(parts) >= 1:
            data = parts[0]
        if len(parts) >= 2:
            difficulty_input = parts[1].lower()
            difficulty_filter = get_search_difficulties(user_id, difficulty_input)

    conn = sqlite3.connect("data/levels.db")
    cursor = conn.cursor()

    results = []

    if not data or data == "#":
        if difficulty_filter:
            placeholders = ",".join("?" * len(difficulty_filter))
            query = f"SELECT * FROM levels WHERE difficulty IN ({placeholders})"
            params = difficulty_filter
        else:
            query = "SELECT * FROM levels"
            params = []

        if MAIN_LEVELS:
            main_placeholders = ",".join("?" * len(MAIN_LEVELS))
            query += f" AND level_id NOT IN ({main_placeholders})" if difficulty_filter else f" WHERE level_id NOT IN ({main_placeholders})"
            params += MAIN_LEVELS

        query += " ORDER BY likes DESC LIMIT 100"
        cursor.execute(query, params)
        rows = cursor.fetchall()
    else:
        try:
            level_id = int(data)
            level_id = data
            if level_id in MAIN_LEVELS:
                rows = []
            else:
                cursor.execute("SELECT * FROM levels WHERE level_id = ?", (level_id,))
                row = cursor.fetchone()
                rows = [row] if row else []
        except:
            data = data.replace("-", " ").replace("\\", "")
            data = discord.utils.escape_markdown(data)

            if data == "#":
                name_condition = "1 = 1"
                name_args = []
            else:
                name_condition = "name LIKE ?"
                name_args = [f"%{data}%"]

            query = f"SELECT * FROM levels WHERE {name_condition}"
            params = name_args

            if difficulty_filter:
                placeholders = ",".join("?" * len(difficulty_filter))
                query += f" AND difficulty IN ({placeholders})"
                params += difficulty_filter

            if MAIN_LEVELS:
                placeholders = ",".join("?" * len(MAIN_LEVELS))
                query += f" AND level_id NOT IN ({placeholders})"
                params += MAIN_LEVELS

            query += " ORDER BY likes DESC LIMIT 100"
            cursor.execute(query, params)
            rows = cursor.fetchall()

    conn.close()

    if not rows:
        await ctx.send("No levels found matching your criteria.")
        return

    results = []
    for row in rows:
        if row[0] in ["daily", "weekly"]:
            continue
        
        level_data = {
            "level_id": row[0],
            "name": row[1],
            "difficulty": row[2],
            "downloads": row[3],
            "likes": row[4],
            "time": row[5],
            "coins": row[6]
        }

        emoji_difficulty = get_difficulty_visual(user_id, level_data['difficulty'])

        stars = min(level_data["difficulty"], 10)
        mana = ORBS[stars - 1] if stars > 0 else 0
        rate_emoji = EMOJIS['like'] if level_data['likes'] >= 0 else EMOJIS['dislike']

        users_level_data = (played[level_data['level_id']]['record']) if level_data['level_id'] in played else None
        if users_level_data == 100:
            users_level_data = EMOJIS['checkmark']
        elif users_level_data:
            users_level_data = f"`{str(users_level_data)}%`"
        else:
            users_level_data = ""
        
        count_coins = (played[level_data['level_id']]['coins']) if level_data['level_id'] in played else [0 for _ in range(level_data['coins'])]
        level_coins = " "
        if len(count_coins) > 0:
            level_coins = "".join(EMOJIS['usercoin'] if coin else EMOJIS['lockedcoin'] for coin in count_coins) + " "

        text = (
            f"`ID {level_data['level_id']}:`\n"
            f"{emoji_difficulty} {level_data['name']} {level_coins}{users_level_data}\n"
            f"{EMOJIS['star']}{stars} {EMOJIS['manaorbs']}{mana}\n"
            f"{EMOJIS['download']}{level_data['downloads']} {rate_emoji}{level_data['likes']} {EMOJIS['time']}{level_time(level_data['time'])}"
        )
        results.append(text)

    pages = [results[i:i + 5] for i in range(0, len(results), 5)]
    total_pages = len(pages)
    current = 0

    def create_embed(index):
        embed = discord.Embed(
            title="🔍 Search Results",
            description="\n\n".join(pages[index]),
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Page {index + 1}/{total_pages}")
        return embed

    message = await ctx.send(embed=create_embed(current))
    if total_pages == 1:
        return

    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "⬅️" and current > 0:
                current -= 1
                await message.edit(embed=create_embed(current))
            elif str(reaction.emoji) == "➡️" and current < total_pages - 1:
                current += 1
                await message.edit(embed=create_embed(current))
            await message.remove_reaction(reaction.emoji, user)
        except asyncio.TimeoutError:
            break

async def recent(ctx):
    user_id = ctx.author.id
    played = userDB.get(user_id)['played']

    recent_ids = botDB.get("recent") or []
    recent_ids.reverse()

    if not recent_ids:
        await ctx.send("📭 No recent levels found.")
        return

    levels = []
    for i, level_id in enumerate(recent_ids, start=1):
        data = levelDB.get(level_id)
        if not data:
            continue

        emoji_difficulty = get_difficulty_visual(user_id, data['difficulty'])

        stars = min(data["difficulty"], 10)
        mana = ORBS[stars - 1] if stars > 0 else 0
        rate_emoji = EMOJIS['like'] if data['likes'] >= 0 else EMOJIS['dislike']

        users_level_progress = (played[level_id]['record']) if level_id in played else ""
        if users_level_progress == 100:
            users_level_progress = EMOJIS['checkmark']
        elif users_level_progress:
            users_level_progress = f"{str(users_level_progress)}%"
        else:
            users_level_progress = ""

        count_coins = (played[level_id]['coins']) if level_id in played else [0 for _ in range(data['coins'])]
        level_coins = " "
        if len(count_coins) > 0:
            level_coins = "".join(EMOJIS['usercoin'] if coin else EMOJIS['lockedcoin'] for coin in count_coins) + " "

        level_str = (
            f"`ID {level_id}:`\n"
            f"{emoji_difficulty} {data['name']} {level_coins}{users_level_progress}\n"
            f"{EMOJIS['star']}{stars} {EMOJIS['manaorbs']}{mana}\n"
            f"{EMOJIS['download']}{data['downloads']} {rate_emoji}{data['likes']} {EMOJIS['time']}{level_time(data['time'])}"
        )
        levels.append(level_str)

    pages = [levels[i:i+5] for i in range(0, len(levels), 5)]
    total_pages = len(pages)
    if total_pages == 0:
        await ctx.send("❌ No valid recent levels found.")
        return

    current = 0

    def create_embed(index):
        embed = discord.Embed(
            title="🕘 Recent Levels",
            description="\n\n".join(pages[index]),
            color=discord.Color.blurple()
        )
        embed.set_footer(text=f"Page {index + 1}/{total_pages}")
        return embed

    message = await ctx.send(embed=create_embed(current))

    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return (
            user == ctx.author and
            reaction.message.id == message.id and
            str(reaction.emoji) in ["⬅️", "➡️"]
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "⬅️" and current > 0:
                current -= 1
                await message.edit(embed=create_embed(current))
            elif str(reaction.emoji) == "➡️" and current < total_pages - 1:
                current += 1
                await message.edit(embed=create_embed(current))
            await message.remove_reaction(reaction.emoji, user)
        except asyncio.TimeoutError:
            break

async def creator(ctx, member: discord.Member):
    user_id = member.id
    creator_data = userDB.get(user_id)

    if not creator_data or "creations" not in creator_data:
        await ctx.send("❌ Failed to found creator's data.")
        return

    creation_ids = creator_data['creations']
    if not creation_ids:
        await ctx.send("📭 This user hasn't submitted any levels.")
        return

    creation_ids.reverse()

    levels = []
    for i, level_id in enumerate(creation_ids, start=1):
        if level_id in MAIN_LEVELS:
            continue

        data = levelDB.get(level_id)
        if not data:
            continue

        emoji_difficulty = get_difficulty_visual(ctx.author.id, data['difficulty'])

        stars = min(data["difficulty"], 10)
        mana = ORBS[stars - 1] if stars > 0 else 0
        rate_emoji = EMOJIS['like'] if data['likes'] >= 0 else EMOJIS['dislike']

        played = userDB.get(ctx.author.id).get('played', {})
        users_level_progress = (played[level_id]['record']) if level_id in played else ""
        if users_level_progress == 100:
            users_level_progress = EMOJIS['checkmark']
        elif users_level_progress:
            users_level_progress = f"{str(users_level_progress)}%"
        else:
            users_level_progress = ""

        count_coins = (played[level_id]['coins']) if level_id in played else [0 for _ in range(data['coins'])]
        level_coins = " "
        if len(count_coins) > 0:
            level_coins = "".join(EMOJIS['usercoin'] if coin else EMOJIS['lockedcoin'] for coin in count_coins) + " "

        level_str = (
            f"`ID {level_id}:`\n"
            f"{emoji_difficulty} {data['name']} {level_coins}{users_level_progress}\n"
            f"{EMOJIS['star']}{stars} {EMOJIS['manaorbs']}{mana}\n"
            f"{EMOJIS['download']}{data['downloads']} {rate_emoji}{data['likes']} {EMOJIS['time']}{level_time(data['time'])}"
        )
        levels.append(level_str)

    pages = [levels[i:i+5] for i in range(0, len(levels), 5)]
    total_pages = len(pages)
    if total_pages == 0:
        await ctx.send("❌ No valid levels submitted by this user.")
        return

    current = 0

    def create_embed(index):
        embed = discord.Embed(
            title=f"🛠️ Levels by {member.name}",
            description="\n\n".join(pages[index]),
            color=discord.Color.orange()
        )
        embed.set_footer(text=f"Page {index + 1}/{total_pages}")
        return embed

    message = await ctx.send(embed=create_embed(current))

    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return (
            user == ctx.author and
            reaction.message.id == message.id and
            str(reaction.emoji) in ["⬅️", "➡️"]
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "⬅️" and current > 0:
                current -= 1
                await message.edit(embed=create_embed(current))
            elif str(reaction.emoji) == "➡️" and current < total_pages - 1:
                current += 1
                await message.edit(embed=create_embed(current))
            await message.remove_reaction(reaction.emoji, user)
        except asyncio.TimeoutError:
            break
