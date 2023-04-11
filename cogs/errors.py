import disnake
from disnake.ext import commands


#allows the cog to be loaded
def setup(bot):
    bot.add_cog(errorCog(bot))


# cog for error handling
class errorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        bot = self.bot
        if error.__class__ == disnake.ext.commands.errors.CheckFailure:
            if str(error) == "The check functions for command 'admin' failed.":
                print(f"Admin command attempted to be used by non-admin user. {inter.author.name}#{inter.author.discriminator} ({inter.author.id})")
            await inter.response.send_message(f"{bot.emoji_error} You do not have permission to use this command.", ephemeral=True)
        elif error == disnake.ext.commands.errors.MissingRequiredArgument:
            await inter.response.send_message(f"{bot.emoji_error} You are missing a required argument.", ephemeral=True)
        elif error == disnake.ext.commands.errors.BadArgument:
            await inter.response.send_message(f"{bot.emoji_error} You have provided an invalid argument.", ephemeral=True)
        elif error == disnake.ext.commands.errors.CommandNotFound:
            await inter.response.send_message(f"{bot.emoji_error} This command does not exist.", ephemeral=True)
        else:
            print(f"An unknown slash command error occurred. User: {inter.author.name}#{inter.author.discriminator} ({inter.author.id})")
            print(f"{error.__class__}: {str(error)}")
            print(f"Context: {error.__context__}")
            print(f"Traceback: {error.__traceback__.tb_frame.f_code}")
            await inter.response.send_message(f"{bot.emoji_error} An unknown error occurred.", ephemeral=True)





