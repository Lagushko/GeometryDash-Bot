from modules import *
from bot import bot

async def daily(ctx):
    key = "daily"
    min_diff = 2
    max_diff = 9

    daily_data = botDB.get(key)
    current_id = daily_data[0] if daily_data and isinstance(daily_data, list) and len(daily_data) > 0 else None
    last_time = daily_data[1] if daily_data and isinstance(daily_data, list) and len(daily_data) > 1 else 0

    now = int(time.time())
    today = datetime.fromtimestamp(now).date()
    last_day = datetime.fromtimestamp(last_time).date()

    if current_id is None or today != last_day:
        with levelDB._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level_id, difficulty FROM levels")
            all_levels = cursor.fetchall()

        random.shuffle(all_levels)

        selected_level_id = None
        for level_id, difficulty in all_levels:
            if (
                min_diff <= difficulty <= max_diff
                and level_id not in MAIN_LEVELS
                and level_id != current_id
            ):
                selected_level_id = level_id
                botDB.update_field(key, [selected_level_id, now])
                break
        else:
            await ctx.send("❌ Failed to select daily level.")
            return

        current_id = selected_level_id

    level = levelDB.get(current_id)
    if not level:
        await ctx.send("❌ Failed to find daily level.")
        return

    emoji = get_difficulty_visual(ctx.author.id, level['difficulty'])
    stars = min(level["difficulty"], 10)
    mana = ORBS[stars - 1] if stars > 0 else 0
    diamonds = DIAMONDS[stars - 1] if stars > 0 else 0
    rate_emoji = EMOJIS['like'] if level['likes'] >= 0 else EMOJIS['dislike']

    embed = discord.Embed(
        title=f"📅 Daily Level",
        color=discord.Color.orange()
    )
    embed.description = (
        f"`ID {level['level_id']}:`\n"
        f"{emoji} {level['name']}\n"
        f"{EMOJIS['star']}{stars} {EMOJIS['diamond']}{diamonds} {EMOJIS['manaorbs']}{mana}\n"
        f"{EMOJIS['download']}{level['downloads']} {rate_emoji}{level['likes']} {EMOJIS['time']}{level_time(level['time'])}"
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

        selected_level_id = None
        for level_id, difficulty in all_levels:
            if (
                min_diff <= difficulty <= max_diff
                and level_id not in MAIN_LEVELS
                and level_id != current_id
            ):
                selected_level_id = level_id
                now = datetime.now()
                monday = now - timedelta(days=now.weekday())
                monday_midnight = datetime(monday.year, monday.month, monday.day)
                now_timestamp = int(monday_midnight.timestamp())
                botDB.update_field(key, [selected_level_id, now_timestamp])
                break
        else:
            await ctx.send("❌ Failed to select daily level.")
            return

        current_id = selected_level_id

    level = levelDB.get(current_id)
    if not level:
        await ctx.send("❌ Failed to find weekly level.")
        return

    emoji = get_difficulty_visual(ctx.author.id, level['difficulty'])
    stars = min(level["difficulty"], 10)
    mana = ORBS[stars - 1] if stars > 0 else 0
    diamonds = DIAMONDS[stars - 1] if stars > 0 else 0
    rate_emoji = EMOJIS['like'] if level['likes'] >= 0 else EMOJIS['dislike']

    embed = discord.Embed(
        title=f"📅 Weekly Level",
        color=discord.Color.blue()
    )
    embed.description = (
        f"`ID {level['level_id']}:`\n"
        f"{emoji} {level['name']}\n"
        f"{EMOJIS['star']}{stars} {EMOJIS['diamond']}{diamonds} {EMOJIS['manaorbs']}{mana}\n"
        f"{EMOJIS['download']}{level['downloads']} {rate_emoji}{level['likes']} {EMOJIS['time']}{level_time(level['time'])}"
    )

    await ctx.send(embed=embed)

async def reward(ctx):
    user_id = ctx.author.id
    user_data = userDB.get(user_id)

    now = int(time.time())
    last_claim = user_data.get("last_reward_time", 0)

    if now - last_claim >= 86400:
        new_orbs = user_data["orbs"] + 100
        userDB.update_field(user_id, "orbs", new_orbs)
        userDB.update_field(user_id, "last_reward_time", now)

        embed = discord.Embed(
            title="🎁 Daily Reward",
            description=f"You received **100** {EMOJIS['manaorbs']} Mana Orbs!",
            color=discord.Color.green()
        )
        embed.set_footer(text="Come back tomorrow for more rewards.")
        await ctx.send(embed=embed)
    else:
        remaining = 86400 - (now - last_claim)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60

        embed = discord.Embed(
            title="⏳ Too Soon!",
            description=f"You've already claimed your reward.\nTry again in {hours:02d}h {minutes:02d}m.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
