#Imports all the required libraries
import disnake
from disnake.ext import commands
import os
from dotenv import load_dotenv
import json
import aiofiles


class Config:
    def __init__(self, filename: str = "config.json"):
        self.filename = filename
        self.config = None
        with open(self.filename, "r") as f:
            self.data = json.load(f)

    async def reload(self):
        async with aiofiles.open(self.filename, "r") as f:
            self.config = json.loads(await f.read())



#Define intents for bot (make these more specific later so bot doesn't require unnecessary intents/permissions)
intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True


#Get config for bot
config = Config()



#Define the test guilds if the bot is in dev mode
if config.data["dev"]:
    bot = commands.Bot(
    command_prefix=config.data["prefix"],
    test_guilds=config.data["test_guilds"],
    command_sync_flags=commands.CommandSyncFlags.all(),
    intents=intents,
    activity = disnake.Activity(name=config.data["activity"])
)
#Define the bot if the bot is not in dev mode (no test guilds)
else:
    bot = commands.Bot(
    command_prefix=config.data["prefix"],
    command_sync_flags = commands.CommandSyncFlags.default(),
    intents=intents,
    activity = disnake.Activity(name=config.data["activity"])
)

# Add config to bot
bot.config = config


# Setup constants from config
# convert string hex color codes from config to int with base 16, then add them to bot
bot.colour_neutral = int(bot.config.data["colours"]["neutral"], base=16)
bot.colour_success = int(bot.config.data["colours"]["success"], base=16)
bot.colour_error = int(bot.config.data["colours"]["error"], base=16)
# add emoji codes from config to bot 
bot.emoji_check = bot.config.data["emojis"]["check"]
bot.emoji_cross = bot.config.data["emojis"]["cross"]
bot.emoji_loading = bot.config.data["emojis"]["loading"]
bot.emoji_bullet_point = bot.config.data["emojis"]["bullet_point"]
bot.emoji_error = bot.config.data["emojis"]["error"]
# add footer and list of owners from config to bot
bot.footer = bot.config.data["footer"]
bot.owners = bot.config.data["owners"]
# Not sure if these are necessary, will hopefully rework the status command later
bot.status_enum = commands.option_enum({"Online": disnake.Status.online.value, "Idle": disnake.Status.idle.value, "Do Not Disturb": disnake.Status.dnd.value, "Invisible": disnake.Status.invisible.value})

bot.permissions_int = bot.config.data["permissions_int"]  # seems to be reasonable permissions, add this to config.json at some point


#Adds cogs to the main bot (if they are enabled in config.json)
cogs = bot.config.data["cogs"]

# loads each cog
for i in cogs:
    if cogs[i]["active"]:
        bot.load_extension(f'cogs.{i}')
# Testing cog - not in config
bot.load_extension("cogs.test_embed")


#Outputs a mesage when bot is online
#Remove this and replace with an uptime bot at some point - API calls are not recommended in on_ready
@bot.event
async def on_ready():
    print("------")
    print(f"Logged in as {bot.user}")
    print("------")
    if bot.config.data["dev"]:
        try:    
            uptime = await bot.fetch_channel(bot.config.data["uptime_channel"])
            dev = bot.emoji_check
            cogs_string = ""
            for i in cogs:
                cogs_string += "\n"
                if cogs[i]["active"]:
                    cogs_string += f">   • {bot.emoji_check} {i} enabled"
                else:
                    cogs_string += f">   • {bot.emoji_cross} {i} disabled"
            await uptime.send(f"{bot.emoji_check} **{bot.user.mention} online!**\n> Disnake: {disnake.__version__}\n> Latency: {int(bot.latency * 1000)}ms\n> Dev mode: {dev}\n> Guilds: {len(bot.guilds)}\n> Cogs: {cogs_string}")
            print("Uptime message sent")
        except:
            print("Uptime channel not found")
    else:
        print("No uptime message sent, bot is not in dev mode")


@bot.slash_command()
# Commands should only be available for a list of owners in config
@commands.check(lambda ctx: ctx.author.id in ctx.bot.owners)
async def admin(inter):
    pass


@admin.sub_command()
async def reload(inter):
    """
    Reloads the bot's config
    """
    await bot.config.reload()
    await inter.response.send_message(f"{bot.emoji_check} Config reloaded")
    print(f"Config reloaded by {inter.author.name}#{inter.author.discriminator} ({inter.author.id})")

# WIP command, likely has issues
@admin.sub_command()
async def status(inter, status: bot.status_enum):
    """
    Set the bot's status
    """
    async with aiofiles.open("config.json", "r") as f:
        data = json.loads(await f.read())
    activity = disnake.Game(name=data["activity"])
    data["status"] = status
    async with aiofiles.open("config.json", "w") as f:
        await f.write(json.dumps(data, indent=4))
    await bot.change_presence(status=status, activity=activity)
    await inter.response.send_message(f"{bot.emoji_check} Status set to {status}")
    print(f"Status set to {status} by {inter.author.name}#{inter.author.discriminator} ({inter.author.id})")




#Runs the bot using token from .env file
load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))
