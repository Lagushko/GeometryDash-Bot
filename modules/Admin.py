from .__utils__ import *
from bot import bot

async def add_level(ctx, level_id: str, name: str, difficulty: int, downloads: int, likes: int, time: int, coins: int, sender: int):
    admins = botDB.get("admins") or []
    moderators = botDB.get("moderators") or []
    if ctx.author.id in (admins + Config.OWNER + moderators):
        if levelDB.get(level_id):
            await ctx.send(f"❌ Level with ID `{level_id}` already exists in the database.")
            return
        
        name = name.replace("-", " ").replace("\\", "")
        name = discord.utils.escape_markdown(name)

        levelDB.add(level_id, name, difficulty, downloads, likes, time, coins, sender)

        recent = botDB.get("recent") or []
        recent.append(level_id)
        if len(recent) > 25:
            recent.pop(0)
        botDB.update_field("recent", recent)

        send_list = botDB.get("send") or []
        send_list = [entry for entry in send_list if entry[0] != level_id]
        botDB.update_field("send", send_list)

        user_data = userDB.get(sender)
        user_data["creatorpoints"] += 1
        user_data["creations"].append(level_id)
        userDB.update_field(sender, "creatorpoints", user_data['creatorpoints'])
        userDB.update_field(sender, "creations", user_data['creations'])

        notification = f"🎉 Your level `{name}` (ID: {level_id}) has been added to the bot! 🏆"
        userDB.update_field(sender, "notification", notification)

        if ctx.author.id != Config.OWNER[0]:
            owner_user = await bot.fetch_user(Config.OWNER[0])
            embed = discord.Embed(
                title=f"{get_difficulty_visual(ctx.author.id, difficulty)} New Level Added",
                color=discord.Color.orange()
            )

            if ctx.author.id in admins:
                role = "Admin"
                emoji = EMOJIS['admin']
            elif ctx.author.id in moderators:
                role = "Moderator"
                emoji = EMOJIS['moderator']
            else:
                role = "Unknown"
                emoji = "❔"

            embed.add_field(name=f"{emoji} {role}", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=False)
            embed.add_field(name="🎮 Level Name", value=f"`{name}`", inline=False)
            embed.add_field(name="🆔 Level ID", value=f"`{level_id}`", inline=True)
            embed.add_field(name="👤 Creator ID", value=f"<@{sender}> (`{sender}`)", inline=True)
            embed.set_footer(text="You might want to verify the content or validity of this level.")

            try:
                await owner_user.send(embed=embed)
            except discord.Forbidden:
                await ctx.send("⚠️ Could not DM the owner (they might have DMs disabled).")

        await ctx.send(f"✅ Level `{name}` ID: {level_id} successfully added!\n🎖️ Creator <@{sender}> has now `{user_data['creatorpoints']}` Creator Points!")

async def delete_user(ctx, user_id: int):
    admins = botDB.get("admins") or []
    moderators = botDB.get("moderators") or []
    if ctx.author.id in (Config.OWNER + admins + moderators) and user_id not in (Config.OWNER + admins + moderators):
        try:
            conn = sqlite3.connect("data/users.db")
            cursor = conn.cursor()

            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            conn.close()

            if ctx.author.id != Config.OWNER[0]:
                owner_user = await bot.fetch_user(Config.OWNER[0])
                embed = discord.Embed(
                    title="🗑️ User Removed",
                    color=discord.Color.red()
                )

                if ctx.author.id in admins:
                    role = "Admin"
                    emoji = EMOJIS['admin']
                elif ctx.author.id in moderators:
                    role = "Moderator"
                    emoji = EMOJIS['moderator']
                else:
                    role = "User"
                    emoji = "❔"

                embed.add_field(name=f"{emoji} {role}", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=False)
                embed.add_field(name="👤 Deleted User", value=f"<@{user_id}> (`{user_id}`)", inline=True)
                embed.set_footer(text="Check if this removal was expected or accidental.")

                try:
                    await owner_user.send(embed=embed)
                except discord.Forbidden:
                    await ctx.send("⚠️ Could not DM the owner (they might have DMs disabled).")

            await ctx.send(f"🗑️ User with ID `{user_id}` has been **successfully deleted** from the database.")
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred while deleting the user: `{e}`")

async def delete_level(ctx, level_id: str):
    admins = botDB.get("admins") or []
    moderators = botDB.get("moderators") or []
    if ctx.author.id in (admins + Config.OWNER + moderators) and level_id not in MAIN_LEVELS:
        try:
            conn = sqlite3.connect("data/levels.db")
            cursor = conn.cursor()

            cursor.execute("SELECT sender FROM levels WHERE level_id = ?", (level_id,))
            row = cursor.fetchone()

            if row:
                sender = row[0]

                user_data = userDB.get(sender)
                current_creator_points = user_data["creatorpoints"]

                userDB.update_field(sender, "creatorpoints", current_creator_points - 1)

                notification = f"⚠️ Your level with ID `{level_id}` has been deleted. You lost 1 Creator Point. 😔"
                userDB.update_field(sender, "notification", notification)

            cursor.execute("DELETE FROM levels WHERE level_id = ?", (level_id,))
            conn.commit()
            conn.close()

            if ctx.author.id != Config.OWNER[0]:
                owner_user = await bot.fetch_user(Config.OWNER[0])
                embed = discord.Embed(
                    title=f"🗑️ Level Deleted",
                    color=discord.Color.red()
                )

                if ctx.author.id in admins:
                    role = "Admin"
                    emoji = EMOJIS['admin']
                elif ctx.author.id in moderators:
                    role = "Moderator"
                    emoji = EMOJIS['moderator']
                else:
                    role = "Uknown"
                    emoji = "❔"

                embed.add_field(name=f"{emoji} {role}", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=False)
                embed.add_field(name="🎮 Deleted Level", value=f"`{row[1]}`", inline=False)
                embed.add_field(name="🆔 Level ID", value=f"`{level_id}`", inline=True)
                embed.add_field(name="👤 Creator ID", value=f"<@{sender}> (`{sender}`)", inline=True)
                embed.set_footer(text="If this was not intended, you may want to look into it.")

                try:
                    await owner_user.send(embed=embed)
                except discord.Forbidden:
                    await ctx.send("⚠️ Could not DM the owner (they might have DMs disabled).")

            await ctx.send(f"🗑️ Level with ID `{level_id}` has been **successfully deleted** from the database.")

        except Exception as e:
            await ctx.send(f"⚠️ An error occurred while deleting the level: `{e}`")

async def delete_sent(ctx, level_id: int):
    admins = botDB.get("admins") or []
    moderators = botDB.get("moderators") or []
    helpers = botDB.get("helpers") or []
    send_list = botDB.get("send") or []

    if ctx.author.id not in (admins + Config.OWNER + moderators):
        if ctx.author.id in helpers:
            await ctx.send("❌ You do not have permission to delete submissions.")
        return

    found_index = next((i for i, item in enumerate(send_list) if int(item[0]) == level_id), None)
    if found_index is None:
        await ctx.send(f"⚠️ No submission found with level ID `{level_id}`.")
        return

    target = send_list.pop(found_index)
    botDB.update_field("send", send_list)

    level_id, sender_id = target

    if ctx.author.id != sender_id:
        notification = f"❌ Your level suggestion with ID `{level_id}` was rejected by a staff member. 😔 Better luck next time!"
        userDB.update_field(sender_id, "notification", notification)

    if ctx.author.id != Config.OWNER[0]:
        try:
            owner_user = await bot.fetch_user(Config.OWNER[0])
            embed = discord.Embed(
                title="🗑️ Submission Deleted",
                color=discord.Color.orange()
            )

            if ctx.author.id in admins:
                role = "Admin"
                emoji = EMOJIS['admin']
            elif ctx.author.id in moderators:
                role = "Moderator"
                emoji = EMOJIS['moderator']
            else:
                role = "Unknown"
                emoji = "❔"

            embed.add_field(name=f"{emoji} {role}", value=f"{ctx.author.mention} (`{ctx.author.id}`)", inline=False)
            embed.add_field(name="🎮 Deleted Submission", value=f"`{level_id}`", inline=False)
            embed.add_field(name="👤 Sender", value=f"<@{sender_id}> (`{sender_id}`)", inline=True)
            embed.set_footer(text="If this was not intended, you may want to look into it.")

            await owner_user.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("⚠️ Could not DM the owner (they might have DMs disabled).")

    await ctx.send(f"🗑️ Submission with level ID `{level_id}` has been **successfully removed**.")

async def cheats(ctx, mode: str, switch: str):
    if ctx.author.id not in permission(3):
        return

    if ctx.author.id not in cheat_modes:
        cheat_modes[ctx.author.id] = {"noclip": 0, "speedhack": 0, "icons": 0}
    
    if not mode in ["noclip", "speedhack", "icons"]:
        await ctx.send("❌ Invalid cheat mode. Use `noclip`/`speedhack`/`icons`.")
        return
    
    if not switch in ['on', 'off']:
        await ctx.send("❌ Invalid switch type. Use `on` or `off`.")
        return
    
    cheat_modes[ctx.author.id][mode] = 1 if switch == "on" else 0
    await ctx.send(f"✅ Successfully turned {switch} `{mode}` cheats!")

async def manage(ctx, obj_type: str, obj_id: str, field: str, data: str):
    if ctx.author.id not in permission(3):
        return
    
    if obj_type == "users":
        obj_id = int(obj_id)

    try:
        parsed_data = ast.literal_eval(data)
    except:
        parsed_data = data.replace("-", " ").replace("\\", "")
        parsed_data = discord.utils.escape_markdown(parsed_data)

    if obj_type.lower() == "user":
        userDB.update_field(obj_id, field, parsed_data)
        await ctx.send(
            f"✅ Field `{field}` for user with ID `{obj_id}` has been successfully updated to `{parsed_data}`."
        )
    elif obj_type.lower() == "level":
        levelDB.update_field(obj_id, field, parsed_data)
        await ctx.send(
            f"✅ Field `{field}` for level with ID `{obj_id}` has been successfully updated to `{parsed_data}`."
        )
    elif obj_type.lower() == "settings":
        botDB.update_field(field, parsed_data)
        await ctx.send(
            f"✅ Field `{field}` in settings has been successfully updated to `{parsed_data}`."
        )
    else:
        await ctx.send("❌ Invalid object type. Use `user`, `level`, or `settings`.")