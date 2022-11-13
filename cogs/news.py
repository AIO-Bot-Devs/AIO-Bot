import disnake
from disnake.ext import commands
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()
weather_token = os.getenv('WEATHER_API_KEY')
news_token = os.getenv('NEWS_API_KEY')

def setup(bot):
    bot.add_cog(newsCog(bot))


def getHeadlinesGnews():
    response = requests.get(f"https://gnews.io/api/v4/top-headlines?token={news_token}&lang=en")
    if response.status_code == 200:
        data = json.loads(response.text)
        articles = data['articles']
        return True, articles
    else:
        return False, response.status_code

def getHeadlinesBBC():
    # Not my code lmao: https://jonathansoma.com/lede/foundations-2017/classes/adv-scraping/scraping-bbc/
    response = requests.get('http://www.bbc.com/news')
    doc = BeautifulSoup(response.text, 'html.parser')
    # Start with an empty list
    stories_list = []
    stories = doc.find_all('div', { 'class': 'gs-c-promo' })
    for story in stories:
        # Create a dictionary without anything in it
        story_dict = {}
        headline = story.find('h3')
        link = story.find('a')
        summary = story.find('p')
        if headline and link and summary:
            story_dict['headline'] = headline.text
            story_dict['url'] = 'https://bbc.co.uk' + link['href']
            story_dict['summary'] = summary.text
            # Add the dict to our list
            stories_list.append(story_dict)
    return stories_list

def getCoords(city):
    response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={weather_token}")
    if response.status_code == 200:
        data = json.loads(response.text)
        if data == []:
            return False, 400
        else:
            lat = data[0]['lat']
            lon = data[0]['lon']
            city = data[0]['name']
            return True, lat, lon, city
    else:
        return False, response.status_code

def getWeather(lat, lon):
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={str(lat)}&lon={str(lon)}&units=metric&appid={weather_token}")
    if response.status_code == 200:
        data = json.loads(response.text)
        general = data['weather'][0]['main']
        temp = data['main']['temp']
        wind = data['wind']['speed']
        icon = data['weather'][0]['icon']
        return True, general, temp, wind, icon
    else:
        return False, response.status_code


class newsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def headlines(self, inter, source = commands.Param(choices=["BBC", "GNews API"])):
        """
        See the latest headlines

        Parameters
        ----------
        source: BBC News (UK) or Gnews API (international)
        """
        bot = self.bot
        if source == "BBC":
            headlines = getHeadlinesBBC()
            if headlines:
                newsEmbed = disnake.Embed(
                        title=f"Headlines",
                        description=f"Here are your news headlines, from BBC News!",
                        color=self.bot.colour_success)
                newsEmbed.add_field(name=headlines[0]['headline'], value=f"{headlines[0]['summary']} [[read more]]({headlines[0]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1]['headline'], value=f"{headlines[1]['summary']} [[read more]]({headlines[1]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[2]['headline'], value=f"{headlines[2]['summary']} [[read more]]({headlines[2]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[3]['headline'], value=f"{headlines[3]['summary']} [[read more]]({headlines[3]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[4]['headline'], value=f"{headlines[4]['summary']} [[read more]]({headlines[4]['url']})", inline=False)
                owner = await bot.fetch_user(self.bot.owner_id)
                newsEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                newsEmbed.set_thumbnail(url="https://evilpanda.me/files/news.png")
                await inter.response.send_message(embed=newsEmbed)
            else:
                errorEmbed = disnake.Embed(
                    title=f"News Content Error",
                    description=f"It appears there is no news? Please report this.",
                    color=self.bot.colour_error)
                owner = await bot.fetch_user(self.bot.owner_id)
                errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        else:
            headlines = getHeadlinesGnews()
            if headlines[0] == True:
                newsEmbed = disnake.Embed(
                        title=f"Headlines",
                        description=f"Here are your international headlines, from GNews API!",
                        color=self.bot.colour_success)
                newsEmbed.add_field(name=headlines[1][0]['title'], value=f"{headlines[1][0]['description']} [[read more]]({headlines[1][0]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1][1]['title'], value=f"{headlines[1][1]['description']} [[read more]]({headlines[1][1]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1][2]['title'], value=f"{headlines[1][2]['description']} [[read more]]({headlines[1][2]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1][3]['title'], value=f"{headlines[1][3]['description']} [[read more]]({headlines[1][3]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1][4]['title'], value=f"{headlines[1][4]['description']} [[read more]]({headlines[1][4]['url']})", inline=False)
                owner = await bot.fetch_user(self.bot.owner_id)
                newsEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                newsEmbed.set_thumbnail(url="https://evilpanda.me/files/news.png")
                await inter.response.send_message(embed=newsEmbed)
            else:
                errorEmbed = disnake.Embed(
                    title=f"GNews API Error",
                    description=f"An error occured while fetching news from GNews API, please report this. Error code: {headlines[1]}",
                    color=self.bot.colour_error)
                owner = await bot.fetch_user(self.bot.owner_id)
                errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
                await inter.response.send_message(embed=errorEmbed)


    @commands.slash_command()
    async def weather(self, inter, city):
        """
        Check the weather in a city

        Parameters
        ----------
        city: The city to check
        """
        bot = self.bot
        coords = getCoords(city)
        if coords[0] == True:
            weather = getWeather(coords[1], coords[2])
            if weather[0] == True:
                weatherEmbed = disnake.Embed(
                    title=f"Weather in {coords[3]}",
                    description=f"Is this data inaccurate? Feedback is always appreciated.",
                    color=self.bot.colour_success)
                weatherEmbed.add_field(name="Conditions", value=f"{weather[1]}")
                weatherEmbed.add_field(name="Temperature", value=f"{weather[2]} °C")
                weatherEmbed.add_field(name="Wind", value=f"{weather[3]} m/s")
                owner = await bot.fetch_user(self.bot.owner_id)
                weatherEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                weatherEmbed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{weather[4]}@2x.png")
                await inter.response.send_message(embed=weatherEmbed)
            else:
                errorEmbed = disnake.Embed(
                title=f"Weather API Error",
                description=f"Request failed, please report this. Error code {weather[1]}",
                color=self.bot.colour_error)
                owner = await bot.fetch_user(self.bot.owner_id)
                errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
                errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        else:
            errorEmbed = disnake.Embed(
                title=f"City Input Error",
                description=f"Could not find the city '{city}'. Please enter a valid city.",
                color=self.bot.colour_error)
            owner = await bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await inter.response.send_message(embed=errorEmbed)