import disnake
from disnake.ext import commands
import datetime
import json

# allows the cog to be loaded
def setup(bot):
    bot.add_cog(remindersCog(bot))

# function to edit reminders
def editReminders(reminders, birthdays):
    with open('../data.json', 'r') as f:
        data = json.load(f)
    # changes the reminders and birthdays and dumps the data back into the file
    data["reminders"]["reminders"] = reminders
    data["reminders"]["birthdays"] = birthdays
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# function to grab reminders
def checkReminders():
    # grabs the reminders and birthdays from the data file
    with open('../data.json', 'r') as f:
        data = json.load(f)
        reminders = data["reminders"]["reminders"]
        birthdays = data["reminders"]["birthdays"]
        return reminders, birthdays

# function to get the next birthday
def getNextBirthday(birthdate):
    # dunno how this works
    now = datetime.datetime.now(datetime.timezone.utc)
    now = int(now.replace(tzinfo=datetime.timezone.utc).timestamp())
    nextBirthday = birthdate
    while nextBirthday < now:
        nextBirthday = nextBirthday + 31557600 
    return nextBirthday

# class for all the reminders commands
class remindersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # default command
    @commands.slash_command()
    async def birthday(self, inter):
        pass
    
    # this subcommand will add or edit a birthday to the list of birthdays
    @birthday.sub_command()
    async def set(self, inter, date):
        """
        Parameters
        ----------
        date: Your birthdate: DD/MM/YYYY
        """
        # try if the date is valid
        try:
            # get the current reminders
            reminders = await checkReminders()
            # if the birthday function is enabled then add the birthday to the list of birthdays
            if str(inter.guild.id) in reminders[1]["servers"]:
                # format the date and set the users birthday to the timestamp
                date = date.split('/')
                date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]), hour=12)
                timestamp = int(date.replace(tzinfo=datetime.timezone.utc).timestamp())
                reminders[1]["servers"][str(inter.guild.id)]["users"][str(inter.user.id)] = timestamp
                await editReminders(reminders[0], reminders[1])
                # sets the birthday channel to the one mentioned in data.json
                birthdayChannel = await self.bot.get_channel(reminders[1]["servers"][str(inter.guild.id)])
                # creates an embed with the users birthday
                successEmbed = disnake.Embed(
            title=f"Birthday added",
            description=f"Your birth date has been set as <t:{timestamp}:D>. We will remind everyone <t:{getNextBirthday(timestamp)}:R> in {birthdayChannel.mention}.",
            color=self.bot.colour_success)
                # adds a footer to the embed
                owner = await self.bot.fetch_user(self.bot.owner_id)
                successEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                successEmbed.set_thumbnail(url="https://evilpanda.me/files/notify.png")
                await inter.response.send_message(embed=successEmbed)
            # if the birthday function is disabled then send an error message
            else:
                # creates an embed with the error message
                errorEmbed = disnake.Embed(
            title=f"Birthday function not enabled",
            description=f"Please ask the server owner to set this up, using `/setup` or `/birthdaychannel`.",
            color=self.bot.colour_error)
                # adds a footer to the embed
                owner = await self.bot.fetch_user(self.bot.owner_id)
                errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        # if the date is invalid then send an error message
        except:
            # creates an embed with the error message
            errorEmbed = disnake.Embed(
        title=f"Invalid birthday date",
        description=f"Please enter a valid date.\n\nUse the format: ``/birthday set DD/MM/YYYY``",
        color=self.bot.colour_error)
            # adds a footer to the embed
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)

    # this subcommand will remove a birthday from the list of birthdays
    @birthday.sub_command()
    async def remove(self, inter):
        # get the current reminders
        reminders = await checkReminders()
        # if the birthday function is enabled then remove the birthday from the list of birthdays
        if str(inter.guild.id) in reminders[1]["servers"]:
            # if the user has a birthday then remove it
            if str(inter.user.id) in reminders[1]["servers"][str(inter.guild.id)]["users"]:
                del reminders[1]["servers"][str(inter.guild.id)]["users"][str(inter.user.id)]
                await editReminders(reminders[0], reminders[1])
                # creates an embed with the success message
                successEmbed = disnake.Embed(
            title=f"Birthday removed",
            description=f"Your birth date has been removed.",
            color=self.bot.colour_success)
                # adds a footer to the embed
                owner = await self.bot.fetch_user(self.bot.owner_id)
                successEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                successEmbed.set_thumbnail(url="https://evilpanda.me/files/bin.png")
                await inter.response.send_message(embed=successEmbed)
            # if the user doesn't have a birthday then send an error message
            else:
                # creates an embed with the error message
                errorEmbed = disnake.Embed(
            title=f"Birthday not found",
            description=f"You don't have a birthday set.",
            color=self.bot.colour_error)
                # adds a footer to the embed
                owner = await self.bot.fetch_user(self.bot.owner_id)
                errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        # if the birthday function is disabled then send an error message
        else:
            # creates an embed with the error message
            errorEmbed = disnake.Embed(
        title=f"Birthday function not enabled",
        description=f"Please ask the server owner to set this up, using `/setup` or `/birthdaychannel`.",
        color=self.bot.colour_error)
            # adds a footer to the embed
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)

    # this is the default command for changing the birthday channel
    @commands.slash_command()
    @commands.default_member_permissions(administrator=True)
    async def birthdaychannel(self, inter):
        pass

    # this subcommand will set the birthday channel
    @birthdaychannel.sub_command()
    async def set(self, inter, channel: disnake.TextChannel):
        """
        Parameters
        ----------
        channel: The channel to set
        """
        # get the current reminders
        reminders = await checkReminders()
        # changes channel.id and list of users 
        reminders[1]["servers"][str(inter.guild.id)] = {"channel": channel.id, "users": {}}
        # why is this here? I don't know
        reminders[1]["servers"][str(inter.guild.id)]
        # edits the reminders
        await editReminders(reminders[0], reminders[1])
        # creates an embed with the success message
        successEmbed = disnake.Embed(
    title=f"Birthday channel set",
    description=f"Birthdays will now be announced in {channel.mention}.",
    color=self.bot.colour_success)
        # adds a footer to the embed
        owner = await self.bot.fetch_user(self.bot.owner_id)
        successEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
        successEmbed.set_thumbnail(url="https://evilpanda.me/files/success.png")
        await inter.response.send_message(embed=successEmbed)

    # this subcommand will remove the birthday channel
    @birthdaychannel.sub_command()
    async def remove(self, inter, channel: disnake.TextChannel):
        """
        Parameters
        ----------
        channel: The channel to remove
        """
        # get the current reminders
        reminders = await checkReminders()
        # checks if server in reminders
        if str(inter.guild.id) in reminders[1]["servers"]:
            # removes the channel from the list of channels
            del reminders[1]["servers"][str(inter.guild.id)]
            await editReminders(reminders[0], reminders[1])
            # creates an embed with the success message
            successEmbed = disnake.Embed(
        title=f"Birthday channel removed",
        description=f"Birthdays will no longer be announced.",
        color=self.bot.colour_success)
            # adds a footer to the embed
            owner = await self.bot.fetch_user(self.bot.owner_id)
            successEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            successEmbed.set_thumbnail(url="https://evilpanda.me/files/bin.png")
            await inter.response.send_message(embed=successEmbed)
        # if the server isn't in the list of servers then send an error message
        else:
            # creates an embed with the error message
            errorEmbed = disnake.Embed(
        title=f"Birthday channel not set",
        description=f"No birthday channel has been set.",
        color=self.bot.colour_error)
            # adds a footer to the embed
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)
