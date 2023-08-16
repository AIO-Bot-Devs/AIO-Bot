
# All in One Bot

<p align="center">
  <a href="https://choosealicense.com/licenses/mit/" target="_blank">
    <img alt="license" src="https://img.shields.io/github/license/veryevilpanda/Panda-Bot"/>
  </a>
  <a href="https://www.python.org/" target="_blank">
    <img alt="top language" src="https://img.shields.io/github/languages/top/veryevilpanda/Panda-Bot"/>
  </a>
  <a href="https://discord.gg/Zu6pDEBCjY" target="_blank">
    <img alt="discord" src="https://img.shields.io/discord/1002963156273999884?label=discord"/>
  </a>
</p>

- Repository for this WIP all-purpose Discord bot.
- If you believe the code could be made more efficient, feel free to open a pull request.
- Please note that some features are currently WIP and may not work correctly.
- THE README IS CURRENTLY OUDATED SO SETUP WILL LIKELY NOT WORK.

## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

- `DISCORD_TOKEN` - Your discord bot token, obtained from [Discord Developer Portal](https://discord.com/developers/applications)
- `WEATHER_API_KEY` - Your weather API key, obtained from [openweathermap.org](https://openweathermap.org/)
- `NEWS_API_KEY` - Your news API key, obtained from [gnews.io](https://gnews.io/)
- `FOOTBALL_TOKEN` - Your football token, obtained from (idk ask Noah)

## Installation

- First of all, make sure you have the latest version of Python installed. 
- Next install the following modules which are required for all aspects of the bot to function.

For bot:
```bash
  pip3 install disnake
  pip3 install python-dotenv
```
For specific functions:
```bash
  pip3 install pillow
  pip3 install table2ascii
  pip3 install beautifulsoup4 
  pip3 install qrcode
  pip3 install googletrans
  pip3 install requests
```
- Download the files from GitHub and unzip them
- Setup your .env file as shown below:
```env
DISCORD_TOKEN=[your discord token]
FOOTBALL_TOKEN=[your football api token]
WEATHER_API_KEY=[your weather api key]
NEWS_API_KEY=[your news api key]
```
- Lastly, Navigate to the folder and run using python 3 (you can use nohup to run it in the background).
```bash
  cd [route to discord bot]
  python3 main.py
  (or) nohup python3 main.py &
```

## Authors


- [@noah-dyson](https://www.github.com/noah-dyson) (aurora.#7523)
- [@veryevilpanda](https://www.github.com/VeryEvilPanda) (EvilPanda#7288)

## Support

There is no guaranteed active support for this discord bot. However, join [the discord](https://discord.gg/Zu6pDEBCjY) and ask any questions!

## License

[MIT](https://choosealicense.com/licenses/mit/)
