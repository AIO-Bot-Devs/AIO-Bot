import disnake
from disnake.ext import commands
import aiohttp
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import asyncio

# loads tokens from .env file
load_dotenv()
weather_token = os.getenv('WEATHER_API_KEY')
news_token = os.getenv('NEWS_API_KEY')

#allows the cog to be loaded
def setup(bot):
    bot.add_cog(newsCog(bot))

# grabs the news from gnews
async def getHeadlinesGnews():
    async with aiohttp.request('GET', f"https://gnews.io/api/v4/top-headlines?token={news_token}&lang=en") as response:
        if response.status == 200:
            data = await response.json()
            articles = data['articles']
            return True, articles
        else:
            return False, response.status

# this just works 
async def getHeadlinesBBC():
    # Not my code lmao: https://jonathansoma.com/lede/foundations-2017/classes/adv-scraping/scraping-bbc/
    async with aiohttp.request('GET', f"http://www.bbc.com/news") as response:
        doc = BeautifulSoup(await response.text(), 'html.parser')
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

# gets the coordinates of the location
async def getCoords(city):
    # sends a request to the weather api
    async with aiohttp.request('GET', f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={weather_token}") as response:
        # if the request is successful, it returns the coordinates of the city, otherwise it returns the error code
        if response.status == 200:
            data = await response.json()
            if data == []:
                return False, 400
            else:
                lat = data[0]['lat']
                lon = data[0]['lon']
                city = data[0]['name']
                return True, lat, lon, city
        else:
            return False, response.status

# gets the weather data based on the coordinates
async def getWeather(lat, lon):
    # sends a request to the weather api with the coordinates
    async with aiohttp.request('GET', f"https://api.openweathermap.org/data/2.5/weather?lat={str(lat)}&lon={str(lon)}&units=metric&appid={weather_token}") as response:
        # if the request is successful, it returns the weather data, otherwise it returns the error code
        if response.status == 200:
            data = await response.text()
            general = data['weather'][0]['main']
            temp = data['main']['temp']
            wind = data['wind']['speed']
            icon = data['weather'][0]['icon']
            return True, general, temp, wind, icon
        else:
            return False, response.status

# class for all the commands
class newsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # this command gets the news
    @commands.slash_command()
    async def headlines(self, inter, source = commands.Param(choices=["BBC", "GNews API"])):
        """
        Parameters
        ----------
        source: BBC News (UK) or Gnews API (international)
        """
        bot = self.bot
        # if the source is BBC, it gets the news from BBC, otherwise it gets the news from Gnews
        if source == "BBC":
            # calls the function to get the news
            headlines = await getHeadlinesBBC()
            # if the news is empty, it sends an error message, otherwise it sends the news
            if headlines:
                # creates an embed with the top 5 headlines
                newsEmbed = disnake.Embed(
                        title=f"Headlines",
                        description=f"Here are your news headlines, from BBC News!",
                        color=self.bot.colour_success)
                newsEmbed.add_field(name=headlines[0]['headline'], value=f"{headlines[0]['summary']} [[read more]]({headlines[0]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1]['headline'], value=f"{headlines[1]['summary']} [[read more]]({headlines[1]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[2]['headline'], value=f"{headlines[2]['summary']} [[read more]]({headlines[2]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[3]['headline'], value=f"{headlines[3]['summary']} [[read more]]({headlines[3]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[4]['headline'], value=f"{headlines[4]['summary']} [[read more]]({headlines[4]['url']})", inline=False)
                # adds a footer
                newsEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
                newsEmbed.set_thumbnail(url="https://api.evilpanda.live/static/news.png")
                await inter.response.send_message(embed=newsEmbed)
            # if the news is empty, it sends an error message
            else:
                errorEmbed = disnake.Embed(
                    title=f"News Content Error",
                    description=f"It appears there is no news? Please report this.",
                    color=self.bot.colour_error)
                # adds a footer
                errorEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
                errorEmbed.set_thumbnail(url="https://api.evilpanda.live/static/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        # if the source is Gnews API, it gets the news from Gnews API
        else:
            # calls the function to get the news
            headlines = await getHeadlinesGnews()
            # if the news is empty, it sends an error message, otherwise it sends the news
            if headlines[0] == True:
                # creates an embed with the top 5 headlines
                newsEmbed = disnake.Embed(
                        title=f"Headlines",
                        description=f"Here are your international headlines, from GNews API!",
                        color=self.bot.colour_success)
                newsEmbed.add_field(name=headlines[1][0]['title'], value=f"{headlines[1][0]['description']} [[read more]]({headlines[1][0]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1][1]['title'], value=f"{headlines[1][1]['description']} [[read more]]({headlines[1][1]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1][2]['title'], value=f"{headlines[1][2]['description']} [[read more]]({headlines[1][2]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1][3]['title'], value=f"{headlines[1][3]['description']} [[read more]]({headlines[1][3]['url']})", inline=False)
                newsEmbed.add_field(name=headlines[1][4]['title'], value=f"{headlines[1][4]['description']} [[read more]]({headlines[1][4]['url']})", inline=False)
                # adds a footer
                newsEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
                newsEmbed.set_thumbnail(url="https://api.evilpanda.live/static/news.png")
                await inter.response.send_message(embed=newsEmbed)
            # if the news is empty, it sends an error message
            else:
                errorEmbed = disnake.Embed(
                    title=f"GNews API Error",
                    description=f"An error occured while fetching news from GNews API, please report this. Error code: {headlines[1]}",
                    color=self.bot.colour_error)
                # adds a footer
                errorEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
                errorEmbed.set_thumbnail(url="https://api.evilpanda.live/static/error1.png")
                await inter.response.send_message(embed=errorEmbed)

    # command to get the weather
    @commands.slash_command()
    async def weather(self, inter, city):
        """
        Parameters
        ----------
        city: The city to check
        """
        bot = self.bot
        # calls the function to get the coordinates of the city
        coords = asyncio.run(getCoords(city))
        # if the coordinates are empty, it sends an error message, otherwise it runs the weather function
        if coords[0] == True:
            # calls the function to get the weather
            weather = asyncio.run(getWeather(coords[1], coords[2]))
            # if the weather is empty, it sends an error message, otherwise it sends the weather
            if weather[0] == True:
                # creates an embed with the weather
                weatherEmbed = disnake.Embed(
                    title=f"Weather in {coords[3]}",
                    description=f"Is this data inaccurate? Feedback is always appreciated.",
                    color=self.bot.colour_success)
                weatherEmbed.add_field(name="Conditions", value=f"{weather[1]}")
                weatherEmbed.add_field(name="Temperature", value=f"{weather[2]} °C")
                weatherEmbed.add_field(name="Wind", value=f"{weather[3]} m/s")
                # adds a footer
                weatherEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
                weatherEmbed.set_thumbnail(url=f"https://openweathermap.org/img/wn/{weather[4]}@2x.png")
                await inter.response.send_message(embed=weatherEmbed)
            # if the weather is empty, it sends an error message
            else:
                # creates an embed with the error message
                errorEmbed = disnake.Embed(
                title=f"Weather API Error",
                description=f"Request failed, please report this. Error code {weather[1]}",
                color=self.bot.colour_error)
                # adds a footer
                errorEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
                errorEmbed.set_thumbnail(url="https://api.evilpanda.live/static/error1.png")
                await inter.response.send_message(embed=errorEmbed)
        # if the coordinates are empty, it sends an error message
        else:
            # creates an embed with the error message
            errorEmbed = disnake.Embed(
                title=f"City Input Error",
                description=f"Could not find the city '{city}'. Please enter a valid city.",
                color=self.bot.colour_error)
            # adds a footer
            errorEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
            errorEmbed.set_thumbnail(url="https://api.evilpanda.live/static/error1.png")
            await inter.response.send_message(embed=errorEmbed)