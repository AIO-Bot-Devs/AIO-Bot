import disnake
from disnake.ext import commands, tasks
import datetime
import json
import random

# allows the cog to be loaded
def setup(bot):
    bot.add_cog(remindersCog(bot))

# function to edit reminders
def editReminders(reminders, birthdays):
    with open('data.json', 'r') as f:
        data = json.load(f)
    # changes the reminders and birthdays and dumps the data back into the file
    data["reminders"]["reminders"] = reminders
    data["reminders"]["birthdays"] = birthdays
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# function to grab reminders
def checkReminders():
    # grabs the reminders and birthdays from the data file
    with open('data.json', 'r') as f:
        data = json.load(f)
        reminders = data["reminders"]["reminders"]
        birthdays = data["reminders"]["birthdays"]
        return reminders, birthdays

# function to get the next birthday
def getNextBirthday(birthdate):
    # adds a year to the birthdate until it is in the future
    now = datetime.datetime.now(datetime.timezone.utc)
    nextBirthday = datetime.datetime.fromtimestamp(birthdate).replace(tzinfo=datetime.timezone.utc)
    while nextBirthday < now:
        nextBirthday = nextBirthday + datetime.timedelta(days=365)
    return int(nextBirthday.timestamp())


# class for all the reminders commands
class remindersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        # adds the task when the cog is loaded
        self.birthdayCheck.start()

    # cancels the task if the cog is unloaded
    def cog_unload(self):
        self.birthdayCheck.cancel()

    # a task which runs every day at 12:00 UTC to check birthdays
    @tasks.loop(time=datetime.time(hour=12, tzinfo=datetime.timezone.utc))
    async def birthdayCheck(self):        
        print("Running birthday check...")
        print(f"Time: {datetime.datetime.now(datetime.timezone.utc)}")
        bot = self.bot
        # get birthdays dictionary
        reminders = checkReminders()
        birthdays = reminders[1]
        # loops over every server and user in the birthdays dictionary
        for server in birthdays["servers"]:
            for user in birthdays["servers"][server]["users"]:
                date = int(birthdays["servers"][server]["users"][user])
                user = await bot.fetch_user(int(user))
                # if the date is in the past, send a birthday message
                if date <= datetime.datetime.now(datetime.timezone.utc).timestamp():
                    birthdayEmbed = disnake.Embed(
                        title=f":tada: Happy Birthday {user.name}!",
                        description=f"It's <t:{date}:D>, so everyone wish {user.mention} a happy birthday! The dev team says have a great day!",
                        color=bot.colour_success
                    )
                    owner = await self.bot.fetch_user(self.bot.owner_id)
                    birthdayEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
                    birthdayEmbed.set_thumbnail(url="https://evilpanda.me/files/birthday.png")
                    # send the message to the birthday channel from the data file 
                    # getting the guild separately ensures the channel is in the same server
                    guild = await bot.fetch_guild(int(server))
                    channel = await bot.fetch_channel(int(birthdays["servers"][server]["channel"]))
                    msg = await channel.send(embed=birthdayEmbed)
                    # adds four birthday emojis as reactions in a random order
                    emoji_list = ['🎉', '🎂', '🎁', '🎈']
                    random.shuffle(emoji_list)
                    await msg.add_reaction(emoji_list[0])
                    await msg.add_reaction(emoji_list[1])
                    await msg.add_reaction(emoji_list[2])
                    await msg.add_reaction(emoji_list[3])
                    # updates the birthday in the data file
                    date = getNextBirthday(date)
                    birthdays["servers"][server]["users"][str(user.id)] = date
                    editReminders(reminders[0], birthdays)
        print("Birthday checks completed (hopefully)")

    # waits for the bot to be ready before running the task, in case of bot starting at around 12:00 UTC
    @birthdayCheck.before_loop
    async def botReadyCheck(self):
        print('Waiting for bot to be ready...')
        await self.bot.wait_until_ready()
        print("Adding birthday check task")

    # default command
    @commands.slash_command()
    async def birthday(self, inter):
        pass
    
    # this subcommand will add or edit a birthday to the list of birthdays
    # set name in decorator to avoid two functions with same name
    @birthday.sub_command(name="set")
    async def set1(self, inter, date):
        """
        Add or edit your birthday
        
        Parameters
        ----------
        date: Your birthdate: DD/MM/YYYY
        """
        bot = self.bot
        # try if the date is valid
        try:
            # get the current reminders
            reminders = checkReminders()
            # if the birthday function is enabled then add the birthday to the list of birthdays
            if str(inter.guild.id) in reminders[1]["servers"]:
                # format the date and set the users birthday to the timestamp
                date = date.split('/')
                date = datetime.datetime(int(date[2]), int(date[1]), int(date[0]), hour=12)
                timestamp = int(date.replace(tzinfo=datetime.timezone.utc).timestamp())
                reminders[1]["servers"][str(inter.guild.id)]["users"][str(inter.user.id)] = timestamp
                editReminders(reminders[0], reminders[1])
                # sets the birthday channel to the one mentioned in data.json
                birthdayChannel = bot.get_channel(reminders[1]["servers"][str(inter.guild.id)]["channel"])
                # creates an embed with the users birthday
                successEmbed = disnake.Embed(
            title=f"Birthday added",
            description=f"Your birth date has been set as <t:{timestamp}:D>. We will remind everyone <t:{getNextBirthday(timestamp)}:R> in {birthdayChannel.mention}.",
            color=self.bot.colour_success)
                # adds a footer to the embed
                owner = await self.bot.fetch_user(self.bot.owner_id)
                successEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
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
                errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
                errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        # if the date is invalid then send an error message
        except (ValueError, IndexError):
            # creates an embed with the error message
            errorEmbed = disnake.Embed(
        title=f"Invalid birthday date",
        description=f"Please enter a valid date.\n\nUse the format: ``/birthday set DD/MM/YYYY``",
        color=self.bot.colour_error)
            # adds a footer to the embed
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)

    # this subcommand will remove a birthday from the list of birthdays
    # set name in decorator to avoid two functions with same name
    @birthday.sub_command(name="delete")
    async def remove1(self, inter):
        """
        Delete your birthday from our database
        
        Parameters
        ----------
        date: Your birthdate: DD/MM/YYYY
        """
        bot = self.bot
        # get the current reminders
        reminders = await checkReminders()
        # if the birthday function is enabled then remove the birthday from the list of birthdays
        if str(inter.guild.id) in reminders[1]["servers"]:
            # if the user has a birthday then remove it
            if str(inter.user.id) in reminders[1]["servers"][str(inter.guild.id)]["users"]:
                del reminders[1]["servers"][str(inter.guild.id)]["users"][str(inter.user.id)]
                editReminders(reminders[0], reminders[1])
                # creates an embed with the success message
                successEmbed = disnake.Embed(
            title=f"Birthday removed",
            description=f"Your birth date has been removed.",
            color=self.bot.colour_success)
                # adds a footer to the embed
                owner = await self.bot.fetch_user(self.bot.owner_id)
                successEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
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
                errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
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
            errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)

    # this is the default command for changing the birthday channel
    @birthday.sub_command_group()
    async def channel(self, inter):
        pass

    # this subcommand will set the birthday channel
    # set name in decorator to avoid two functions with same name
    @channel.sub_command(name="set")
    async def set2(self, inter, channel: disnake.TextChannel):
        """
        Change or setup the birthday channel

        Parameters
        ----------
        channel: The channel to set
        """
        if inter.user.guild_permissions.administrator:
            bot = self.bot
            # get the current reminders
            reminders = checkReminders()
            # changes channel.id and list of users 
            reminders[1]["servers"][str(inter.guild.id)] = {"channel": channel.id, "users": {}}
            # why is this here? I don't know
            reminders[1]["servers"][str(inter.guild.id)]
            # edits the reminders
            editReminders(reminders[0], reminders[1])
            # creates an embed with the success message
            successEmbed = disnake.Embed(
        title=f"Birthday channel set",
        description=f"Birthdays will now be announced in {channel.mention}.",
        color=self.bot.colour_success)
            # adds a footer to the embed
            owner = await self.bot.fetch_user(self.bot.owner_id)
            successEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            successEmbed.set_thumbnail(url="https://evilpanda.me/files/success.png")
            await inter.response.send_message(embed=successEmbed)
        else:
            errorEmbed = disnake.Embed(
                title=f"Permission error",
                description=f"You don't have permission to use this command.",
                color=self.bot.colour_error
            )
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)


    # this subcommand will remove the birthday channel
    # set name in decorator to avoid two functions with same name
    @channel.sub_command(name="remove")
    async def remove2(self, inter):
        """
        Remove the birthday channel
        """
        if inter.user.guild_permissions.administrator:
            bot = self.bot
            # get the current reminders
            reminders = checkReminders()
            # checks if server in reminders
            if str(inter.guild.id) in reminders[1]["servers"]:
                # removes the channel from the list of channels
                del reminders[1]["servers"][str(inter.guild.id)]
                editReminders(reminders[0], reminders[1])
                # creates an embed with the success message
                successEmbed = disnake.Embed(
            title=f"Birthday channel removed",
            description=f"Birthdays will no longer be announced.",
            color=self.bot.colour_success)
                # adds a footer to the embed
                owner = await self.bot.fetch_user(self.bot.owner_id)
                successEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
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
                errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
                errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        else:
            errorEmbed = disnake.Embed(
                title=f"Permission error",
                description=f"You don't have permission to use this command.",
                color=self.bot.colour_error
            )
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)
