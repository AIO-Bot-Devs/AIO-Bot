import disnake
from disnake.ext import commands
import json

# allows the cog to be loaded
def setup(bot):
    bot.add_cog(suggestionsCog(bot))

# grabs the list of channels
def checkChannels():
    with open('data.json', 'r') as f:
        data = json.load(f)
        channels = data["suggestions"]["channels"]
        return channels

# edits the list of channels
def editChannels(channels):
    with open('data.json', 'r') as f:
        data = json.load(f)
    data["suggestions"]["channels"] = channels
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# class for all the suggestion commands
class suggestionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def add_embed(self, description, color, name, icon):
        embed = disnake.Embed(
                description=description,
                color=color)
        embed.set_author(name=name, icon_url=icon)
        # set the embed footer
        owner = await self.bot.fetch_user(self.bot.owner_id)
        embed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
        return embed

    async def reaction_check(self, bot, payload):
        message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
        reactions = message.reactions
        oldEmbed = message.embeds[0]
        # added the info for the embed to variables
        description = oldEmbed.description
        name = oldEmbed.author.name
        icon = oldEmbed.author.icon_url
        # if there are more thumbs up than thumbs down, set the colour to green
        if reactions[0].count > reactions[1].count:
            newEmbed = await self.add_embed(description, self.bot.colour_success, name, icon)
        # if there are more thumbs down than thumbs up, set the colour to red
        elif reactions[0].count < reactions[1].count:
            newEmbed = await self.add_embed(description, self.bot.colour_error, name, icon)
        # if there are an equal amount of thumbs up and thumbs down, set the colour to neutral
        else:
            newEmbed = await self.add_embed(description, self.bot.colour_neutral, name, icon)
        return message, newEmbed

    # create a suggestion embed
    @commands.Cog.listener()
    async def on_message(self, message):
        bot = self.bot
        channels = checkChannels()
        # if the message is in a suggestion channel and is not a bot
        if message.channel.id in channels and not message.author.bot:
            # delete the message
            await message.delete()
            # create the embed
            description = message.content
            color = self.bot.colour_neutral
            name = f"Suggestion from {message.author}"
            icon = message.author.avatar
            suggestEmbed = await self.add_embed(description, color, name, icon)
            embed_msg = await message.channel.send(embed=suggestEmbed)
            # add the reactions, should change to buttons
            await embed_msg.add_reaction('👍')
            await embed_msg.add_reaction('👎')

    # Updates the colour of an embed based on the ratio of upvotes to downvotes
    # Only when reactions are added
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channels = checkChannels()
        bot = self.bot
        guild = bot.get_guild(payload.guild_id)
        # whats payload??
        if payload.channel_id in channels and payload.member != guild.me:
            # create the new embed with the updated colour
            message, newEmbed = await self.reaction_check(bot, payload)
            await message.edit(embed=newEmbed)

    # Updates the colour of an embed based on the ratio of upvotes to downvotes
    # Only when reactions are removed
    # Could be combined with the above function
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channels = checkChannels()
        bot = self.bot
        if payload.channel_id in channels:
            # create the new embed with the updated colour
            message, newEmbed = await self.reaction_check(bot, payload)
            await message.edit(embed=newEmbed)

    # default command for the suggestions channel command
    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def suggestionschannel(self, inter):
        pass

    # adds a channel to the list of suggestion channels
    @suggestionschannel.sub_command()
    async def set(self, inter, channel: disnake.TextChannel):
        """
        Parameters
        ----------
        channel: The channel to add
        """
        bot = self.bot
        # if the user is an admin, add the channel to the list, otherwise send an error message
        if inter.user.guild_permissions.administrator == True:
            channels = checkChannels()
            # if the channel is already in the list, send an error message
            if channel.id not in channels:
                channels.append(channel.id)
                editChannels(channels)
                await inter.response.send_message(f'{bot.emoji_check} {channel.mention} has been added as a suggestions channel.')
            else:
                await inter.response.send_message(f'{bot.emoji_cross} {channel.mention} is already a suggestions channel.')
        else:
            await inter.response.send_message(f'{bot.emoji_cross} You do not have permission to use this command.', ephemeral=True)

    # removes a channel from the list of suggestion channels
    @suggestionschannel.sub_command()
    async def remove(self, inter, channel: disnake.TextChannel):
        """
        Parameters
        ----------
        channel: The channel to remove
        """
        bot = self.bot
        # if the user is an admin, remove the channel from the list, otherwise send an error message
        if inter.user.guild_permissions.administrator == True:
            channels = checkChannels()
            # if the channel is in the list, remove it, otherwise send an error message
            if channel.id in channels:
                channels.remove(channel.id)
                editChannels(channels)
                await inter.response.send_message(f'{bot.emoji_check} {channel.mention} has been removed as a suggestions channel.')
            else:    
                await inter.response.send_message(f'{bot.emoji_cross} {channel.mention} is not a suggestions channel.')
        else:
            await inter.response.send_message(f'{bot.emoji_cross} You do not have permission to use this command.', ephemeral=True)
            
