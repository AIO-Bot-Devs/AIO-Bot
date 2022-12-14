import disnake
from disnake.ext import commands
import googletrans
from googletrans import Translator

# allows the cog to be loaded
def setup(bot):
    bot.add_cog(translateCog(bot))

# function to get the language from the code
def getLanguage(code):
    language = googletrans.LANGUAGES[code]
    return language

# function to get the code from the language
def getCode(lang):
    for i in googletrans.LANGUAGES:
        if googletrans.LANGUAGES[i] == lang:
            code = googletrans.LANGUAGES[i]
    return code

# constant list of all available languages
LANGUAGES = ['afrikaans', 'albanian', 'amharic', 'arabic', 'armenian', 'azerbaijani', 'basque', 'belarusian', 'bengali', 'bosnian', 'bulgarian', 'catalan', 'cebuano', 'chichewa', 'chinese (simplified)', 'chinese (traditional)', 'corsican', 'croatian', 'czech', 'danish', 'dutch', 'english', 'esperanto', 'estonian', 'filipino', 'finnish', 'french', 'frisian', 'galician', 'georgian', 'german', 'greek', 'gujarati', 'haitian creole', 'hausa', 'hawaiian', 'hebrew', 'hebrew', 'hindi', 'hmong', 'hungarian', 'icelandic', 'igbo', 'indonesian', 'irish', 'italian', 'japanese', 'javanese', 'kannada', 'kazakh', 'khmer', 'korean', 'kurdish (kurmanji)', 'kyrgyz', 'lao', 'latin', 'latvian', 'lithuanian', 'luxembourgish', 'macedonian', 'malagasy', 'malay', 'malayalam', 'maltese', 'maori', 'marathi', 'mongolian', 'myanmar (burmese)', 'nepali', 'norwegian', 'odia', 'pashto', 'persian', 'polish', 'portuguese', 'punjabi', 'romanian', 'russian', 'samoan', 'scots gaelic', 'serbian', 'sesotho', 'shona', 'sindhi', 'sinhala', 'slovak', 'slovenian', 'somali', 'spanish', 'sundanese', 'swahili', 'swedish', 'tajik', 'tamil', 'telugu', 'thai', 'turkish', 'ukrainian', 'urdu', 'uyghur', 'uzbek', 'vietnamese', 'welsh', 'xhosa', 'yiddish', 'yoruba', 'zulu']

# class for all the translate commands
class translateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    # command to translate a message
    @commands.slash_command()
    async def translate(self, inter, text, destination, source=None):
        """
        Parameters
        ----------
        text: The text to be translated
        destination: The destination language
        source: The source language (optional)
        """
        bot = self.bot
        await inter.response.send_message(f"{bot.emoji_loading} This command is currently in progress.")
        # TRY TO FIX AT SOME POINT LOL
        # code = getCode(destination)
        # translator = Translator()
        # if source != None:
        #     result = translator.translate(text, dest=code, src=source)
        # else:
        #     result = translator.translate(text, dest=code)
        # translateEmbed = disnake.Embed(
        #     title=f"Translation into {destination.capitalize()}",
        #     description=result.text,
        #     colour=self.bot.colour_success)
        # owner = await self.bot.fetch_user(self.bot.owner_id)
        # translateEmbed.set_footer(text=bot.footer, icon_url=owner.avatar)
        # await inter.response.send_message(embed=translateEmbed)

    
