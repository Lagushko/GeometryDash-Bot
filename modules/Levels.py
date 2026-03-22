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

        level_str = level_markdown(user_id, played, data, remove_details=True)
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

    await message.add_reaction("⏮")
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")
    await message.add_reaction("⏭")

    def check(reaction, user):
        return (
            user == ctx.author and
            reaction.message.id == message.id and
            str(reaction.emoji) in ["⏮", "⬅️", "➡️", "⏭"]
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            emoji = str(reaction.emoji)
            if emoji == "⏮" and current != 0:
                current = 0
                await message.edit(embed=create_embed(current))
            elif emoji == "⬅️" and current > 0:
                current -= 1
                await message.edit(embed=create_embed(current))
            elif emoji == "➡️" and current < total_pages - 1:
                current += 1
                await message.edit(embed=create_embed(current))
            elif emoji == "⏭" and current != total_pages - 1:
                current = total_pages - 1
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

        text = level_markdown(user_id, played, level_data)
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

    await message.add_reaction("⏮")
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")
    await message.add_reaction("⏭")

    def check(reaction, user):
        return (
            user == ctx.author and
            reaction.message.id == message.id and
            str(reaction.emoji) in ["⏮", "⬅️", "➡️", "⏭"]
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            emoji = str(reaction.emoji)
            if emoji == "⏮" and current != 0:
                current = 0
                await message.edit(embed=create_embed(current))
            elif emoji == "⬅️" and current > 0:
                current -= 1
                await message.edit(embed=create_embed(current))
            elif emoji == "➡️" and current < total_pages - 1:
                current += 1
                await message.edit(embed=create_embed(current))
            elif emoji == "⏭" and current != total_pages - 1:
                current = total_pages - 1
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

        level_str = level_markdown(user_id, played, data)
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

    await message.add_reaction("⏮")
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")
    await message.add_reaction("⏭")

    def check(reaction, user):
        return (
            user == ctx.author and
            reaction.message.id == message.id and
            str(reaction.emoji) in ["⏮", "⬅️", "➡️", "⏭"]
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            emoji = str(reaction.emoji)
            if emoji == "⏮" and current != 0:
                current = 0
                await message.edit(embed=create_embed(current))
            elif emoji == "⬅️" and current > 0:
                current -= 1
                await message.edit(embed=create_embed(current))
            elif emoji == "➡️" and current < total_pages - 1:
                current += 1
                await message.edit(embed=create_embed(current))
            elif emoji == "⏭" and current != total_pages - 1:
                current = total_pages - 1
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

    played = userDB.get(ctx.author.id).get('played', {})

    levels = []
    for i, level_id in enumerate(creation_ids, start=1):
        if level_id in MAIN_LEVELS:
            continue

        data = levelDB.get(level_id)
        if not data:
            continue

        level_str = level_markdown(ctx.author.id, played, data)
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

    await message.add_reaction("⏮")
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")
    await message.add_reaction("⏭")

    def check(reaction, user):
        return (
            user == ctx.author and
            reaction.message.id == message.id and
            str(reaction.emoji) in ["⏮", "⬅️", "➡️", "⏭"]
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            emoji = str(reaction.emoji)
            if emoji == "⏮" and current != 0:
                current = 0
                await message.edit(embed=create_embed(current))
            elif emoji == "⬅️" and current > 0:
                current -= 1
                await message.edit(embed=create_embed(current))
            elif emoji == "➡️" and current < total_pages - 1:
                current += 1
                await message.edit(embed=create_embed(current))
            elif emoji == "⏭" and current != total_pages - 1:
                current = total_pages - 1
                await message.edit(embed=create_embed(current))
            await message.remove_reaction(reaction.emoji, user)
        except asyncio.TimeoutError:
            break

async def demonlist(ctx):
    user_id = ctx.author.id
    played = userDB.get(user_id)['played']

    admins = botDB.get("admins") or []
    moderators = botDB.get("moderators") or []
    show_aredl = user_id in (admins + Config.OWNER + moderators)

    aredl_list = []
    if show_aredl:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.aredl.net/v2/api/aredl/levels") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    aredl_list = [str(level["level_id"]) for level in data if "level_id" in level]

    demonlist_ids = botDB.get("demonlist") or []

    if not demonlist_ids:
        await ctx.send("📭 No levels in the demonlist.")
        return

    levels = []
    for i, level_id in enumerate(demonlist_ids, start=1):
        data = levelDB.get(level_id)
        if not data:
            continue

        level_str = level_markdown(user_id, played, data, enum=i)

        if show_aredl:
            try:
                aredl_pos = aredl_list.index(level_id) + 1
                level_str = f"`#{aredl_pos} AREDL`\n" + level_str
            except:
                None

        levels.append(level_str)

    pages = [levels[i:i+5] for i in range(0, len(levels), 5)]
    total_pages = len(pages)
    if total_pages == 0:
        await ctx.send("❌ No valid demonlist levels found.")
        return

    current = 0

    def create_embed(index):
        embed = discord.Embed(
            title=f"{EMOJIS['extremedemon']} Demon List",
            description="\n\n".join(pages[index]),
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Page {index + 1}/{total_pages}")
        return embed

    message = await ctx.send(embed=create_embed(current))

    await message.add_reaction("⏮")
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")
    await message.add_reaction("⏭")

    def check(reaction, user):
        return (
            user == ctx.author and
            reaction.message.id == message.id and
            str(reaction.emoji) in ["⏮", "⬅️", "➡️", "⏭"]
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            emoji = str(reaction.emoji)
            if emoji == "⏮" and current != 0:
                current = 0
                await message.edit(embed=create_embed(current))
            elif emoji == "⬅️" and current > 0:
                current -= 1
                await message.edit(embed=create_embed(current))
            elif emoji == "➡️" and current < total_pages - 1:
                current += 1
                await message.edit(embed=create_embed(current))
            elif emoji == "⏭" and current != total_pages - 1:
                current = total_pages - 1
                await message.edit(embed=create_embed(current))
            await message.remove_reaction(reaction.emoji, user)
        except asyncio.TimeoutError:
            break
