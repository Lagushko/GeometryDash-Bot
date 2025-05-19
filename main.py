from bot import bot

from modules import *
from modules import Basic
from modules import Levels
from modules import Interaction
from modules import Bonuses
from modules import Shop
from modules import Submissions
from modules import Admin
from modules import Control

@bot.event
async def on_ready():
    activity = discord.Game(name=f"!help for info • Fire in the hole 🙂")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = message.author.id
    userDB.ensure(user_id)

    if message.content.startswith("!"):
        notification = userDB.get(user_id).get("notification", "")
        if notification:
            try:
                await message.reply(f"📬 <@{user_id}> {notification}")
            except Exception as e2:
                print(f"❌ Failed to reply in channel: {e2}")

            userDB.update_field(user_id, "notification", "")

    await bot.process_commands(message)

# ----- BASIC COMMANDS ------ #
bot.command(name='help')(Basic.help)
bot.command(name='link')(Basic.link)
bot.command(name='profile')(Basic.profile)
bot.command(name='leaderboards')(Basic.leaderboards)
bot.command(name='visual')(Basic.visual)

# ---------- LEVELS --------- #
bot.command(name='main')(Levels.main)
bot.command(name='search')(Levels.search)
bot.command(name='recent')(Levels.recent)
bot.command(name='creator')(Levels.creator)

# ------- INTERACTION ------- #
bot.command(name='join')(Interaction.join)
bot.command(name='quit')(Interaction.quit)
bot.command(name='play')(Interaction.play)
bot.command(name='like')(Interaction.like)
bot.command(name='dislike')(Interaction.dislike)

# --------- BONUSES --------- #
bot.command(name='daily')(Bonuses.daily)
bot.command(name='weekly')(Bonuses.weekly)
bot.command(name='reward')(Bonuses.reward)

# -------- ICON SHOP -------- #
bot.command(name='shop')(Shop.shop)
bot.command(name='buy')(Shop.buy)
bot.command(name='equip')(Shop.equip)

# ------- SUBMISSIONS ------- #
bot.command(name='send')(Submissions.send)
bot.command(name='sent-list')(Submissions.sent_list)

# ------- ADMIN ONLY -------- #
bot.command(name='add-level')(Admin.add_level)
bot.command(name='delete-user')(Admin.delete_user)
bot.command(name='delete-level')(Admin.delete_level)
bot.command(name='delete-sent')(Admin.delete_sent)
bot.command(name='cheats')(Admin.cheats)
bot.command(name='manage')(Admin.manage)

# ------- BOT CONTROL ------- #
bot.command(name='update-db')(Control.update_db)
bot.command(name='set-db')(Control.set_db)
bot.command(name='role')(Control.role)
bot.command(name='data')(Control.data)


if __name__ == "__main__":
    bot.run(Config.TOKEN_BOT)