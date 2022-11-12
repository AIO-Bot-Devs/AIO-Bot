import os
from dotenv import load_dotenv
import disnake
from disnake.ui import button, View
from disnake.ext import commands
import aiohttp
from table2ascii import table2ascii as t2a, Alignment
from PIL import Image, ImageDraw, ImageFont
import json
from .button_menu import ButtonMenu

# getting bot token from token.env
load_dotenv()
token = os.getenv("FOOTBALL_TOKEN")

# This is the class that will be used to create the commands
class TableCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # This is the command that will be used to get the league table
    @commands.slash_command(name="table", description="Get the league table for a specific league")
    async def table(self, inter, league_id: int,img: bool = False):
        # send request to api

        script_dir = os.path.dirname(__file__)
        rel_path = f"leagues/{league_id}.json"
        abs_file_path = os.path.join(script_dir, rel_path)
        # if there is text in league_id.json, then use that, otherwise, send a request to the api
        if os.path.exists(abs_file_path):
            with open(abs_file_path, "r") as f:
                data = json.load(f)
        else:                
            url = f"https://v3.football.api-sports.io/standings?league={league_id}&season=2022"
            payload={}
            headers = {
                'x-rapidapi-key': token,
                'x-rapidapi-host': 'v3.football.api-sports.io'
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, data=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        with open(abs_file_path, "w") as f:
                            f.write(response.text)
            # read the data from the file
            with open(abs_file_path, "r") as f:
                data = json.load(f)
        # convert the data to a dictionary and the nescassary data to a list
        width = len(max([data["response"][0]["league"]["standings"][0][x]["team"]["name"] for x in range(len(data["response"][0]["league"]["standings"][0]))], key=len))
        print(width)
        body = [[data["response"][0]["league"]["standings"][0][x]["rank"], data["response"][0]["league"]["standings"][0][x]["team"]["name"], data["response"][0]["league"]["standings"][0][x]["all"]["played"], data["response"][0]["league"]["standings"][0][x]["all"]["win"], data["response"][0]["league"]["standings"][0][x]["all"]["draw"], data["response"][0]["league"]["standings"][0][x]["all"]["lose"],data["response"][0]["league"]["standings"][0][x]["all"]["goals"]["for"],data["response"][0]["league"]["standings"][0][x]["all"]["goals"]["against"],data["response"][0]["league"]["standings"][0][x]["goalsDiff"],data["response"][0]["league"]["standings"][0][x]["points"]] for x in range(len(data["response"][0]["league"]["standings"][0]))]
        # create the table using table2ascii
        table = t2a(
            header=["Rank", "Team", "Played", "Wins", "Draws", "Losses", "GF", "GA", "GD", "Points"],
            body=body,
            first_col_heading=True,
            column_widths=[8, width+2, 8, 8, 8, 8, 8, 8, 8, 8],
            alignments=[Alignment.LEFT] + [Alignment.LEFT] + [Alignment.CENTER] * 8,
        )
        # send the table as a message

        #await inter.response.send_message(content=content)
        if img:
            img_size = (2500,1000)
            img_xy = tuple(size/2 for size in img_size)
            out = Image.new('RGB', img_size, (47, 49, 54))

            fnt = ImageFont.truetype('ANDALEMO.ttf', 40)
            d = ImageDraw.Draw(out)
            d.multiline_text(xy=img_xy, text=table, font=fnt, fill=(185, 187, 190), anchor="mm")
            # save image to file
            out.save("table.png")

            # create embed using the PIL image
            """embed = disnake.Embed(title=f"{data['response'][0]['league']['name']} Table", color=0x2F3136)
            embed.set_image(file=disnake.File("table.png"))"""
            await inter.response.send_message(file = disnake.File("table.png"))
        elif not img:
            # split the table into a list of strings
            table = table.splitlines()
            # split top 10 and bottom 10 into seperate lists and join them to strings
            top = """```{0}\n{1}```""".format("\n".join(table[:13]), table[-1])
            print(top)
            bottom = """```{0}\n{1}```""".format("\n".join(table[:3]),"\n".join(table[13:]))
            print(bottom)
            pages = [top, bottom]

            await inter.response.send_message(content=pages[0], view=ButtonMenu(pages=pages, timeout=60))

# allows the cog to be loaded
def setup(bot: commands.Bot):
    bot.add_cog(TableCommands(bot))

