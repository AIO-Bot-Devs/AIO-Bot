import disnake
from disnake.ext import commands
from time import sleep
import requests
from bs4 import BeautifulSoup
import urllib.parse
import asyncio
import json
import os
from dotenv import load_dotenv
from cogs.qrcodes import generateQr


# allows the cog to be loaded
def setup(bot):
    bot.add_cog(utilsCog(bot))

# gets dimensions of webpage render
def getDimensions():
    with open('config.json', 'r') as f:
        data = json.load(f)
    height = str(data["cogs"]["utils"]["webpage_render_height"])
    width = str(data["cogs"]["utils"]["webpage_render_width"])
    return height, width

# class for all the utility commands
class utilsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # command to get the pfp of a user
    @commands.slash_command()
    async def avatar(self, inter, user: disnake.User):
        """
        Get a user's avatar
        
        Parameters
        ----------
        user: The user to get it from
        """
        bot = self.bot
        # create the embed
        avatarEmbed = disnake.Embed(
            title=f"User Avatar",
            color=self.bot.colour_success)
        avatarEmbed.set_image(url=user.avatar)
        avatarEmbed.set_author(name=user)
        # set the embed footer
        avatarEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
        await inter.response.send_message(embed=avatarEmbed)

    # command to get bot's ping
    @commands.slash_command()
    async def ping(self, inter):
        """
        Check ping of bot
        """
        await inter.response.send_message(f"Pong! Latency: {int(self.bot.latency * 1000)}ms")

    # command to render a webpage
    # TODO: API trial ran out lol, change to use selenium webdriver and render the page locally instead, or just remove
    @commands.slash_command()
    async def webpage(self, inter, url: str):
        """
        Generates preview of website
        
        Parameters
        ----------
        url: The url of the webpage
        """
        bot = self.bot
        # adds a waiting message
        await inter.response.defer(with_message=True)
        # if the url does not start with http/s, add it
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        # try to get the webpage, if it fails, send an error message
        try:
            r = requests.get(url)
        except:
            # creates the error embed
            errorEmbed = disnake.Embed(
                title="Invalid URL provided",
                description="Make sure this URL exists and is valid",
                color=self.bot.colour_error)
            # set the embed footer
            errorEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
            errorEmbed.set_thumbnail(url="https://api.evilpanda.live/static/error1.png")
            await inter.edit_original_message(embed=errorEmbed)
            return
        # WTF IS SOUP LMAO
        soup = BeautifulSoup(r.content, 'html.parser')
        # get the title of the webpage
        title = soup.find('title').text
        # if the title is empty, set it to No Title
        if title == "":
            title = "No title"
        # send the passed url to the screenshot api
        parsedUrl = urllib.parse.quote_plus(url)
        height, width = getDimensions()
        load_dotenv()
        api_key = os.getenv('SCREENSHOT_API_KEY')
        screenshot_api = f"https://shot.screenshotapi.net/screenshot?token={api_key}&url={parsedUrl}&width={width}&height={height}&output=image&file_type=png&wait_for_event=load"
        screenshot = requests.get(screenshot_api)
        # open the screenshot file and writes the screenshot to it
        with open("screenshot.png", "wb") as f:
            f.write(screenshot.content)
        image = disnake.File("screenshot.png")
        # create the embed
        webpageEmbed = disnake.Embed(
            title=title,
            description=f"[[go to webpage]]({url})",
            color=self.bot.colour_success)
        # set the embed footer
        webpageEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
        webpageEmbed.set_image(file=image)
        await inter.edit_original_message(embed=webpageEmbed)

    # command to get the invite link and QR code for the bot
    @commands.slash_command()
    async def invite(self, inter):
        """
        Generates invite link for bot
        """
        bot = self.bot
        # create the invite
        link = f"https://discord.com/api/oauth2/authorize?client_id={str(self.bot.application_id)}&permissions={str(bot.permissions_int)}&scope=bot%20applications.commands"
        qrcode_file = generateQr(link)
        # create the embed
        inviteEmbed = disnake.Embed(
            title="Invite me to your server!",
            description=f"[[Invite link]]({link})",
            color=self.bot.colour_success)
        # set the embed footer
        inviteEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
        inviteEmbed.set_image(file=qrcode_file)
        await inter.response.send_message(embed=inviteEmbed)

