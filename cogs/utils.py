import disnake
from disnake.ext import commands
from time import sleep
import requests
from bs4 import BeautifulSoup
import urllib.parse
import asyncio

# function to genertate a progress bar
def progressBar(percentage):
    bar = "["
    for i in range(25):
        if i < percentage / 4:
            bar += "#"
        else:
            bar += "--"
    bar += "]"
    return bar

# WTF WHO DOES THIS
def listToString(list):
    string = ""
    for i in list:
        string += i + ", "
    string = string[:-2]
    return string

# allows the cog to be loaded
def setup(bot):
    bot.add_cog(utilsCog(bot))

# class for all the utility commands
class utilsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # command to get the pfp of a user
    @commands.slash_command()
    async def avatar(self, inter, user: disnake.User):
        """
        Parameters
        ----------
        user: The user to get it from
        """
        # create the embed
        avatarEmbed = disnake.Embed(
            title=f"User Avatar",
            color=self.bot.colour_success)
        avatarEmbed.set_image(url=user.avatar)
        avatarEmbed.set_author(name=user)
        # set the embed footer
        owner = await self.bot.fetch_user(self.bot.owner_id)
        avatarEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
        await inter.response.send_message(embed=avatarEmbed)

    # test command to edit a message
    @commands.slash_command()
    async def edit(inter):
        await inter.response.send_message("Test message 1")
        sleep(1)
        await inter.edit_original_message(content="Test message 2")

    # command to ping a user
    @commands.slash_command()
    async def ping(inter, user: disnake.User):
        """
        Parameters
        ----------
        user: The user to ping
        """
        await inter.response.send_message("Pong! {}".format(user.mention))

    # command to render a webpage
    @commands.slash_command()
    async def webpage(self, inter, url: str):
        """
        Parameters
        ----------
        url: The url of the webpage
        """
        # adds a waiting message
        await inter.response.defer(with_message=True)
        # if the url does not start with http/s, add it
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url
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
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
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
        screenshot_api = f"https://shot.screenshotapi.net/screenshot?token=N72DF2K-5ZZ4WCR-JJPEHAX-2E1T31G&url={parsedUrl}&width=1920&height=1080&output=image&file_type=png&wait_for_event=load"
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
        owner = await self.bot.fetch_user(self.bot.owner_id)
        webpageEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
        webpageEmbed.set_image(file=image)
        await inter.edit_original_message(embed=webpageEmbed)


