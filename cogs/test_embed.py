import disnake
from disnake.ext import commands
from .embeds import New_Embed
import json

# allows the cog to be loaded
def setup(bot):
    bot.add_cog(TestEmbed(bot))

class TestEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def embed(self, inter):
        global embed
        embed = New_Embed("test", description="this is a test")
        embed_msg = await inter.channel.send(embed=embed)
        await embed_msg.add_reaction("👍")
        await embed_msg.add_reaction("👎")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        bot = self.bot
        guild = bot.get_guild(payload.guild_id)
        # whats payload??
        if payload.member != guild.me:
            # create the new embed with the updated colour
            message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            embed.set_color(self.bot.colour_success)
            await message.edit(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        bot = self.bot
        guild = bot.get_guild(payload.guild_id)
        # whats payload??
        if payload.member != guild.me:
            # create the new embed with the updated colour
            message = await bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            embed.set_color(self.bot.colour_error)
            await message.edit(embed=embed)
