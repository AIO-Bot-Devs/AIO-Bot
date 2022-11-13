import disnake
from disnake.ext import commands
import json
import requests
import datetime
import base64

def setup(bot):
    bot.add_cog(minecraftCog(bot))

class minecraftCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def minecraft(self, inter):
        pass

    @minecraft.sub_command()
    async def user(self, inter, username: str):
        """
        Get info on a Minecraft account

        Parameters
        ----------
        username: The username of the account
        """
        await inter.response.defer(with_message=True)
        url = f"https://api.ashcon.app/mojang/v2/user/{username}"
        response = requests.get(url)
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
            if data['created_at'] == None:
                userEmbed.add_field(name="Creation Date", value="Unknown", inline=False)
            else:
                date = data['created_at'].split('-')
                date = datetime.datetime(int(date[0]), int(date[1]), int(date[2]), hour=12)
                timestamp = int(date.replace(tzinfo=datetime.timezone.utc).timestamp())
                userEmbed.add_field(name="Creation Date", value=f"<t:{timestamp}:D>", inline=False)
            capes = []
            for cape, capeDict in capeData.items():
                if capeDict['exists']:
                    capes.append(f"[[{capeDict['type'].capitalize()}]]({capeDict['imageUrl']})")
            if capes:
                userEmbed.add_field(name=f"Capes ({len(capes)})", value=" ".join(capes), inline=False)
            else:
                userEmbed.add_field(name="Capes (0)", value="None", inline=False)
            namemc = requests.get(f"https://api.namemc.com/profile/{data['uuid']}/friends")
            namemc = json.loads(namemc.text)
            friends = []
            for friend in namemc:
                friends.append(friend['name'])
            if len(friends) > 20:
                friends = friends[:20]
                userEmbed.add_field(name=f"NameMC Friends ({len(namemc)})", value=", ".join(friends) + ' ...', inline=False)
            elif friends:
                userEmbed.add_field(name=f"NameMC Friends ({len(friends)})", value=", ".join(friends), inline=False)
            else:
                userEmbed.add_field(name="NameMC Friends (0)", value="None", inline=False)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            userEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            await inter.edit_original_message(embed=userEmbed)
        elif response.status_code == 404:
            errorEmbed = disnake.Embed(
                title=f"User Not Found",
                description=f"The user '{username}' does not exist.",
                color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.edit_original_message(embed=errorEmbed)
        elif response.status_code == 400:
            errorEmbed = disnake.Embed(
                title=f"Invalid Username",
                description=f"The username '{username}' is invalid.",
                color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.edit_original_message(embed=errorEmbed)
        else:
            errorEmbed = disnake.Embed(
                title=f"An Error Occured",
                description=f"Error {response.status_code}. {response.error}",
                color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.edit_original_message(embed=errorEmbed)
    
    @minecraft.sub_command()
    async def server(self, inter, address: str, port: int = 25565):
        """
        Get info on a Minecraft server

        Parameters
        ----------
        address: The address of the server
        port: The port of the server (default 25565)
        """
        address = address.replace(" ", "").lower()
        await inter.response.defer(with_message=True)
        if port == 25565:
            api = f"https://api.mcsrvstat.us/2/{address}"
        else:
            api = f"https://api.mcsrvstat.us/2/{address}:{port}"
        img = f"http://status.mclive.eu/Minecraft%20Server/{address}/{port}/banner.png"
        response = requests.get(api)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data['online']:
                serverEmbed = disnake.Embed(
                    title=f"Server: {address}",
                    description="<:check:1002964750356987935> Online",
                    color=self.bot.colour_success
                )
                if data["icon"]:
                    with open("icon.png", "wb") as fh:
                        fh.write(base64.decodebytes(data["icon"].split(',')[1].encode()))
                    serverEmbed.set_thumbnail(file=disnake.File("icon.png"))
                else:
                    serverEmbed.set_thumbnail(file=disnake.File("default_icon.png"))
                serverEmbed.add_field(name="Port", value=port, inline=False)
                serverEmbed.add_field(name="Version", value=data['version'], inline=False)
                serverEmbed.add_field(name="Players", value=f"{data['players']['online']}/{data['players']['max']}", inline=False)
                if 'software' in data:
                    serverEmbed.add_field(name="Software", value=data['software'], inline=False)
                serverEmbed.set_image(url=img)
            else:
                serverEmbed = disnake.Embed(
                    title=f"Server: '{address}'",
                    description="<:cross:1002964682585407591> Offline",
                    color=self.bot.colour_error
                )
                serverEmbed.set_thumbnail(file=disnake.File("default_icon_64.png"))
                serverEmbed.set_image(url=img)
            await inter.edit_original_message(embed=serverEmbed)
        else:
            errorEmbed = disnake.Embed(
                title=f"API Error",
                description=f"Error {response.status_code} occured with server status api.",
                color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.edit_original_message(embed=errorEmbed)


        