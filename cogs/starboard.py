import disnake
from disnake.ext import commands
import json

# allows the cog to be loaded
def setup(bot):
    bot.add_cog(starboardCog(bot))

# function to check list of servers
def checkServers():
    with open('data.json', 'r') as f:
        data = json.load(f)
        servers = data["starboard"]["servers"]
        return servers

# function to edit list of server
def editServers(servers):
    with open('data.json', 'r') as f:
        data = json.load(f)
    data["starboard"]["servers"] = servers
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# class for all the starboard commands
class starboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # function to add to starboard upon reaction
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        bot = self.bot
        servers = checkServers()
        # if starboard is enabled in your server
        if str(payload.guild_id) in servers:
            # TODO: reformats this for fewer calls
            # grabs the starboard channel
            starboard = bot.get_channel(servers[str(payload.guild_id)])
            # grabs the message that was reacted to
            message = bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            # grab the reaction that was added
            reactions = message.reactions
            for reaction in reactions:
                # if the reaction is a star, pin the message
                if reaction.emoji == '⭐':
                    await message.pin(reason='⭐') 
                    # create the embed
                    starboardEmbed = disnake.Embed(
                        description=message.content + f'\n[[jump to message]]({message.jump_url})',
                        color=0xffd700)
                    # set the embed author
                    starboardEmbed.set_author(name=f"{message.author}", icon_url=message.author.avatar)
                    # set the embed footer
                    starboardEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
                    await starboard.send(content=f"⭐ {message.channel.mention}", embed=starboardEmbed)

    
    # default command for starboard channel
    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def starboardchannel(self, inter):
        pass

    # subcommand to set the starboard channel
    @starboardchannel.sub_command()
    async def set(self, inter, channel: disnake.TextChannel):
        """
        Parameters
        ----------
        channel: The channel to set
        """
        bot = self.bot
        # if the user is an admin allow them to set the channel, otherwise deny
        if inter.user.guild_permissions.administrator == True:
            servers = checkServers()
            # if a starboard channel is already set, send error message
            if str(inter.guild.id) in servers and servers[str(inter.guild.id)] == channel.id:
                await inter.response.send_message(f'{bot.emoji_cross} {channel.mention} is already set as the starboard channnel.')
            # if a starboard channel is not set, set the channel
            else: 
                servers[str(inter.guild.id)] = channel.id
                editServers(servers)
                await inter.response.send_message(f'{bot.emoji_check} {channel.mention} has been set as the starboard channel.')
        # if the user is not an admin, send error message
        else:
            await inter.response.send_message(f'{bot.emoji_cross} You do not have permission to use this command.', ephemeral=True)

    # subcommand to remove the starboard channel
    @starboardchannel.sub_command()
    async def remove(self, inter):
        """
        Removes the starboard channel (admin)
        """
        bot = self.bot
        # if the user is an admin allow them to remove the channel, otherwise deny
        if inter.user.guild_permissions.administrator == True:
            servers = checkServers()
            # if a starboard channel is set, remove the channel
            if str(inter.guild.id) in servers:
                channel = bot.get_channel(servers[str(inter.guild.id)])
                await inter.response.send_message(f'{bot.emoji_check} {channel.mention} has been removed as the starboard channel.')
                del servers[str(inter.guild.id)]
                editServers(servers)
            # if a starboard channel is not set, send error message
            else:    
                await inter.response.send_message(f'{bot.emoji_cross} There is no starboard channel setup in this server. Consider using ``/starboardchannel set``')
        # if the user is not an admin, send error message
        else:
            await inter.response.send_message(f'{bot.emoji_cross} You do not have permission to use this command.', ephemeral=True)