import disnake
from disnake.ext import commands
import json

def setup(bot):
    bot.add_cog(suggestionsCog(bot))

def checkChannels():
    with open('data.json', 'r') as f:
        data = json.load(f)
        channels = data["suggestions"]["channels"]
        return channels

def editChannels(channels):
    with open('data.json', 'r') as f:
        data = json.load(f)
    data["suggestions"]["channels"] = channels
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


class suggestionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #Create suggestion embed from message in correct channel
    @commands.Cog.listener()
    async def on_message(self, message):
        channels = checkChannels()
        bot = self.bot
        if message.channel.id in channels and not message.author.bot:
            await message.delete()
            suggestEmbed = disnake.Embed(
                description=message.content,
                color=self.bot.colour_neutral)
            suggestEmbed.set_author(name=f"Suggestion from {message.author}", icon_url=message.author.avatar)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            suggestEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            embed_msg = await message.channel.send(embed=suggestEmbed)
            await embed_msg.add_reaction('👍')
            await embed_msg.add_reaction('👎')

    #Updates the colour of embed based on reaction ratio, when reaction is added
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channels = checkChannels()
        bot = self.bot
        guild = bot.get_guild(payload.guild_id)
        if payload.channel_id in channels and payload.member != guild.me:
            message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            reactions = message.reactions
            oldEmbed = message.embeds[0]
            if reactions[0].count > reactions[1].count:
                newEmbed = disnake.Embed(
                description=oldEmbed.description,
                color=self.bot.colour_success)
            elif reactions[0].count < reactions[1].count:
                newEmbed = disnake.Embed(
                description=oldEmbed.description,
                color=self.bot.colour_error)
            else:
                newEmbed = disnake.Embed(
                description=oldEmbed.description,
                color=self.bot.colour_neutral)
            newEmbed.set_author(name=oldEmbed.author.name, icon_url=oldEmbed.author.icon_url)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            newEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            await message.edit(embed=newEmbed)

    #Updates the colour on removal of reactions as well
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channels = checkChannels()
        bot = self.bot
        if payload.channel_id in channels:
            message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            reactions = message.reactions
            oldEmbed = message.embeds[0]
            if reactions[0].count > reactions[1].count:
                newEmbed = disnake.Embed(
                description=oldEmbed.description,
                color=self.bot.colour_success)
            elif reactions[0].count < reactions[1].count:
                newEmbed = disnake.Embed(
                description=oldEmbed.description,
                color=self.bot.colour_error)
            else:
                newEmbed = disnake.Embed(
                description=oldEmbed.description,
                color=self.bot.colour_neutral)
            newEmbed.set_author(name=oldEmbed.author.name, icon_url=oldEmbed.author.icon_url)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            newEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            await message.edit(embed=newEmbed)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def suggestionschannel(self, inter):
        pass

    @suggestionschannel.sub_command()
    async def set(inter, channel: disnake.TextChannel):
        """
        Sets a suggestions channel (admin)

        Parameters
        ----------
        channel: The channel to add
        """
        if inter.user.guild_permissions.administrator == True:
            channels = checkChannels()
            if channel.id not in channels:
                channels.append(channel.id)
                editChannels(channels)
                await inter.response.send_message(f'<:check:1002964750356987935> {channel.mention} has been added as a suggestions channel.')
            else:
                await inter.response.send_message(f'<:cross:1002964682585407591> {channel.mention} is already a suggestions channel.')
        else:
            await inter.response.send_message('<:cross:1002964682585407591> You do not have permission to use this command.', ephemeral=True)

    @suggestionschannel.sub_command()
    async def remove(inter, channel: disnake.TextChannel):
        """
        Removes a suggestions channel (admin)

        Parameters
        ----------
        channel: The channel to remove
        """
        if inter.user.guild_permissions.administrator == True:
            channels = checkChannels()
            if channel.id in channels:
                channels.remove(channel.id)
                editChannels(channels)
                await inter.response.send_message(f'<:check:1002964750356987935> {channel.mention} has been removed as a suggestions channel.')
            else:    
                await inter.response.send_message(f'<:cross:1002964682585407591> {channel.mention} is not a suggestions channel.')
        else:
            await inter.response.send_message('<:cross:1002964682585407591> You do not have permission to use this command.', ephemeral=True)
            
