import os
from dotenv import load_dotenv
from disnake.ext import commands
import logging

# I have no clue how this works but it does logging
# https://docs.disnake.dev/en/stable/logging.html
logger = logging.getLogger("disnake")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="disnake.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# creating a commands.bot instance, and assigning it to "bot"
bot = commands.Bot(test_guilds=[1011201735685050418])

# outputs "Bot is ready" to the console when the bot is ready
@bot.event
async def on_ready():
    print("Bot is ready")

# loads the league_table cog
bot.load_extension("cogs.league_table.league_table")

# getting bot token from token.env using dotenv and runs the bot
load_dotenv()
bot.run(os.getenv("DISCORD_TOKEN"))