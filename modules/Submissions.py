from modules import *
from bot import bot

async def send(ctx, level_id: int):
    user_id = ctx.author.id
    user_name = ctx.author.name

    userDB.ensure(user_id)
    user_data = userDB.get(user_id)
    now = int(time.time())

    last_send = user_data.get("last_send_time", 0)
    cooldown = 86400

    if now - last_send < cooldown and user_id not in permission(1):
        remaining = cooldown - (now - last_send)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        await ctx.send(f"⏳ You can use this command again in {hours}h {minutes}m.")
        return

    try:
        admin_id = Config.OWNER[0]
        admin = await bot.fetch_user(admin_id)
        await admin.send(
            f"📨 User **{user_name}** (ID: `{user_id}`) has submitted level ID: `{level_id}`"
        )
        await ctx.send("✅ Your level has been submitted and sent to the admin!")

        userDB.update_field(user_id, "last_send_time", now)

        current_list = botDB.get("send") or []
        current_list.append([level_id, user_id])
        botDB.update_field("send", current_list)

    except Exception as e:
        await ctx.send("❌ Failed to notify the admin.")
        print(f"DM send error: {e}")

async def sent_list(ctx):
    if ctx.author.id not in permission(1):
        return

    sent_data = botDB.get("send") or []
    if not sent_data:
        await ctx.send("📭 No levels have been submitted yet.")
        return

    sent_data = list(reversed(sent_data))

    entries_per_page = 10
    pages = [sent_data[i:i + entries_per_page] for i in range(0, len(sent_data), entries_per_page)]
    total_pages = len(pages)
    current_page = 0

    async def get_embed(index):
        embed = discord.Embed(
            title="📨 Sent Levels",
            description="",
            color=discord.Color.blurple()
        )

        page = pages[index]
        lines = []
        for level_id, user_id in page:
            try:
                user = await bot.fetch_user(user_id)
                user_name = user.name
            except:
                user_name = "UnknownUser"

            admins = botDB.get('admins') or []
            moderators = botDB.get('moderators') or []
            helpers = botDB.get('helpers') or []

            status = 0
            if user_id in helpers:
                status = 1
            if user_id in moderators:
                status = 2
            if user_id in (Config.OWNER + admins):
                status = 3

            emoji = ["", EMOJIS['creatorpoints'], EMOJIS['moderator'], EMOJIS['admin']][status]
            
            lines.append(f"`{level_id}`\nby: {user_name} {emoji}\n(`{user_id}`)")

        embed.description = "\n\n".join(lines)
        embed.set_footer(text=f"Page {index + 1}/{total_pages}")
        return embed

    message = await ctx.send(embed=await get_embed(current_page))

    if total_pages <= 1:
        return

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

            if str(reaction.emoji) == "⬅️" and current_page > 0:
                current_page -= 1
                await message.edit(embed=await get_embed(current_page))
            elif str(reaction.emoji) == "➡️" and current_page < total_pages - 1:
                current_page += 1
                await message.edit(embed=await get_embed(current_page))

            await message.remove_reaction(reaction.emoji, user)
        except asyncio.TimeoutError:
            break
