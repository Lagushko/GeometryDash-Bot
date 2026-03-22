from .__utils__ import *
from bot import bot

async def daily(ctx):
    key = "daily"
    min_diff = 2
    max_diff = 9

    daily_data = botDB.get(key)
    current_id = daily_data[0] if daily_data and len(daily_data) > 0 else None
    last_time = daily_data[1] if daily_data and len(daily_data) > 1 else 0

    now = int(time.time())
    today = datetime.fromtimestamp(now).date()
    last_day = datetime.fromtimestamp(last_time).date()

    if current_id is None or today != last_day:
        with levelDB._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level_id, difficulty FROM levels")
            all_levels = cursor.fetchall()

        random.shuffle(all_levels)

        for level_id, difficulty in all_levels:
            if (
                min_diff <= difficulty <= max_diff
                and level_id not in MAIN_LEVELS
                and level_id != current_id
                and level_id != key
            ):
                level = levelDB.get(level_id)
                if level:
                    levelDB.fix_duplicates(key)
                    levelDB.add("daily", level["name"], level["difficulty"], level["downloads"], level["likes"], level["time"], level["coins"], level["sender"])
                    botDB.update_field(key, [level_id, now])
                    current_id = level_id
                    break
        else:
            await ctx.send("❌ Failed to select daily level.")
            return

    level = levelDB.get("daily")
    if not level:
        await ctx.send("❌ Failed to load daily level.")
        return
    
    played = userDB.get(ctx.author.id)['played']

    level_cid = key + str(current_id)
    level['level_id'] = level_cid

    level_str = level_markdown(ctx.author.id, played, level, custom_id="daily")

    embed = discord.Embed(
        title="📅 Daily Level",
        color=discord.Color.orange()
    )
    embed.description = level_str

    await ctx.send(embed=embed)

async def weekly(ctx):
    key = "weekly"
    min_diff = 10
    max_diff = 12

    weekly_data = botDB.get(key)
    current_id = weekly_data[0] if weekly_data and len(weekly_data) > 0 else None
    last_time = weekly_data[1] if weekly_data and len(weekly_data) > 1 else 0

    now = datetime.now().date()
    last_date = datetime.fromtimestamp(last_time).date()

    if current_id is None or (now - last_date).days >= 7:
        with levelDB._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level_id, difficulty FROM levels")
            all_levels = cursor.fetchall()

        random.shuffle(all_levels)

        for level_id, difficulty in all_levels:
            if (
                min_diff <= difficulty <= max_diff
                and level_id not in MAIN_LEVELS
                and level_id != current_id
                and level_id != key
            ):
                level = levelDB.get(level_id)
                if level:
                    levelDB.fix_duplicates(key)
                    levelDB.add("weekly", level["name"], level["difficulty"], level["downloads"], level["likes"], level["time"], level["coins"], level["sender"])
                    monday = datetime.now() - timedelta(days=datetime.now().weekday())
                    monday_midnight = datetime(monday.year, monday.month, monday.day)
                    now_timestamp = int(monday_midnight.timestamp())
                    botDB.update_field(key, [level_id, now_timestamp])
                    current_id = level_id
                    break
        else:
            await ctx.send("❌ Failed to select weekly level.")
            return

    level = levelDB.get("weekly")
    if not level:
        await ctx.send("❌ Failed to load weekly level.")
        return

    played = userDB.get(ctx.author.id)['played']

    level_cid = key + str(current_id)
    level['level_id'] = level_cid

    level_str = level_markdown(ctx.author.id, played, level, custom_id="weekly")

    embed = discord.Embed(
        title="📅 Weekly Level",
        color=discord.Color.orange()
    )
    embed.description = level_str

    await ctx.send(embed=embed)

async def reward(ctx):
    user_id = ctx.author.id
    user_data = userDB.get(user_id)

    now = int(time.time())
    last_rewards = user_data.get("last_reward_time", [0, 0])
    small_ready = now - last_rewards[0] >= 14400
    large_ready = now - last_rewards[1] >= 86400

    embed = discord.Embed(
        title="🎁 Chest Rewards",
        color=discord.Color.gold()
    )

    small_value = ""
    if small_ready:
        manaorbs = random.randint(4, 10) * 5
        diamonds = random.randint(1, 4)
        small_value += f"+ {EMOJIS['manaorbs']} {manaorbs} Mana Orbs\n"
        small_value += f"+ {EMOJIS['diamond']} {diamonds} Diamonds"
        userDB.update_field(user_id, "orbs", user_data["orbs"] + manaorbs)
        userDB.update_field(user_id, "diamonds", user_data.get("diamonds", 0) + diamonds)
        last_rewards[0] = now
    else:
        remaining = 14400 - (now - last_rewards[0])
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60
        small_value += f"{EMOJIS['time']} You can open it in {hours}h {minutes}m {seconds}s"
    embed.add_field(name=f"{EMOJIS['smallchest']} Small Chest", value=small_value, inline=False)

    large_value = ""
    if large_ready:
        manaorbs = random.randint(4, 12) * 25
        diamonds = random.randint(4, 10)
        large_value += f"+ {EMOJIS['manaorbs']} {manaorbs} Mana Orbs\n"
        large_value += f"+ {EMOJIS['diamond']} {diamonds} Diamonds"
        userDB.update_field(user_id, "orbs", userDB.get(user_id)["orbs"] + manaorbs)
        userDB.update_field(user_id, "diamonds", userDB.get(user_id).get("diamonds", 0) + diamonds)
        last_rewards[1] = now
    else:
        remaining = 86400 - (now - last_rewards[1])
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60
        large_value += f"{EMOJIS['time']} You can open it in {hours}h {minutes}m {seconds}s"
    embed.add_field(name=f"{EMOJIS['largechest']} Large Chest", value=large_value, inline=False)

    userDB.update_field(user_id, "last_reward_time", last_rewards)

    await ctx.send(embed=embed)

async def map_pack(ctx, pack_id: str = None, collect: str = None):
    user_data = userDB.get(ctx.author.id)
    played = user_data['played']
    map_packs = botDB.get("mappacks")

    if pack_id and pack_id not in map_packs:
        await ctx.send(f"❌ Map pack with ID: `{pack_id}` doesn't exist.")
        return

    if collect == "collect":
        pdata = map_packs[pack_id]
        levels = [levelDB.get(str(lid)) for lid in pdata['levels']]
        total = len(levels)
        completed = [lvl for lvl in levels if lvl['level_id'] in played and played[lvl['level_id']]['record'] == 100]

        if len(completed) < total:
            await ctx.send(f"❌ You have only {len(completed)}/{total} levels completed in this map pack. Complete all to take your reward.")
            return

        if f"mappack{pack_id}" in user_data['collected']:
            await ctx.send(f"❌ You already collected reward from this map pack.")
            return

        avg_difficulty = round(sum(lvl['difficulty'] for lvl in levels) / total)
        stars = min(10, avg_difficulty)
        coins = (1 if pdata['difficulty'] < 10 else 2)

        user_data['collected'].append(f"mappack{pack_id}")
        user_data['goldcoins'] += coins
        user_data['stars'] += stars

        userDB.update_field(ctx.author.id, 'collected', user_data['collected'])
        userDB.update_field(ctx.author.id, 'goldcoins', user_data['goldcoins'])
        userDB.update_field(ctx.author.id, 'stars', user_data['stars'])

        embed = discord.Embed(
            title=f"{EMOJIS[DIFFICULTIES[pdata['difficulty'] - 1]]} {pdata['name']} reward",
            description=f"+ {EMOJIS['star']} {stars} Stars\n+ {EMOJIS['goldcoin']} {coins} Gold Coins"
        )
        await ctx.send(embed=embed)
        return

    if pack_id:
        data = map_packs[pack_id]
        levels = [levelDB.get(str(x)) for x in data['levels']]
        field_text = ""

        for level_data in levels:
            level_str = level_markdown(ctx.author.id, played, level_data)
            field_text += level_str + "\n\n"

        embed = discord.Embed(
            title=f"📁 {data['name']}",
            description=field_text,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    else:
        pack_list = []

        for pid, pdata in map_packs.items():
            levels = [levelDB.get(str(lid)) for lid in pdata['levels']]
            total = len(levels)
            avg_diff = round(sum(lvl['difficulty'] for lvl in levels) / total)
            stars = min(10, avg_diff)
            pack_list.append((avg_diff, stars, pid, pdata, levels, total))

        pack_list.sort(key=lambda x: (x[0], x[1]))

        pages = []
        page = []
        for avg_diff, stars, pid, pdata, levels, total in pack_list:
            completed = sum(1 for lvl in levels if lvl['level_id'] in played and played[lvl['level_id']]['record'] == 100)
            check = EMOJIS['checkmark'] if f"mappack{pid}" in user_data['collected'] else ""
            coins = f"{EMOJIS['goldcoin']}{(1 if pdata['difficulty'] < 10 else 2)}"

            entry = (
                f"`ID {pid}:`\n{EMOJIS[DIFFICULTIES[pdata['difficulty'] - 1]]} {pdata['name']} "
                f"({completed}/{total}) {check}\n{TAB * 2}{EMOJIS['star']}{stars} {coins}\n\n"
            )
            page.append(entry)
            if len(page) == 5:
                pages.append(page)
                page = []
        if page:
            pages.append(page)

        current = 0

        def make_embed(index):
            embed = discord.Embed(
                title="📁 Map Packs",
                description="".join(pages[index]),
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Page {index + 1}/{len(pages)}")
            return embed

        message = await ctx.send(embed=make_embed(current))
        for emoji in ["⏮", "⬅️", "➡️", "⏭"]:
            await message.add_reaction(emoji)

        def check(reaction, user):
            return (
                user == ctx.author and
                reaction.message.id == message.id and
                str(reaction.emoji) in ["⬅️", "➡️", "⏮", "⏭"]
            )

        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                emoji = str(reaction.emoji)

                if emoji == "⬅️" and current > 0:
                    current -= 1
                elif emoji == "➡️" and current < len(pages) - 1:
                    current += 1
                elif emoji == "⏮":
                    current = 0
                elif emoji == "⏭":
                    current = len(pages) - 1

                await message.edit(embed=make_embed(current))
                await message.remove_reaction(reaction.emoji, user)
            except asyncio.TimeoutError:
                break
