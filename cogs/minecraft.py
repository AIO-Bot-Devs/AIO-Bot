import disnake
from disnake.ext import commands
import json
import requests
import datetime
import base64

# allows the cog to be loaded
def setup(bot):
    bot.add_cog(minecraftCog(bot))

# class for all the minecraft commands
class minecraftCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # default command
    @commands.slash_command()
    async def minecraft(self, inter):
        pass

    # this subcommand will retrieve data about a minecraft player
    @minecraft.sub_command()
    async def user(self, inter, username: str):

        # TODO: put each step into a function to increase readability
        # TODO: implement aiohttp requests

        """
        Parameters
        ----------
        username: The username of the account
        """
        bot = self.bot
        # bot is thinking
        await inter.response.defer(with_message=True)
        # get the data from the api, should update to use aiohttp
        url = f"https://api.ashcon.app/mojang/v2/user/{username}"
        response = requests.get(url)
        # if the request is successful, then get the json file and generate the embed data
        if response.status_code == 200:
            data = json.loads(response.text)
            avatar = f"https://crafatar.com/renders/head/{data['uuid']}?size=512&default=MHF_Steve&overlay"
            cape = requests.get(f"https://api.capes.dev/load/{data['username']}")
            capeData = json.loads(cape.text)
            userEmbed = disnake.Embed(
                title=f"{data['username']}",
                description=f"[[NameMC]](https://namemc.com/profile/{data['username']})",
                color=self.bot.colour_success)
            userEmbed.set_thumbnail(url=avatar)
            userEmbed.add_field(name="UUID", value=data['uuid'], inline=False)
            # if no creation date is found, then set it to unknown, otherwise, convert it to a readable format
            if data['created_at'] == None:
                userEmbed.add_field(name="Creation Date", value="Unknown", inline=False)
            else:
                date = data['created_at'].split('-')
                date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), hour=12)
                timestamp = int(date.replace(tzinfo=datetime.timezone.utc).timestamp())
                userEmbed.add_field(name="Creation Date", value=f"<t:{timestamp}:D>", inline=False)
            capes = []
            # adds all of the users capes to a list
            for cape, capeDict in capeData.items():
                if capeDict['exists']:
                    capes.append(f"[[{capeDict['type'].capitalize()}]]({capeDict['imageUrl']})")
            # if the user has no capes, then set the value to none, otherwise, join the list into a string
            if capes:
                userEmbed.add_field(name=f"Capes ({len(capes)})", value=" ".join(capes), inline=False)
            else:
                userEmbed.add_field(name="Capes (0)", value="None", inline=False)
            # gets the friend data from the api and formats it into a list
            namemc = requests.get(f"https://api.namemc.com/profile/{data['uuid']}/friends")
            namemc = json.loads(namemc.text)
            friends = []
            for friend in namemc:
                friends.append(friend['name'])
            # if the user has no friends, then set the value to none, or if the user has more than 20 friends, then set the value to the first 20 friends
            # otherwise, join the list into a string
            if len(friends) > 20:
                friends = friends[:20]
                userEmbed.add_field(name=f"NameMC Friends ({len(namemc)})", value=", ".join(friends) + ' ...', inline=False)
            elif friends:
                userEmbed.add_field(name=f"NameMC Friends ({len(friends)})", value=", ".join(friends), inline=False)
            else:
                userEmbed.add_field(name="NameMC Friends (0)", value="None", inline=False)
            # adds pfp and footer to the embed
            owner = await self.bot.fetch_user(self.bot.owner_id)
            userEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            await inter.edit_original_message(embed=userEmbed)
        # if the user is not found, then send an error message
        elif response.status_code == 404:
            errorEmbed = disnake.Embed(
                title=f"User Not Found",
                description=f"The user '{username}' does not exist.",
                color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.live/files/error1.png")
            await inter.edit_original_message(embed=errorEmbed)
        # if the username is invalid, then send an error message
        elif response.status_code == 400:
            errorEmbed = disnake.Embed(
                title=f"Invalid Username",
                description=f"The username '{username}' is invalid.",
                color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.live/files/error1.png")
            await inter.edit_original_message(embed=errorEmbed)
        # if any other error occurs, then send an error message
        else:
            errorEmbed = disnake.Embed(
                title=f"An Error Occured",
                description=f"Error {response.status_code}. {response.error}",
                color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.live/files/error1.png")
            await inter.edit_original_message(embed=errorEmbed)
    
    # this subcommand will retrieve data about a server
    @minecraft.sub_command()
    async def server(self, inter, address: str, port: int = 25565):
        """
        Parameters
        ----------
        address: The address of the server
        port: The port of the server (default 25565)
        """
        bot = self.bot
        address = address.strip().lower()
        # sends a loading message
        await inter.response.defer(with_message=True)
        # gets the server data from the api
        # checks if port is 25565 so the image doesn't contain port if it's default
        if port == 25565:
            api = f"https://api.mcsrvstat.us/2/{address}"
        else:
            api = f"https://api.mcsrvstat.us/2/{address}:{port}"
        img = f"http://status.mclive.eu/Minecraft%20Server/{address}/{port}/banner.png"
        # sends a request to the api
        response = requests.get(api)
        # if the request is successful, then send the server data
        if response.status_code == 200:
            data = json.loads(response.text)
            # if the server is online use green embed colour, otherwise use red
            if data['online']:
                serverEmbed = disnake.Embed(
                    title=f"Server: {address}",
                    description=f"{bot.emoji_check} Online",
                    color=self.bot.colour_success
                )
                # if there is an icon, then set the thumbnail to the icon
                if data["icon"]:
                    # decode the icon in api from base64 to bytes and write to an image file
                    with open("icon.png", "wb") as fh:
                        fh.write(base64.decodebytes(data["icon"].split(',')[1].encode()))
                    serverEmbed.set_thumbnail(file=disnake.File("icon.png"))
                # if there is no icon, then set the thumbnail to the default icon
                else:
                    serverEmbed.set_thumbnail(file=disnake.File("default_icon_64.png"))
                # add the port, version and player to the embed
                serverEmbed.add_field(name="Port", value=port, inline=False)
                serverEmbed.add_field(name="Version", value=data['version'], inline=False)
                serverEmbed.add_field(name="Players", value=f"{data['players']['online']}/{data['players']['max']}", inline=False)
                # if the server software is available in api then add it to the embed 
                if 'software' in data:
                    serverEmbed.add_field(name="Software", value=data['software'], inline=False)
                # add the server banner to the embed
                serverEmbed.set_image(url=img)
            # if the server is offline, then send an error message
            else:
                serverEmbed = disnake.Embed(
                    title=f"Server: '{address}'",
                    description=f"{bot.emoji_cross} Offline",
                    color=self.bot.colour_error
                )
                # set the thumbnail to the default icon
                serverEmbed.set_thumbnail(file=disnake.File("default_icon_64.png"))
                # add banner to the embed
                serverEmbed.set_image(url=img)
            # add footer to embed
            owner = await self.bot.fetch_user(self.bot.owner_id)
            serverEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            # edit the original message with the embed
            await inter.edit_original_message(embed=serverEmbed)
        # if the api returns an error, then send an error message
        else:
            errorEmbed = disnake.Embed(
                title=f"API Error",
                description=f"Error {response.status_code} occured with server status api. Please report this",
                color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            # add footer to embed
            errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.live/files/error1.png")
            # edit the original message with the embed
            await inter.edit_original_message(embed=errorEmbed)


        