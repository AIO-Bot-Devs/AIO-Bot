import disnake
from disnake.ext import commands
import json

def setup(bot):
    bot.add_cog(starboardCog(bot))

def checkServers():
    with open('data.json', 'r') as f:
        data = json.load(f)
        servers = data["starboard"]["servers"]
        return servers

def editServers(servers):
    with open('data.json', 'r') as f:
        data = json.load(f)
    data["starboard"]["servers"] = servers
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class starboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        bot = self.bot
        servers = checkServers()
        if str(payload.guild_id) in servers:
            starboard = bot.get_channel(servers[str(payload.guild_id)])
            message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            reactions = message.reactions
            for reaction in reactions:
                if reaction.emoji == '⭐':
                    await message.pin(reason='⭐')  
                    starboardEmbed = disnake.Embed(
                        description=message.content + f'\n[[jump to message]]({message.jump_url})',
                        color=0xffd700)
                    starboardEmbed.set_author(name=f"{message.author}", icon_url=message.author.avatar)
                    owner = await self.bot.fetch_user(self.bot.owner_id)
                    starboardEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                    await starboard.send(content=f"⭐ {message.channel.mention}", embed=starboardEmbed)

    
    
    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def starboardchannel(self, inter):
        pass

    @starboardchannel.sub_command()
    async def set(inter, channel: disnake.TextChannel):
        """
        Sets the starboard channel (admin)

        Parameters
        ----------
        channel: The channel to set
        """
        if inter.user.guild_permissions.administrator == True:
            servers = checkServers()
            if str(inter.guild.id) in servers and servers[str(inter.guild.id)] == channel.id:
                await inter.response.send_message(f'<:cross:1002964682585407591> {channel.mention} is already set as the starboard channnel.')
            else: 
                servers[str(inter.guild.id)] = channel.id
                editServers(servers)
                await inter.response.send_message(f'<:check:1002964750356987935> {channel.mention} has been set as the starboard channel.')
        else:
            await inter.response.send_message('<:cross:1002964682585407591> You do not have permission to use this command.', ephemeral=True)

    @starboardchannel.sub_command()
    async def remove(self, inter):
        """
        Removes the starboard channel (admin)
        """
        bot = self.bot
        if inter.user.guild_permissions.administrator == True:
            servers = checkServers()
            if str(inter.guild.id) in servers:
                channel = bot.get_channel(servers[str(inter.guild.id)])
                await inter.response.send_message(f'<:check:1002964750356987935> {channel.mention} has been removed as the starboard channel.')
                del servers[str(inter.guild.id)]
                editServers(servers)
            else:    
                await inter.response.send_message(f'<:cross:1002964682585407591> There is no starboard channel setup in this server. Consider using ``/starboardchannel set``')
        else:
            await inter.response.send_message('<:cross:1002964682585407591> You do not have permission to use this command.', ephemeral=True)