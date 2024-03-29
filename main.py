#Imports all the required libraries
import disnake
from disnake.ext import commands
import os
from dotenv import load_dotenv
import json


#Loads the config file
def getConfig():
    with open('config.json', 'r') as f:
        data = json.load(f)
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


#Define the test guilds if the bot is in dev mode
if config[1] == True:
    bot = commands.Bot(
    command_prefix=config[3],
    test_guilds=config[2],
    sync_commands_debug=True,
    intents=intents,
    activity = disnake.Activity(name=config[5])
)
#Define the bot if the bot is not in dev mode (no test guilds)
else:
    bot = commands.Bot(
        command_prefix=config[3],
        sync_commands_debug=True,
        intents=intents,
        activity = disnake.Activity(name=config[5])
    )


#Setup global variables
# convert string hex color codes from config to int with base 16, then add them to bot
bot.colour_neutral = int(config[8]["neutral"], base=16)
bot.colour_success = int(config[8]["success"], base=16)
bot.colour_error = int(config[8]["error"], base=16)
# add emoji codes from config to bot 
bot.emoji_check = config[9]["check"]
bot.emoji_cross = config[9]["cross"]
bot.emoji_loading = config[9]["loading"]
# add ownerd id and footer from config to bot
bot.owner_id = config[0]
bot.footer = config[7]


#Adds cogs to the main bot (if they are enabled in config.json)
cogs = config[10]

# loads each cog
for i in cogs:
    if cogs[i]:
        bot.load_extension(f'cogs.{i}')


#Outputs a mesage when bot is online
#Remove this and replace with an uptime bot at some point - API calls are not recommended in on_ready
@bot.event
async def on_ready():
    print("------")
    print(f"Logged in as {bot.user}")
    print("------")
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


        


#Make this at some point lol
# @bot.slash_command()
# async def setup(inter):
#     setupEmbed = disnake.Embed(
# title=f"Begin Setup",
# description=f"",
# color=bot.colour_success)
#     owner = await bot.fetch_user(bot.owner_id)
#     setupEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
#     setupEmbed.set_thumbnail(url="https://evilpanda.me/files/idk.png")
#     await inter.response.send_message(embed=setupEmbed)


#Runs the bot using token from .env file
load_dotenv()
bot.run(os.getenv('DISCORD_TOKEN'))
