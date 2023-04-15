import disnake
from disnake.ext import commands


#allows the cog to be loaded
def setup(bot):
    bot.add_cog(errorsCog(bot))


# cog for error handling
class errorsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        bot = self.bot
        if error.__class__ == disnake.ext.commands.errors.CheckFailure:
            await inter.response.send_message(f"{bot.emoji_error} You do not have permission to use this command.", ephemeral=True)
        else:
            print(f"An unknown slash command error occurred. User: {inter.author.name}#{inter.author.discriminator} ({inter.author.id})")
            print(f"{error.__class__}: {str(error)}")
            print(f"Context: {error.__context__}")
            print(f"Traceback: {error.__traceback__.tb_frame.f_code}")
            await inter.response.send_message(f"{bot.emoji_error} An unknown error occurred.", ephemeral=True)





