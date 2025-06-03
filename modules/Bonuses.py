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
            ):
                level = levelDB.get(level_id)
                if level:
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

    emoji = get_difficulty_visual(ctx.author.id, level['difficulty'])
    stars = min(level["difficulty"], 10)
    mana = ORBS[stars - 1] if stars > 0 else 0
    diamonds = DIAMONDS[stars - 1] if stars > 0 else 0
    rate_emoji = EMOJIS['like'] if level['likes'] >= 0 else EMOJIS['dislike']

    played = userDB.get(ctx.author.id)['played']
    level_cid = key + str(current_id)

    users_level_data = (played[level_cid]['record']) if level_cid in played else None
    if users_level_data == 100:
        users_level_data = EMOJIS['checkmark']
    elif users_level_data:
        users_level_data = f"`{str(users_level_data)}%`"
    else:
        users_level_data = ""
    
    count_coins = (played[level_cid]['coins']) if level_cid in played else [0 for _ in range(level['coins'])]
    level_coins = " "
    if len(count_coins) > 0:
        level_coins = "".join(EMOJIS['usercoin'] if coin else EMOJIS['lockedcoin'] for coin in count_coins) + " "

    embed = discord.Embed(
        title="📅 Daily Level",
        color=discord.Color.orange()
    )
    embed.description = (
        f"`ID {key}:`\n"
        f"{emoji} {level['name']} {level_coins}{users_level_data}\n"
        f"{TAB*2}{EMOJIS['star']}{stars} {EMOJIS['diamond']}{diamonds} {EMOJIS['manaorbs']}{mana}\n"
        f"{TAB*2}{EMOJIS['download']}{level['downloads']} {rate_emoji}{level['likes']} {EMOJIS['time']}{level_time(level['time'])}"
    )

    await ctx.send(embed=embed)

async def weekly(ctx):
    key = "weekly"
    min_diff = 10
    max_diff = 13

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
            ):
                level = levelDB.get(level_id)
                if level:
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

    emoji = get_difficulty_visual(ctx.author.id, level['difficulty'])
    stars = min(level["difficulty"], 10)
    mana = ORBS[stars - 1] if stars > 0 else 0
    diamonds = DIAMONDS[stars - 1] if stars > 0 else 0
    rate_emoji = EMOJIS['like'] if level['likes'] >= 0 else EMOJIS['dislike']

    played = userDB.get(ctx.author.id)['played']
    level_cid = key + str(current_id)

    users_level_data = (played[level_cid]['record']) if level_cid in played else None
    if users_level_data == 100:
        users_level_data = EMOJIS['checkmark']
    elif users_level_data:
        users_level_data = f"`{str(users_level_data)}%`"
    else:
        users_level_data = ""
    
    count_coins = (played[level_cid]['coins']) if level_cid in played else [0 for _ in range(level['coins'])]
    level_coins = " "
    if len(count_coins) > 0:
        level_coins = "".join(EMOJIS['usercoin'] if coin else EMOJIS['lockedcoin'] for coin in count_coins) + " "

    embed = discord.Embed(
        title="📅 Weekly Level",
        color=discord.Color.orange()
    )
    embed.description = (
        f"`ID {key}:`\n"
        f"{emoji} {level['name']} {level_coins}{users_level_data}\n"
        f"{TAB*2}{EMOJIS['star']}{stars} {EMOJIS['diamond']}{diamonds} {EMOJIS['manaorbs']}{mana}\n"
        f"{TAB*2}{EMOJIS['download']}{level['downloads']} {rate_emoji}{level['likes']} {EMOJIS['time']}{level_time(level['time'])}"
    )

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
            title=f"{EMOJIS[DIFFICULTIES[pdata['difficulty']-1]]} {pdata['name']} reward",
            description=f"+ {EMOJIS['star']} {stars} Stars\n+ {EMOJIS['goldcoin']} {coins} Gold Coins"
        )

        await ctx.send(embed=embed)
        return
    else:
        if pack_id:
            data = map_packs[pack_id]
            levels = [levelDB.get(str(x)) for x in data['levels']]

            field_text = ""

            for level_data in levels:
                lid = level_data['level_id']
                user_record = played[lid]['record'] if lid in played else None
                if user_record == 100:
                    user_record = EMOJIS['checkmark']
                elif user_record is not None:
                    user_record = f"`{user_record}%`"
                else:
                    user_record = ""

                coins_got = played[lid]['coins'] if lid in played else [0] * level_data['coins']
                level_coins = "".join(
                    EMOJIS['usercoin'] if coin else EMOJIS['lockedcoin'] for coin in coins_got
                ) + " " if coins_got else " "

                rate_emoji = EMOJIS['like'] if level_data['likes'] >= 0 else EMOJIS['dislike']
                field_text += (
                    f"`ID {lid}:`\n"
                    f"{EMOJIS[DIFFICULTIES[level_data['difficulty']-1]]} {level_data['name']} {level_coins}{user_record}\n"
                    f"{TAB*2}{EMOJIS['star']}{min(10, level_data['difficulty'])} "
                    f"{EMOJIS['manaorbs']}{ORBS[min(10, level_data['difficulty'])]}\n"
                    f"{TAB*2}{EMOJIS['download']}{level_data['downloads']} {rate_emoji}{level_data['likes']} "
                    f"{EMOJIS['time']}{level_time(level_data['time'])}\n\n"
                )

            embed = discord.Embed(
                title=f"{EMOJIS[DIFFICULTIES[data['difficulty']-1]]} {data['name']}", 
                description=field_text,
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="📁 Map Packs", color=discord.Color.green())
            description = ""

            for pid, pdata in map_packs.items():
                levels = [levelDB.get(str(lid)) for lid in pdata['levels']]
                total = len(levels)
                completed = sum(1 for lvl in levels if lvl['level_id'] in played and played[lvl['level_id']]['record'] == 100)
                check = EMOJIS['checkmark'] if f"mappack{pid}" in user_data['collected'] else ""

                avg_difficulty = round(sum(lvl['difficulty'] for lvl in levels) / total)
                stars = f"{EMOJIS['star']}{min(10, avg_difficulty)}"

                coins = f"{EMOJIS['goldcoin']}{(1 if pdata['difficulty'] < 10 else 2)}"

                description += (
                    f"`ID {pid}:`\n{EMOJIS[DIFFICULTIES[pdata['difficulty']-1]]} {pdata['name']} "
                    f"({completed}/{total}) {check}\n{TAB*2}{stars} {coins}\n\n"
                )

            embed.description = description
            await ctx.send(embed=embed)