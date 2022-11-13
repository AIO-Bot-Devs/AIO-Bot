import disnake
from disnake.ext import commands
import asyncio
import requests

@commands.slash_command()
async def spotify(self, inter):
    pass

    @spotify.sub_command()
    async def nowplaying(self, inter):
        """
        Get the currently playing song on Spotify
        """
        await inter.response.send_modal(
            title="Spotify",
            custom_id = "spotify_modal",
            components=[
                disnake.ui.TextInput(
                    label = "Code",
                    placeholder="Go to https://evilpanda.me/spotify/",
                    custom_id="spotify_code",
                    style=disnake.TextInputStyle.short
                )
            ]
        )
        try:
            modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                "modal_submit",
                check=lambda i: i.custom_id == "spotify_modal" and i.author.id == inter.author.id,
                timeout=600,
            )
        except asyncio.TimeoutError:
            return
        
        code = modal_inter.text_values["spotify_code"]
        request = {
            "grant_type":    "authorization_code",
            "code":          code,
            "redirect_uri":  "https://evilpanda.me/botpanda/spotify/",
            "client_secret": "024cb76a16ab4903ad940f75059c5fdb",
            "client_id":     "d7bdc1d9fe15411991b32d96336ebd4f",
        }
        tokenResponse = requests.post("https://accounts.spotify.com/api/token", data=request)
        if tokenResponse.status_code != 200:
            errorEmbed = disnake.Embed(
                title="An error occured",
                description=f"Make sure you input the correct code, and nothing else. Error {tokenResponse.status_code}: {tokenResponse.reason}",
                color=self.bot.colour_error)
            owner = await self.bot.fetch_user(self.bot.owner_id)
            errorEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            errorEmbed.set_thumbnail(url="https://evilpanda.me/files/error1.png")
            await modal_inter.send(embed=errorEmbed)
        else:
            token = tokenResponse.json()["access_token"]
            playing = requests.get("https://api.spotify.com/v1/me/player", headers={'Authorization': f"Bearer {token}", 'Content-Type': 'application/json'}).json()
            track_id = playing['item']['id']
            track = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers={'Authorization': f"Bearer {token}", 'Content-Type': 'application/json'}).json()
            artist = listToString(track['artists'])
            progress = playing['progress_ms'] / 1000
            progressSeconds = round(progress % 60) if progress % 60 > 10 else "0" + str(round(progress % 60))
            duration = track['duration_ms'] / 1000
            durationSeconds = round(duration % 60) if duration % 60 > 10 else "0" + str(round(duration % 60))
            percentage = progress / duration * 100
            bar = progressBar(percentage)
            playingEmbed = disnake.Embed(
                title=f"{track['name']} by {artist}",
                description=f"{int(progress/60)}:{progressSeconds} / {int(duration/60)}:{durationSeconds}\n{bar}",
                color=self.bot.colour_success,
                url=f"https://open.spotify.com/track/{track_id}"
            )
            playingEmbed.set_thumbnail(url=track['album']['images'][0]['url'])
            playingEmbed.add_field(name="Album", value=track['album']['name'])
            owner = await self.bot.fetch_user(self.bot.owner_id)
            playingEmbed.set_footer(text="Panda Bot • EvilPanda#7288", icon_url=owner.avatar)
            await modal_inter.send(embed=playingEmbed)
