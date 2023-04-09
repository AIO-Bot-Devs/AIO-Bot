import disnake
from disnake.ext import commands
import qrcode as qrmodule # I need to call the slash command qrcode, so this avoids confusion/errors
import json
import io

# allows the cog to be loaded
def setup(bot):
    bot.add_cog(qrcodesCog(bot))

# gets index from data.json, adds one, and returns it
def editIndex():
    with open('data.json', 'r') as f:
        data = json.load(f)
    data["qrcodes"]["index"] += 1
    with open('data.json', 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data["qrcodes"]["index"]

# function to generate the QR code with the data
def generateQr(data):
    """
    Generates a QR code from the data provided
    
    Parameters
    ----------
    data: The data to generate it with

    Returns
    -------
    file: The QR code image as a disnake file object
    """
    filename = f'qrcodes/qrcode.png'
    # creates the QR code object
    qr = qrmodule.QRCode(
        version=1,
        box_size=10,
        border=5)
    # adds the data to the QR code object
    qr.add_data(data)
    # makes the image
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    # saves the image to a 'file' (memory buffer)
    with io.BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)
        # returns a disnake file object so it can be used in an embed
        file = disnake.File(fp=image_binary, filename='qrcode.png')
    return file

# class for all the commands
class qrcodesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # default command
    @commands.slash_command()
    async def qrcode(self, inter):
        pass
    
    # command to generate a QR code from text
    @qrcode.sub_command()
    async def generate(self, inter, data):
        """
        Parameters
        ----------
        data: The data to generate it with
        """
        bot = self.bot
        # generates QR code and gets the file object
        image = generateQr(data)
        # creates an embed with the image and number of QR codes generated
        qrcodeEmbed = disnake.Embed(
            title=f"Generated QR Code",
            description=f"{editIndex()} total QR codes generated by {self.bot.user.mention}!",
            color=self.bot.colour_success)
        qrcodeEmbed.set_image(file=image)
        # adds the footer
        qrcodeEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
        await inter.response.send_message(embed=qrcodeEmbed)
        # except:
        #     errorEmbed = disnake.Embed(
        #     title=f"An Error Occurred",
        #     description=f"This is most likely due to the input data being too large. Try something smaller? (please?)",
        #     color=self.bot.colour_error)
        #     errorEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
        #     errorEmbed.set_thumbnail(url="https://api.evilpanda.live/static/error1.png")
        #     await inter.response.send_message(embed=errorEmbed)
