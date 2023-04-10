import disnake
from disnake.ext import commands
import aiohttp
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import asyncio
import datetime

# loads tokens from .env file
load_dotenv()
weather_token = os.getenv('WEATHER_API_KEY')
news_token = os.getenv('NEWS_API_KEY')

#allows the cog to be loaded
def setup(bot):
    bot.add_cog(newsCog(bot))

# formats dates from rss feed to discord timestamps
async def formatDate(dateInput):
    datetimeObject = datetime.datetime.strptime(dateInput, "%a, %d %b %Y %H:%M:%S GMT")
    timestamp = int(datetimeObject.timestamp())
    return f"<t:{timestamp}:R>"


# gets the news using bbc rss feed and beautiful soup parsing
async def getHeadlinesBBCRSS():
    # try except statement to catch any errors
    try:
        async with aiohttp.request('GET', f"http://feeds.bbci.co.uk/news/rss.xml") as response:
            bs = BeautifulSoup(await response.text(), 'xml')
        # find all stories in feed
        stories = bs.find_all('item')
        stories_list = []
        # add a dictionary for each story to a list
        for story in stories:
            story_dict = {}
            story_dict['headline'] = story.find('title').text
            story_dict['summary'] = story.find('description').text
            story_dict['url'] = story.find('guid').text
            story_dict['date'] = story.find('pubDate').text
            stories_list.append(story_dict)
        return stories_list
    except:
        return False


# gets the coordinates of the location, in order to use them for the weather api
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

# gets the weather data based on the coordinates of the city (limitation of api - no city name search)
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
    async def headlines(self, inter):
        """
        Gets the headlines from BBC News
        """
        bot = self.bot
        # calls the function to get the news
        headlines = await getHeadlinesBBCRSS()
        # if the news is empty, it sends an error message, otherwise it sends the news
        if headlines:
            # creates an embed with the top 5 headlines
            newsEmbed = disnake.Embed(
                    title=f"Headlines",
                    description=f"Here are your news headlines, from BBC News!",
                    color=self.bot.colour_success)
            # add a field for each story
            newsEmbed.add_field(name=f"{bot.emoji_bullet_point} {headlines[0]['headline']}", value=f"{await formatDate(headlines[0]['date'])}\n{headlines[0]['summary']}\n[[read more]]({headlines[0]['url']})", inline=False)
            newsEmbed.add_field(name=f"{bot.emoji_bullet_point} {headlines[1]['headline']}", value=f"{await formatDate(headlines[1]['date'])}\n{headlines[1]['summary']}\n[[read more]]({headlines[1]['url']})", inline=False)
            newsEmbed.add_field(name=f"{bot.emoji_bullet_point} {headlines[2]['headline']}", value=f"{await formatDate(headlines[2]['date'])}\n{headlines[2]['summary']}\n[[read more]]({headlines[2]['url']})", inline=False)
            newsEmbed.add_field(name=f"{bot.emoji_bullet_point} {headlines[3]['headline']}", value=f"{await formatDate(headlines[3]['date'])}\n{headlines[3]['summary']}\n[[read more]]({headlines[3]['url']})", inline=False)
            newsEmbed.add_field(name=f"{bot.emoji_bullet_point} {headlines[4]['headline']}", value=f"{await formatDate(headlines[4]['date'])}\n{headlines[4]['summary']}\n[[read more]]({headlines[4]['url']})", inline=False)
            # adds a footer
            newsEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
            newsEmbed.set_thumbnail(url="https://api.evilpanda.live/static/news.png")
            await inter.response.send_message(embed=newsEmbed)
        # if an error occured while getting the news, it sends an error message
        else:
            errorEmbed = disnake.Embed(
                title=f"News Content Error",
                description=f"It appears there is no news? Please report this.",
                color=self.bot.colour_error)
            # adds a footer
            errorEmbed.set_footer(text=self.bot.footer, icon_url=self.bot.user.avatar)
            errorEmbed.set_thumbnail(url="https://api.evilpanda.live/static/error1.png")
            await inter.response.send_message(embed=errorEmbed)

    # command to get the weather
    @commands.slash_command()
    async def weather(self, inter, city):
        """
        Gets the weather in a specified city
        
        Parameters
        ----------
        city: The city to check
        """
        bot = self.bot
        # calls the function to get the coordinates of the city
        coords = asyncio.run(getCoords(city))
        # if the coordinates are empty, it sends an error message, otherwise it runs the weather function
        if coords[0]:
            # calls the function to get the weather
            weather = asyncio.run(getWeather(coords[1], coords[2]))
            # if the weather is empty, it sends an error message, otherwise it sends the weather
            if weather[0]:
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