
# Noah Bot

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

- Repository for my WIP all-purpose Discord bot.
- If you believe my code could be made more efficient, feel free to open a pull request.
- Please note that some features are currently WIP and may not work correctly.

## Environment Variables

- First of all, make sure you have the latest version of Python installed. 
- Next install the following modules which are required for all aspects of the bot to function.

For bot:
```bash
  pip3 install disnake
  pip3 install python-dotenv
```
For specific functions:
```bash
  pip3 install pil
  pip3 install table2ascii
```
- Download the files from GitHub and unzip them
- Setup your .env file as shown below:
```env
DISCORD_TOKEN=[your discord token]
FOOTBALL_TOKEN=[your football api token]
```
- Lastly, Navigate to the folder and run using python 3 (you can use nohup to run it in the background).
```bash
  cd [route to discord bot]
  python3 main.py
  (or) nohup python3 main.py &
```

## Author

- [@noah-dyson](https://www.github.com/noah-dyson) (aurora.#7523)

## Support

There is no active support for this discord bot. However you can contact me on Discord: aurora.#7523.

## License

[MIT](https://choosealicense.com/licenses/mit/)
