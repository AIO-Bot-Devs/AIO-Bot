import os
from dotenv import load_dotenv
import disnake
from disnake.ext import commands
import logging

logger = logging.getLogger("disnake")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="disnake.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

load_dotenv()

# getting bot token from token.env
token = os.getenv("DISCORD_TOKEN")

# creating a commands.bot instance, and assigning it to "bot"
bot = commands.Bot(test_guilds=[1011201735685050418])

# when the bot is ready, run this command
@bot.event
async def on_ready():
    print("Bot is ready")

bot.load_extension("cogs.league_table.league_table")

bot.run(token)