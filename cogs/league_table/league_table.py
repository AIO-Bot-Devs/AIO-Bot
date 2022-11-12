import os
from dotenv import load_dotenv
import disnake
from disnake.ext import commands
import aiohttp
import datetime
from table2ascii import table2ascii as t2a, Alignment
from PIL import Image, ImageDraw, ImageFont
import json
from .button_menu import ButtonMenu

# getting bot token from token.env
load_dotenv()
token = os.getenv("FOOTBALL_TOKEN")

# class for all the commands
class TableCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # this command will retrieve the league table from the football-data.org api
    @commands.slash_command(name="table", description="Get the league table for a specific league")
    async def table(self, inter, league_id: int, img: bool = False):

        async def table_gen(data):
            # base_json is used to reduce the length of the code
            base_json = data["response"][0]["league"]["standings"][0]
            # width grabs the max length of a team name
            width = len(max([base_json[x]["team"]["name"] for x in range(len(base_json))], key=len))
            body = [[base_json[x]["rank"], 
                    base_json[x]["team"]["name"], 
                    base_json[x]["all"]["played"], 
                    base_json[x]["all"]["win"],
                    base_json[x]["all"]["draw"], 
                    base_json[x]["all"]["lose"],
                    base_json[x]["all"]["goals"]["for"],
                    base_json[x]["all"]["goals"]["against"],
                    base_json[x]["goalsDiff"],
                    base_json[x]["points"]] for x in range(len(base_json))]
            # create the table using table2ascii
            table = t2a(
                header=["Rank", "Team", "Played", "Wins", "Draws", "Losses", "GF", "GA", "GD", "Points"],
                body=body,
                first_col_heading=True,
                column_widths=[8, width+2, 8, 8, 8, 8, 8, 8, 8, 8],
                alignments=[Alignment.LEFT] + [Alignment.LEFT] + [Alignment.CENTER] * 8,
            )
            return table, data['response'][0]['league']['name']

        async def image_gen(table):
            # create a new image 
            img_size = (2500,1000)
            # img_xy is the centre of the image used to anchor the text
            img_xy = tuple(size/2 for size in img_size)
            # 47, 49, 95 is the discord background colour
            out = Image.new('RGB', img_size, (47, 49, 54))
            # set font to a variable
            fnt = ImageFont.truetype('ANDALEMO.ttf', 40)
            # draw the text onto the image, fill is the colour of the text
            d = ImageDraw.Draw(out)
            d.multiline_text(xy=img_xy, text=table, font=fnt, fill=(185, 187, 190), anchor="mm")
            # save image to file
            file_name = "table.png"
            out.save(file_name)
            return file_name

        async def table_format(table):
            # split the table into a list of strings
            table = table.splitlines()
            # split top 10 and the rest of the entries into seperate lists and join them to strings
            top = """```{0}\n{1}```""".format("\n".join(table[:13]), table[-1])
            bottom = """```{0}\n{1}```""".format("\n".join(table[:3]),"\n".join(table[13:]))
            # pages is used to in the button menu
            pages = [top, bottom]
            return pages
        
        async def make_request(abs_file_path):
            # data required to make the request
            url = f"https://v3.football.api-sports.io/standings?league={league_id}&season=2022"
            payload={}
            headers = {
                'x-rapidapi-key': token,
                'x-rapidapi-host': 'v3.football.api-sports.io'
            }
            # sends request to the api using aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, data=payload) as response:
                    # if the request is successful, then get the json file
                    if response.status == 200:
                        # convert json file to a python dictionary and add the time of the request to the dictionary
                        data = await response.json()
                        data["time"] = str(datetime.datetime.now())
                        with open(abs_file_path, "w") as f:
                            json.dump(data, f)
            # read the data from the file
            with open(abs_file_path, "r") as f:
                return json.load(f)


        # getting the league table json file
        script_dir = os.path.dirname(__file__)
        rel_path = f"leagues/{league_id}.json"
        abs_file_path = os.path.join(script_dir, rel_path)

        # if there is text in league_id.json, then use that, otherwise, send a request to the api
        if os.path.exists(abs_file_path):
            with open(abs_file_path, "r") as f:
                data = json.load(f)
            # if the data is older than 1 day, then send a new request
            if datetime.datetime.now() - datetime.datetime.strptime(data["time"], "%Y-%m-%d %H:%M:%S.%f") > datetime.timedelta(days=1):
                data = await make_request(abs_file_path)
        else:                
            data = await make_request(abs_file_path)

        # generating the table using table2ascii
        table, table_name = await table_gen(data)
        # if img is true, then generate an image of the table otherwise, send the table as a formatted string
        if img:
            file_name = await image_gen(table)
            embed = disnake.Embed(title=f"{table_name} Table", color=0x2F3136)
            embed.set_image(file=disnake.File(file_name))
            await inter.response.send_message(embed=embed)
        elif not img:
            pages = await table_format(table)
            await inter.response.send_message(content=pages[0], view=ButtonMenu(pages=pages, timeout=60))

# allows the cog to be loaded
def setup(bot: commands.Bot):
    bot.add_cog(TableCommands(bot))

