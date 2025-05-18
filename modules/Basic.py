from modules import *
from bot import bot

async def help(ctx):
    """
`!command` — Text
    """

    embed = discord.Embed(
        title=f"{EMOJIS['demon']} Welcome to Geometry Dash Bot! {EMOJIS['demon']}",
        description=f"This is a **Geometry Dash simulation bot**! {EMOJIS['like']} Play, collect stars, unlock icons, and compete with others!",
        color=discord.Color.blue()
    )

    embed.add_field(name="📖 Basic Commands", value="""
`!help` — Show this help message  
`!profile [@player]` — Show your or another player's profile  
`!leaderboards <global/local>` — View global or server-only leaderboards  
`!main` — View main official game levels  
`!visual <extremes/defaults> <on/off>` — Enable or disable additional visuals (disabled all on standard)
`!search <#/name/id> [difficulty]` — Search for a level, # is without name filter, difficulty without space 
`!recent` — View recent 25 levels
`!creator <@player>` — View all levels submitted by user
""", inline=False)

    embed.add_field(name="👍 Interaction", value="""
`!join <id>` — Join a level (optional)
`!quit` — Leave the level (optional)
`!play [id]` — Play the joined level, write an ID if you haven't joined anything
`!like <id>` — Like a level (you must play it at least once)  
`!dislike <id>` — Dislike a level (same rule applies)  
""", inline=False)

    embed.add_field(name="⏳ Bonuses", value=f"""
`!daily` — View the daily level  
`!weekly` — View the weekly level  
`!reward` — Claim your daily reward: {EMOJIS['manaorbs']} 100 mana orbs  
""", inline=False)

    embed.add_field(name="🛒 Icon Shop", value="""
`!shop` — View available icons  
`!buy <id>` — Buy an icon  
`!equip <id>` — Equip an icon  
""", inline=False)
    
    if ctx.author.id not in permission(1):
        submissions = f"""
`!send <id>` — Submit a real Geometry Dash level for review (you can earn creator points!) {EMOJIS['creatorpoints']}
"""
    else:
        submissions = f"""
`!send <id>` — Submit a real Geometry Dash level for review (unlimited use for helpers+) {EMOJIS['creatorpoints']}
`!sent-list` — View a list of sent levels that aren't added
"""
    embed.add_field(name="📤 Submissions", value=submissions, inline=False)

    if ctx.author.id in permission(2):
        embed.add_field(name="🔧 Admin Only", value="""
`!add-level <id> <name> <difficulty> <downloads> <likes> <time> <sender>` — Add a level to the bot's database (replace space with - in name)
`!delete-user <id>` — Delete a user's data from the bot  
`!delete-level <id>` — Delete a levels's data from the bot  
`!delete-sent <id>` — Delete a level ID that was sent on review
`!cheats <noclip/speedhack/icons> <on/off>` — Toggle cheat modes
`!manage <user/level> <id> <field> <data>` — Manages database's data
""", inline=False)
        
    if ctx.author.id in permission(4):
        embed.add_field(name="🔒 Bot Control", value="""
`!update-db <users/levels> <field> <default> <type>` — Updates and adds new field to old database's tables
`!set-db <users/levels> <field> <value>` — Sets a value in field for all database's datas
`!role <role> <add/remove> <id>` — Controls user's permissions role
`!data <name> <default> <type>` — Adds new bot data field to database
""", inline=False)

    embed.set_footer(text="🕹️ Bot by lyagushkeee6400 • Type !play <id> to start playing!")

    await ctx.send(embed=embed)

async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = member.id

    admins = botDB.get('admins') or []
    moderators = botDB.get('moderators') or []

    status = ""
    if user_id in moderators:
        status = EMOJIS['moderator'] + " "
    if user_id in (Config.OWNER + admins):
        status = EMOJIS['admin'] + " "

    data = userDB.get(user_id)

    if not data:
        await ctx.send("Profile not found.")
        return
    
    with userDB._connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users ORDER BY stars DESC")
        top_list = [row[0] for row in cursor.fetchall()]

    top = top_list.index(user_id) + 1 if user_id in top_list and data['stars'] > 0 else None
    rank = EMOJIS["rank" + (str(get_ranking(top)) if top else "7")]
    top_message = f"{rank} Top {top}" if top else f"{rank} Top ?"

    embed = discord.Embed(
        title=f"{status}{member.name}",
        description=(f"User ID: `{user_id}`\n{top_message}" if ctx.author.id in permission(2) else top_message),
        color=discord.Color.purple()
    )

    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

    stats = (
        f"{EMOJIS['star']} Stars: {data['stars']}\n"
        f"{EMOJIS['diamond']} Diamonds: {data['diamonds']}\n"
        f"{EMOJIS['goldcoin']} Gold Coins: {data['goldcoins']}\n"
        f"{EMOJIS['usercoin']} User Coins: {data['usercoins']}\n"
        f"{EMOJIS['demon']} Demons: {data['demons']}\n"
        f"{EMOJIS['creatorpoints']} Creator Points: {data['creatorpoints']}\n"
        f"{EMOJIS['manaorbs']} Mana Orbs: {data['orbs']}"
    )

    icons = " ".join([ICONS[i][data['icons'][i]] for i in range(8)])

    embed.add_field(name="Statistics", value=stats, inline=False)
    embed.add_field(name="Icons", value=icons, inline=False)
    embed.set_footer(text="Geometry Dash Bot • Profile")

    await ctx.send(embed=embed)

async def leaderboards(ctx, scope: str = "global"):
    if scope not in ("global", "local"):
        await ctx.send("Usage: `!leaderboards <global|local>`")
        return

    conn = sqlite3.connect("data/users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, stars FROM users WHERE stars > 0 ORDER BY stars DESC")
    all_global = cursor.fetchall()

    global_ranks = {}
    for rank, (uid, _) in enumerate(all_global, start=1):
        global_ranks[uid] = rank

    if scope == "global":
        rows = []
        for user_id, stars in all_global:
            user = bot.get_user(user_id)
            if not user:
                try:
                    user = await bot.fetch_user(user_id)
                except:
                    continue
            if user and not user.bot:
                rows.append((user_id, stars))
            if len(rows) >= 100:
                break

        title = "🌍 Global Leaderboard"

    else:
        member_ids = [m.id for m in ctx.guild.members if not m.bot]
        if not member_ids:
            await ctx.send("No players found on this server.")
            return

        placeholders = ",".join("?" * len(member_ids))
        cursor.execute(f"""
            SELECT user_id, stars FROM users
            WHERE user_id IN ({placeholders}) AND stars > 0
            ORDER BY stars DESC LIMIT 100
        """, member_ids)
        rows = cursor.fetchall()
        title = f"🏠 Local Leaderboard — {ctx.guild.name}"

    conn.close()

    if not rows:
        await ctx.send("No players found for this leaderboard.")
        return

    pages = []
    per_page = 10
    for page in range(0, len(rows), per_page):
        chunk = rows[page:page + per_page]
        description = ""
        for _, (user_id, stars) in enumerate(chunk):
            name = "Unknown"
            user = bot.get_user(user_id)
            if not user:
                try:
                    user = await bot.fetch_user(user_id)
                except:
                    pass
            if user:
                name = user.name

            global_rank = global_ranks.get(user_id)
            rank_emoji = EMOJIS.get("rank" + str(get_ranking(global_rank)), "") if global_rank else ""

            display_rank = f"#{global_rank}" if global_rank else "#???"

            description += f"`{display_rank}` {EMOJIS['star']}{stars} — **{name}** {rank_emoji}\n"

        pages.append(description)

    total_pages = len(pages)
    current_page = 0

    def get_embed(page):
        embed = discord.Embed(
            title=title,
            description=pages[page],
            color=discord.Color.dark_gold()
        )
        embed.set_footer(text=f"Top 100 players sorted by stars • Page {page+1}/{total_pages}")
        return embed

    message = await ctx.send(embed=get_embed(current_page))

    await message.add_reaction("◀️")
    await message.add_reaction("▶️")

    def check(reaction, user):
        return (
            user == ctx.author and
            str(reaction.emoji) in ["◀️", "▶️"] and
            reaction.message.id == message.id
        )

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            if str(reaction.emoji) == "▶️" and current_page + 1 < total_pages:
                current_page += 1
                await message.edit(embed=get_embed(current_page))
            elif str(reaction.emoji) == "◀️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=get_embed(current_page))

            await message.remove_reaction(reaction.emoji, user)
        except asyncio.TimeoutError:
            break

    try:
        await message.clear_reactions()
    except:
        pass

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

        users_level_progress = (played[str(i)]['record']) if str(i) in played else ""
        if users_level_progress == 100:
            users_level_progress = EMOJIS['checkmark']
        elif users_level_progress:
            users_level_progress = f"`{str(users_level_progress)}%`"
        else:
            users_level_progress = ""

        count_coins = (played[str(i)]['coins']) if str(i) in played else [0 for _ in range(data['coins'])]
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

async def visual(ctx, visual_type: str, state: str):
    user_id = ctx.author.id
    user_data = userDB.get(user_id)
    if not user_data:
        await ctx.send("❌ User not found in database.")
        return

    visuals = user_data.get("visuals", [0, 0])
    if len(visuals) < 2:
        visuals += [0] * (2 - len(visuals))

    state = state.lower()
    if state not in ["on", "off"]:
        await ctx.send("❌ State must be `on` or `off`.")
        return

    if visual_type.lower() == "extremes":
        visuals[0] = 1 if state == "on" else 0
        message = f"🎨 Extremes visuals have been turned **{'ON' if visuals[0] else 'OFF'}**."
        if visuals[0]:
            example = " ".join(EMOJIS[DIFFICULTIES[i]] for i in range(13, 20))
            message += f"\n✨ Example: {example}"
    elif visual_type.lower() == "defaults":
        visuals[1] = 1 if state == "on" else 0
        message = f"🎨 Defaults visuals have been turned **{'ON' if visuals[1] else 'OFF'}**."
        if visuals[1]:
            example = " ".join(EMOJIS[DIFFICULTIES[i]] for i in range(3, 9))
            message += f"\n✨ Example: {example}"
    else:
        await ctx.send("❌ Visual type must be `defaults` or `extremes`.")
        return

    userDB.update_field(user_id, "visuals", visuals)
    await ctx.send(message)

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

        users_level_data = (played[str(level_data['level_id'])]['record']) if str(level_data['level_id']) in played else None
        if users_level_data == 100:
            users_level_data = EMOJIS['checkmark']
        elif users_level_data:
            users_level_data = f"`{str(users_level_data)}%`"
        else:
            users_level_data = ""
        
        count_coins = (played[str(level_data['level_id'])]['coins']) if str(level_data['level_id']) in played else [0 for _ in range(level_data['coins'])]
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

        users_level_progress = (played[str(level_id)]['record']) if str(level_id) in played else ""
        if users_level_progress == 100:
            users_level_progress = EMOJIS['checkmark']
        elif users_level_progress:
            users_level_progress = f"{str(users_level_progress)}%"
        else:
            users_level_progress = ""

        count_coins = (played[str(level_id)]['coins']) if str(level_id) in played else [0 for _ in range(data['coins'])]
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
        if int(level_id) in MAIN_LEVELS:
            continue

        data = levelDB.get(level_id)
        if not data:
            continue

        emoji_difficulty = get_difficulty_visual(ctx.author.id, data['difficulty'])

        stars = min(data["difficulty"], 10)
        mana = ORBS[stars - 1] if stars > 0 else 0
        rate_emoji = EMOJIS['like'] if data['likes'] >= 0 else EMOJIS['dislike']

        played = userDB.get(ctx.author.id).get('played', {})
        users_level_progress = (played[str(level_id)]['record']) if str(level_id) in played else ""
        if users_level_progress == 100:
            users_level_progress = EMOJIS['checkmark']
        elif users_level_progress:
            users_level_progress = f"{str(users_level_progress)}%"
        else:
            users_level_progress = ""

        count_coins = (played[str(level_id)]['coins']) if str(level_id) in played else [0 for _ in range(data['coins'])]
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
