from .__utils__ import *
from bot import bot

async def shop(ctx):
    user_id = ctx.author.id
    user_data = userDB.get(user_id)
    
    page = 0

    def generate_embed(page_index):
        embed = discord.Embed(
            title="🛒 Icon Shop",
            description=f"**{GAMEMODES[page_index].capitalize()}s list:**\n",
            color=discord.Color.blue()
        )

        for idx, icon in enumerate(ICONS[page_index]):
            icon_id = f"{page_index + 1}.{idx}"
            price_text = f"{EMOJIS['manaorbs']}{PRICES[idx]}" if user_data and not icon_id in user_data['purchased'] and PRICES[idx] > 0 else ""
            embed.description += f"{icon} ID: `{icon_id}` {price_text}\n"
        
        embed.set_footer(text=f"Page {page_index + 1} of {len(ICONS)}")
        return embed

    message = await ctx.send(embed=generate_embed(page))
    await message.add_reaction("⬅️")
    await message.add_reaction("➡️")

    def check(reaction, user):
        return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in ["⬅️", "➡️"]

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "➡️":
                page = (page + 1) % len(ICONS)
            elif str(reaction.emoji) == "⬅️":
                page = (page - 1) % len(ICONS)

            await message.edit(embed=generate_embed(page))
            await message.remove_reaction(reaction, user)

        except Exception:
            break

async def buy(ctx, icon_id: str):
    user_id = ctx.author.id
    user_data = userDB.get(user_id)

    if not user_data:
        await ctx.send("❌ User data not found.")
        return

    try:
        gamemode_str, number_str = icon_id.split(".")
        gamemode = int(gamemode_str)
        number = int(number_str)
    except Exception:
        await ctx.send("❌ Invalid icon ID format. Use `gamemode.number` (e.g. `1.0`).")
        return

    if gamemode < 1 or gamemode > len(ICONS):
        await ctx.send("❌ Invalid gamemode index.")
        return
    if number < 0 or number >= len(ICONS[gamemode - 1]):
        await ctx.send("❌ Invalid icon number for this gamemode.")
        return

    purchased_icons = user_data.get("purchased", [])
    if icon_id in purchased_icons or PRICES[number] == 0:
        await ctx.send("❌ You already have this icon or it is free.")
        return

    orbs = user_data.get("orbs", 0)
    price = PRICES[number]

    if orbs < price:
        await ctx.send(f"❌ You need {price} orbs to buy this icon, but you only have {orbs}.")
        return

    userDB.update_field(user_id, "orbs", orbs - price)

    purchased_icons.append(icon_id)
    userDB.update_field(user_id, "purchased", purchased_icons)

    embed = discord.Embed(
        title="Icon Purchased 🛒",
        description=f"You successfully purchased a **{GAMEMODES[gamemode - 1]}** {ICONS[gamemode - 1][number]} for **{price}**{EMOJIS['manaorbs']}!",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Icon ID: {icon_id} | Remaining orbs: {orbs - price}")

    await ctx.send(embed=embed)

async def equip(ctx, icon_id: str):
    user_id = ctx.author.id
    user_data = userDB.get(user_id)

    if not user_data:
        await ctx.send("❌ User data not found.")
        return
    
    try:
        gamemode_str, number_str = icon_id.split(".")
        gamemode = int(gamemode_str)
        number = int(number_str)
    except Exception:
        await ctx.send("❌ Invalid icon ID format. Use `gamemode.number` (e.g. `1.0`).")
        return

    if gamemode < 1 or gamemode > len(ICONS):
        await ctx.send("❌ Invalid gamemode index.")
        return
    if number < 0 or number >= len(ICONS[gamemode - 1]):
        await ctx.send("❌ Invalid icon number for this gamemode.")
        return

    if icon_id not in user_data.get("purchased", []) and PRICES[number] > 0:
        if not user_id in cheat_modes or cheat_modes[user_id]['icons'] == 0:
            await ctx.send("❌ You don't own this icon.")
            return

    icons_list = user_data.get("icons", [0] * len(ICONS))
    icons_list[gamemode - 1] = number

    userDB.update_field(user_id, "icons", icons_list)

    embed = discord.Embed(
        title="Icon Equipped ✅",
        description=f"You equipped a **{GAMEMODES[gamemode - 1]}** {ICONS[gamemode - 1][number]}",
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Icon ID: {icon_id}")

    await ctx.send(embed=embed)
