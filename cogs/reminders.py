import disnake
from disnake.ext import commands
import datetime
import json

def setup(bot):
    bot.add_cog(remindersCog(bot))

def editReminders(reminders, birthdays):
    with open('../data.json', 'r') as f:
        data = json.load(f)
    data["reminders"]["reminders"] = reminders
    data["reminders"]["birthdays"] = birthdays
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def checkReminders():
    with open('../data.json', 'r') as f:
        data = json.load(f)
        reminders = data["reminders"]["reminders"]
        birthdays = data["reminders"]["birthdays"]
        return reminders, birthdays

def getNextBirthday(birthdate):
    now = datetime.datetime.now(datetime.timezone.utc)
    now = int(now.replace(tzinfo=datetime.timezone.utc).timestamp())
    nextBirthday = birthdate
    while nextBirthday < now:
        nextBirthday = nextBirthday + 31557600 
    return nextBirthday



class remindersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None


    @commands.slash_command()
    async def birthday(self, inter):
        pass

    @birthday.sub_command()
    async def set(self, inter, date):
        """
        Adds (or edits) your birthday

        Parameters
        ----------
        date: Your birthdate: DD/MM/YYYY
        """
        try:
            reminders = await checkReminders() 
            if str(inter.guild.id) in reminders[1]["servers"]:
                date = date.split('/')
                date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]), hour=12)
                timestamp = int(date.replace(tzinfo=datetime.timezone.utc).timestamp())
                reminders[1]["servers"][str(inter.guild.id)]["users"][str(inter.user.id)] = timestamp
                await editReminders(reminders[0], reminders[1])
                birthdayChannel = await self.bot.get_channel(reminders[1]["servers"][str(inter.guild.id)])
                successEmbed = disnake.Embed(
            title=f"Birthday added",
            description=f"Your birth date has been set as <t:{timestamp}:D>. We will remind everyone <t:{getNextBirthday(timestamp)}:R> in {birthdayChannel.mention}.",
            color=self.bot.colour_success)
                owner = await self.bot.fetch_user(self.bot.owner_id)
                successEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                successEmbed.set_thumbnail(url="https://evilpanda.me/files/notify.png")
                await inter.response.send_message(embed=successEmbed)
            else:
                errorEmbed = disnake.Embed(
            title=f"Birthday function not enabled",
            description=f"Please ask the server owner to set this up, using `/setup` or `/birthdaychannel`.",
            color=self.bot.colour_error)
                owner = await self.bot.fetch_user(self.bot.owner_id)
                errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        except:
            errorEmbed = disnake.Embed(
        title=f"Invalid birthday date",
        description=f"Please enter a valid date.\n\nUse the format: ``/birthday set DD/MM/YYYY``",
        color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)

    @birthday.sub_command()
    async def remove(self, inter):
        """
        Removes your birthday
        """
        reminders = await checkReminders()
        if str(inter.guild.id) in reminders[1]["servers"]:
            if str(inter.user.id) in reminders[1]["servers"][str(inter.guild.id)]["users"]:
                del reminders[1]["servers"][str(inter.guild.id)]["users"][str(inter.user.id)]
                await editReminders(reminders[0], reminders[1])
                successEmbed = disnake.Embed(
            title=f"Birthday removed",
            description=f"Your birth date has been removed.",
            color=self.bot.colour_success)
                owner = await self.bot.fetch_user(self.bot.owner_id)
                successEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                successEmbed.set_thumbnail(url="https://evilpanda.me/files/bin.png")
                await inter.response.send_message(embed=successEmbed)
            else:
                errorEmbed = disnake.Embed(
            title=f"Birthday not found",
            description=f"You don't have a birthday set.",
            color=self.bot.colour_error)
                owner = await self.bot.fetch_user(self.bot.owner_id)
                errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        else:
            errorEmbed = disnake.Embed(
        title=f"Birthday function not enabled",
        description=f"Please ask the server owner to set this up, using `/setup` or `/birthdaychannel`.",
        color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)

    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def birthdaychannel(self, inter):
        pass

    @birthdaychannel.sub_command()
    async def set(self, inter, channel: disnake.TextChannel):
        """
        Sets the channel for birthday reminders

        Parameters
        ----------
        channel: The channel to set
        """
        reminders = await checkReminders()
        reminders[1]["servers"][str(inter.guild.id)] = {"channel": channel.id, "users": {}}
        reminders[1]["servers"][str(inter.guild.id)]
        await editReminders(reminders[0], reminders[1])
        successEmbed = disnake.Embed(
    title=f"Birthday channel set",
    description=f"Birthdays will now be announced in {channel.mention}.",
    color=self.bot.colour_success)
        owner = await self.bot.fetch_user(self.bot.owner_id)
        successEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
        successEmbed.set_thumbnail(url="https://evilpanda.me/files/success.png")
        await inter.response.send_message(embed=successEmbed)

    @birthdaychannel.sub_command()
    async def remove(self, inter, channel: disnake.TextChannel):
        """
        Removes the channel for birthday reminders

        Parameters
        ----------
        channel: The channel to remove
        """
        reminders = await checkReminders()
        if str(inter.guild.id) in reminders[1]["servers"]:
            del reminders[1]["servers"][str(inter.guild.id)]
            await editReminders(reminders[0], reminders[1])
            successEmbed = disnake.Embed(
        title=f"Birthday channel removed",
        description=f"Birthdays will no longer be announced.",
        color=self.bot.colour_success)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            successEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            successEmbed.set_thumbnail(url="https://evilpanda.me/files/bin.png")
            await inter.response.send_message(embed=successEmbed)
        else:
            errorEmbed = disnake.Embed(
        title=f"Birthday channel not set",
        description=f"No birthday channel has been set.",
        color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)
