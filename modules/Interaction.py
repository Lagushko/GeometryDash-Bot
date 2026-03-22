from .__utils__ import *
from bot import bot

async def join(ctx, level_id: str):
    guild_id = ctx.guild.id
    user_id = ctx.author.id

    user_data = userDB.get(user_id)

    if guild_id not in current_levels:
        current_levels[guild_id] = {}

    level = levelDB.get(level_id)
    if not level:
        await ctx.send("❌ Level not found. Please check the ID.")
        return

    played = user_data.get("played", {})
    level_id = str(level_id)
    edited_level_id = level_id
    if level_id in ['weekly', 'daily']:
        edited_level_id += botDB.get(level_id)[0]
    if edited_level_id not in played:
        played[edited_level_id] = {
            "attempts": 0,
            "record": 0,
            "rated": False,
            "coins": [0 for _ in range(level['coins'])],
        }
        userDB.update_field(user_id, "played", played)

        level["downloads"] = level.get("downloads", 0) + 1
        levelDB.update_field(level_id, "downloads", level["downloads"])

    current_levels[guild_id][user_id] = level_id

    emoji = get_difficulty_visual(user_id, level['difficulty'])

    embed = discord.Embed(
        title=f"🎮 Joined Level: {emoji} {level['name']}",
        description=f"Level ID: `{level_id}`\nUse `!quit` to leave or `!play` to start playing.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

async def quit(ctx):
    guild_id = ctx.guild.id
    user_id = ctx.author.id

    if guild_id not in current_levels or user_id not in current_levels[guild_id]:
        await ctx.send("❌ You are not currently playing any level in this server.")
        return

    level_id = current_levels[guild_id].pop(user_id)
    level = levelDB.get(level_id)

    name = level["name"] if level else "Unknown"
    emoji = get_difficulty_visual(user_id, level['difficulty'])

    embed = discord.Embed(
        title="👋 Exited Level",
        description=f"You have exited level {emoji} **{name}** (ID: `{level_id}`).",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

async def play(ctx, level_id: str = None):
    guild_id = ctx.guild.id
    user_id = ctx.author.id

    userDB.ensure(user_id)
    user_data = userDB.get(user_id)

    if level_id is not None:
        level = levelDB.get(level_id)
        if not level:
            await ctx.send("❌ Level not found. Please check the ID.")
            return
    else:
        if guild_id not in current_levels or user_id not in current_levels[guild_id]:
            await ctx.send("❌ You haven't joined any level. Use `!join <id>` or `!play <id>`.")
            return
        level_id = current_levels[guild_id][user_id]
        level = levelDB.get(level_id)

    if not hasattr(bot, "play_locks"):
        bot.play_locks = set()

    if user_id in bot.play_locks:
        await ctx.send("⏳ You're already playing a level.")
        return

    bot.play_locks.add(user_id)

    played = user_data.get("played", {})
    edited_level_id = level_id
    if level_id in ['weekly', 'daily']:
        edited_level_id += botDB.get(level_id)[0]
    if edited_level_id not in played:
        played[edited_level_id] = {
            "attempts": 0,
            "record": 0,
            "rated": False,
            "coins": [0 for _ in range(level['coins'])],
        }
        level["downloads"] = level.get("downloads", 0) + 1
        levelDB.update_field(level_id, "downloads", level["downloads"])
    played[edited_level_id]["attempts"] += 1
    attempt_num = played[edited_level_id]["attempts"]
    userDB.update_field(user_id, "played", played)

    cheat = cheat_modes.get(user_id, {})
    speedhack = cheat.get("speedhack", 0) == 1
    noclip = cheat.get("noclip", 0) == 1

    if noclip:
        percent = 100
    else:
        nickname = ctx.author.display_name if ctx.author else f"User {user_id}"
        percent = predict_level_completion(level, user_data, nickname=nickname)

    sim_time = max(round((level.get("time", 60) * (percent / 100)) / 10), 1)

    difficulty_emoji = get_difficulty_visual(user_id, level['difficulty'])
    embed = discord.Embed(
        title=f"{difficulty_emoji} {level['name']} `{played[edited_level_id]['record']}%`",
        description=f"🎮 Attempt {attempt_num}\n{EMOJIS['time']} Playing... 0s",
        colour=discord.Colour.orange()
    )
    msg = await ctx.reply(embed=embed)

    if not speedhack:
        for i in range(1, sim_time + 1):
            await asyncio.sleep(1)
            embed.description = f"🎮 Attempt {attempt_num}\n{EMOJIS['time']} Playing... {i}s"
            await msg.edit(embed=embed)

    response = f"🎮 Attempt {attempt_num}\n💥 **{percent}%**"
    new_best = False

    if percent > played[edited_level_id]["record"]:
        played[edited_level_id]["record"] = percent
        userDB.update_field(user_id, "played", played)
        new_best = True
        response += " **New Best! 🔥**"

    if percent == 100:
        response += f"\n\n{EMOJIS['checkmark']} **Level Completed!** "
        coins_reward = []
        coins_reward = [random.randint(0, 1) for _ in range(level['coins'])]
        all_coins = [max(a, b) for a, b in zip(played[edited_level_id]['coins'], coins_reward)]
        new_coins = max(0, all_coins.count(1) - played[edited_level_id]['coins'].count(1))

        played[edited_level_id]['coins'] = all_coins.copy()

        coin_type = 'goldcoin' if level['level_id'] in MAIN_LEVELS else 'usercoin'
        user_data[coin_type + "s"] += new_coins

        userDB.update_field(user_id, "played", user_data["played"])
        userDB.update_field(user_id, coin_type + "s", user_data[coin_type + "s"])
        if len(coins_reward) > 0:
            response += " ".join([(EMOJIS[coin_type]) if coin else EMOJIS["lockedcoin"] for coin in all_coins])

        if new_best:
            stars = min(level['difficulty'], 10)
            orb_reward = ORBS[stars - 1]
            star_reward = stars
            diamond_reward = 0

            user_data["orbs"] += orb_reward
            user_data["stars"] += star_reward
            userDB.update_field(user_id, "orbs", user_data["orbs"])
            userDB.update_field(user_id, "stars", user_data["stars"])

            if str(level_id) in ["daily", "weekly"]:
                diamond_reward = DIAMONDS[stars - 1]
                user_data["diamonds"] += diamond_reward
                userDB.update_field(user_id, "diamonds", user_data["diamonds"])

            if stars >= 10:
                user_data["demons"] += 1
                userDB.update_field(user_id, "demons", user_data["demons"])

            current_difficulty = level['difficulty']
            if user_data['hardest'][0] < current_difficulty:
                user_data['hardest'] = [int(current_difficulty), 1]
            elif user_data['hardest'][0] == int(current_difficulty):
                user_data['hardest'][1] += 1
            userDB.update_field(user_id, "hardest", user_data["hardest"])

            response += "\n"
            
            response += f"+ {EMOJIS['star']} {star_reward} Stars\n"
            if diamond_reward:
                response += f"+ {EMOJIS['diamond']} {diamond_reward} Diamonds\n"
            response += f"+ {EMOJIS['manaorbs']} {orb_reward} Mana Orbs\n"
            if stars >= 10:
                response += f"+ {EMOJIS['demon']} 1 Demon\n"

    final_embed = discord.Embed(
        title=f"{difficulty_emoji} {level['name']} `{str(played[edited_level_id]['record'])}%`",
        description=response,
        colour=discord.Colour.green() if percent == 100 else discord.Colour.blue()
    )
    await msg.edit(embed=final_embed)

    bot.play_locks.remove(user_id)

async def like(ctx, level_id: str):
    user_id = ctx.author.id
    user_data = userDB.get(user_id)

    played = user_data.get("played", {})
    edited_level_id = level_id
    if level_id in ['weekly', 'daily']:
        edited_level_id += botDB.get(level_id)[0]
    level_played = played.get(edited_level_id)

    if not level_played or level_played.get("attempts", 0) <= 0:
        await ctx.send("❗ You must play this level at least once before liking it.")
        return

    if level_played.get("rated"):
        await ctx.send("✅ You have already rated this level.")
        return

    level = levelDB.get(level_id)
    if not level:
        await ctx.send("❌ Level not found.")
        return

    new_likes = level["likes"] + 1
    levelDB.update_field(level_id, "likes", new_likes)

    level_played["rated"] = True
    played[edited_level_id] = level_played
    userDB.update_field(user_id, "played", played)

    embed = discord.Embed(
        title=f"{EMOJIS['like']} Liked!",
        description=f"You liked **{level['name']}**.\nTotal Likes: `{new_likes}`",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

async def dislike(ctx, level_id: str):
    user_id = ctx.author.id
    user_data = userDB.get(user_id)

    played = user_data.get("played", {})
    edited_level_id = level_id
    if level_id in ['weekly', 'daily']:
        edited_level_id += botDB.get(level_id)[0]
    level_played = played.get(edited_level_id)

    if not level_played or level_played.get("attempts", 0) <= 0:
        await ctx.send("❗ You must play this level at least once before disliking it.")
        return

    if level_played.get("rated"):
        await ctx.send("✅ You have already rated this level.")
        return

    level = levelDB.get(level_id)
    if not level:
        await ctx.send("❌ Level not found.")
        return

    new_likes = level["likes"] - 1
    levelDB.update_field(level_id, "likes", new_likes)

    level_played["rated"] = True
    played[edited_level_id] = level_played
    userDB.update_field(user_id, "played", played)

    embed = discord.Embed(
        title=f"{EMOJIS['dislike']} Disliked!",
        description=f"You disliked **{level['name']}**.\nTotal Likes: `{new_likes}`",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)
