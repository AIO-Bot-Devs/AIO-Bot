"""This file stores the New_Embed class, which inherits from disnake.Embed."""
import json
import os.path

from disnake import Embed

with open(os.path.dirname(__file__) + "/../config.json", "r", encoding="UTF-8") as f:
    data = json.load(f)
    colours = data["colours"]
    default_footer = data["footer"]

# TODO: grab the default footer from the database and set it to the footer variable
class NewEmbed(Embed):
    """This class inherits from disnake.Embed and adds some extra functionality."""

    def __init__(
        self,
        title: str = None,
        embed_type: str = "rich",
        description: str = None,
        color=int(colours["neutral"], base=16),
        author="this is an author",
        footer=None,
        icon="https://cdn.discordapp.com/avatars/123456789012345678/123456789012345678.png",
        field_list=None,
    ):
        super().__init__(
            title=title, type=embed_type, description=description, color=color
        )
        self.set_author(name=author, icon_url=icon)
        if footer is None:
            self.set_footer(text=default_footer)
        else:
            self.set_footer(text=default_footer + " • " + footer)
        self.field_list = field_list
        if field_list is not None:
            for field in self.field_list:
                self.add_field(name=field[0], value=field[1], inline=False)

    def set_color(self, color):
        """This method sets the color of the embed."""
        self.color = color
        return self
