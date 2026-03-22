from .__utils__ import *
from bot import bot

async def help(ctx):
    main_embed = discord.Embed(
        title=f"{EMOJIS['demon']} Welcome to Geometry Dash Bot! {EMOJIS['demon']}",
        description=(
            f"This is a **Geometry Dash simulation bot**! {EMOJIS['like']} Play, collect stars, unlock icons, and compete with others!\n\n"
            "**React with an emoji to view a help section:**\n" +
            "\n".join([f"{emoji} — {data['title']}" for emoji, data in HELP_SECTIONS.items()
                      if 'condition' not in data or data['condition'](ctx)])
        ),
        color=discord.Color.blue()
    )
    main_embed.set_footer(text="🕹️ Bot by lagushkeee6400 • Type !play <id> to start playing!")

    msg = await ctx.send(embed=main_embed)

    for emoji in HELP_SECTIONS.keys():
        if 'condition' not in HELP_SECTIONS[emoji] or HELP_SECTIONS[emoji]['condition'](ctx):
            await msg.add_reaction(emoji)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in HELP_SECTIONS and reaction.message.id == msg.id

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            await msg.remove_reaction(reaction.emoji, user)

            section = HELP_SECTIONS[str(reaction.emoji)]
            content = section['content'](ctx) if callable(section['content']) else section['content']
            new_embed = discord.Embed(
                title=f"{EMOJIS['demon']} Welcome to Geometry Dash Bot! {EMOJIS['demon']}",
                description=(
                    f"This is a **Geometry Dash simulation bot**! {EMOJIS['like']} Play, collect stars, unlock icons, and compete with others!\n\n"
                    f"**{str(reaction.emoji)} {section['title']}:** {content}\n"
                    "**React with an emoji to view a help section:**\n" +
                    "\n".join([f"{emoji} — {data['title']}" for emoji, data in HELP_SECTIONS.items()
                            if 'condition' not in data or data['condition'](ctx)])
                ),
                color=discord.Color.blue()
            )
            new_embed.set_footer(text="🕹️ Bot by lagushkeee6400 • Type !play <id> to start playing!")

            await msg.edit(embed=new_embed)

        except asyncio.TimeoutError:
            break

async def link(ctx):
    embed = discord.Embed(
        title="🤖 Invite the Bot",
        description=f"[Click here to add the bot to your server]({Config.BOT_URL})",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Thanks for using Geometry Dash Bot!")
    await ctx.send(embed=embed)

async def profile(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = member.id

    admins = botDB.get('admins') or []
    moderators = botDB.get('moderators') or []
    devs = botDB.get('devs') or []

    status = ""
    if user_id in moderators:
        status = EMOJIS['moderator'] + " "
    if user_id in (Config.OWNER + admins):
        status = EMOJIS['admin'] + " "
    if user_id in devs:
        status = "DEV " + EMOJIS['creatorpoints'] + " "

    data = userDB.get(user_id)

    if not data:
        await ctx.send("Profile not found.")
        return
    
    with userDB._connect() as conn:
        cursor = conn.cursor()
        devs = botDB.get("devs") or []
        if devs:
            placeholders = ",".join("?" * len(devs))
            cursor.execute(f"SELECT user_id FROM users WHERE user_id NOT IN ({placeholders}) ORDER BY stars DESC", devs)
        else:
            cursor.execute("SELECT user_id FROM users ORDER BY stars DESC")
        top_list = [row[0] for row in cursor.fetchall()]

    top = top_list.index(user_id) + 1 if user_id in top_list and data['stars'] > 0 else None
    rank = EMOJIS["rank" + (str(get_ranking(top)) if top else "7")]
    if user_id in devs:
        top_message = "❗ Developer accounts are out of top"
    else:
        top_message = f"{rank} Top {top}" if top else f"{rank} Top ?"

    embed = discord.Embed(
        title=f"{status}{member.name}",
        description=(f"🆔 User ID: `{user_id}`\n{top_message}" if ctx.author.id in permission(2) else top_message),
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

    devs = botDB.get("devs") or []
    if devs:
        placeholders = ",".join("?" * len(devs))
        cursor.execute(f"SELECT user_id, stars FROM users WHERE stars > 0 AND user_id NOT IN ({placeholders}) ORDER BY stars DESC", devs)
    else:
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
            example = " ".join(EMOJIS[DIFFICULTIES[i]] for i in [13, 15, 17, 19, 21, 24, 27])
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
