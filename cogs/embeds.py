from disnake import Embed
import os.path
import json
import asyncio

with open(os.path.dirname(__file__) + '/../config.json', 'r') as f:
    data = json.load(f)
    colours = data["colours"]

# TODO: grab the default footer from the database and set it to the footer variable
class New_Embed(Embed):
    def __init__(
        self,
        title: str = None, 
        type: str = "rich",
        description: str = None,
        color = int(colours["neutral"], base=16),
        author = "this is an author", 
        footer = "this is a footer", 
        icon = "https://cdn.discordapp.com/avatars/867530986753098765/867530986753098765.png?size=1024",
    ):
        super().__init__(title=title, type=type, description=description, color=color)
        self.set_author(name=author, icon_url=icon)
        self.set_footer(text=footer)

    def set_color(self, color):
        self.color = color
        return self