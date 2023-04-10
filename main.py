#Imports all the required libraries
import disnake
from disnake.ext import commands
import os
from dotenv import load_dotenv
import json
import aiofiles


#Loads the config file
def getConfig():
    with open('config.json', 'r') as f:
        data = json.loads(f.read())
    # grabs all the config data
    owner = data["owner"]
    dev = data["dev"]
    test_guilds = data["test_guilds"]
    prefix = data["prefix"]
    status = data["status"]
    activity = data["activity"]
    uptime_channel = data["uptime_channel"]
    footer = data["footer"]
    colours = data["colours"]
    emojis = data["emojis"]
    # makes a dict of all the cogs and their status
    cogs = {}
    for i in data["cogs"]:
        cogs[i] = data["cogs"][i]["active"]
    return owner, dev, test_guilds, prefix, status, activity, uptime_channel, footer, colours, emojis, cogs


#Define intents for bot (make these more specific later so bot doesn't require unnecessary intents/permissions)
intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True


#Get config for bot
config = getConfig()


command_sync_flags = commands.CommandSyncFlags.all()

#Define the test guilds if the bot is in dev mode
if config[1] == True:
    bot = commands.Bot(
    command_prefix=config[3],
    test_guilds=config[2],
    command_sync_flags=command_sync_flags,
    intents=intents,
    activity = disnake.Activity(name=config[5])
)
#Define the bot if the bot is not in dev mode (no test guilds)
else:
    bot = commands.Bot(
        command_prefix=config[3],
        command_sync_flags=command_sync_flags,
        intents=intents,
        activity = disnake.Activity(name=config[5])
    )


# Setup constants from config
# convert string hex color codes from config to int with base 16, then add them to bot
bot.colour_neutral = int(config[8]["neutral"], base=16)
bot.colour_success = int(config[8]["success"], base=16)
bot.colour_error = int(config[8]["error"], base=16)
# add emoji codes from config to bot 
bot.emoji_check = config[9]["check"]
bot.emoji_cross = config[9]["cross"]
bot.emoji_loading = config[9]["loading"]
bot.emoji_bullet_point = config[9]["bullet_point"]
# add ownerd id and footer from config to bot
bot.owner_id = config[0]
bot.footer = config[7]
bot.status_enum = commands.option_enum({"Online": disnake.Status.online.value, "Idle": disnake.Status.idle.value, "Do Not Disturb": disnake.Status.dnd.value, "Invisible": disnake.Status.invisible.value})
bot.status_dict = {"online": disnake.Status.online, "idle": disnake.Status.idle, "dnd": disnake.Status.dnd, "invisible": disnake.Status.invisible}

bot.permissions_int = 515433154624  # seems to be reasonable permissions, add this to config.json at some point


#Adds cogs to the main bot (if they are enabled in config.json)
cogs = config[10]

# loads each cog
for i in cogs:
    if cogs[i]:
        bot.load_extension(f'cogs.{i}')
bot.load_extension("cogs.test_embed")


#Outputs a mesage when bot is online
#Remove this and replace with an uptime bot at some point - API calls are not recommended in on_ready
@bot.event
async def on_ready():
    print("------")
    print(f"Logged in as {bot.user}")
    print("------")
    if config[1] == True:
        try:    
            uptime = await bot.fetch_channel(config[6])
            if config[1] == True:
                dev = bot.emoji_check
            else:
                dev = bot.emoji_cross
            cogs_string = ""
            for i in cogs:
                cogs_string += "\n"
                if cogs[i] == True:
                    cogs_string += f">   • {bot.emoji_check} {i} enabled"
                else:
                    cogs_string += f">   • {bot.emoji_cross} {i} disabled"
            await uptime.send(f"{bot.emoji_check} **{bot.user.mention} online!**\n> Disnake: {disnake.__version__}\n> Latency: {int(bot.latency * 1000)}ms\n> Dev mode: {dev}\n> Guilds: {len(bot.guilds)}\n> Cogs: {cogs_string}")
        except:
            print("Uptime channel not found")
    else:
        print("No uptime message sent, bot is not in dev mode")


@bot.slash_command()
@commands.is_owner()
async def admin(inter):
    pass

# very WIP command, likely will not work/has issues
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
    print(f"Status set to {status} by {inter.author.name} ({inter.author.id})")




#Runs the bot using token from .env file
load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))
