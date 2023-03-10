"""This file is used to test the embeds.py file. It is not intended to be used in production."""
import os.path

import disnake
from disnake.ext import commands
from disnake.ui import Button
from sqlalchemy.future import select

from .embeds import NewEmbed
from .models import Suggestions, async_session


def setup(bot):
    """allows the cog to be loaded"""
    bot.add_cog(TestEmbed(bot))


class TestEmbed(commands.Cog):
    """This cog is used to test the embeds.py file. It is not intended to be used in production."""

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def embed(self, inter):
        """This command creates an embed using the New_Embed class from embeds.py"""
        embed = NewEmbed("test", description="this is a test", suggestion=True)
        up_button = Button(label="up", style=disnake.ButtonStyle.green)
        down_button = Button(label="down", style=disnake.ButtonStyle.red)
        await inter.response.send_message(
            embed=embed, components=[up_button, down_button]
        )
        msg = await inter.original_response()
        rating = await add_suggestion(msg.id, 0)

    @commands.Cog.listener()
    async def on_button_click(self, inter: Button):
        """This listener changes the colour of the embed when a button is clicked."""
        if inter.component.label == "up":
            rating = await add_suggestion(inter.message.id, 1)
        elif inter.component.label == "down":
            rating = await add_suggestion(inter.message.id, -1)
        embed = NewEmbed(
            "test",
            description="this is a test",
            field_list=[("test", "down")],
            suggestion=True,
            rating=rating,
        )
        if rating > 0:
            color = self.bot.colour_success
        elif rating < 0:
            color = self.bot.colour_error
        else:
            color = self.bot.colour_neutral
        embed.set_color(color)
        await inter.response.edit_message(embed=embed)

    # @commands.Cog.listener()
    # async def on_raw_reaction_add(self, payload):
    #    """This listener changes the color of the embed based on the reaction."""
    #    bot = self.bot
    #    guild = bot.get_guild(payload.guild_id)
    #    # whats payload??
    #    if payload.member != guild.me:
    #        # create the new embed with the updated colour
    #        message = await bot.get_channel(payload.channel_id).fetch_message(
    #            payload.message_id
    #        )
    #        embed = message.embeds[0]
    #        embed = NewEmbed.set_color(embed, self.bot.colour_success)
    #        await payload.response.edit_message(embed=embed)


#
# @commands.Cog.listener()
# async def on_raw_reaction_remove(self, payload):
#    """This listener changes the color of the embed based on the reaction."""
#    bot = self.bot
#    guild = bot.get_guild(payload.guild_id)
#    # whats payload??
#    if payload.member != guild.me:
#        # create the new embed with the updated colour
#        message = await bot.get_channel(payload.channel_id).fetch_message(
#            payload.message_id
#        )
#        embed = message.embeds[0]
#        embed = NewEmbed.set_color(embed, self.bot.colour_success)
#        await payload.response.edit_message(embed=embed)
async def add_suggestion(message_id, rating):
    """Add a suggestion to the database."""
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Suggestions).where(Suggestions.message_id == message_id)
            )
            rating_row = result.scalars().first()
            if rating_row is None:
                session.add(Suggestions(message_id=message_id, rating=rating))
            else:
                rating_row.rating += rating
        await session.commit()
    if rating_row is None:
        return rating
    return rating_row.rating
