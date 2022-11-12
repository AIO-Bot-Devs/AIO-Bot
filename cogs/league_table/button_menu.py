from disnake.ui import View, button
from disnake import ui
import disnake
from typing import Optional

# copied from a tutorial so might want to find better alternative

class ButtonMenu(View):
    def __init__(self, pages:list, timeout:float, user:Optional[disnake.User]=None) -> None:
        super().__init__(timeout=timeout)
        self.current_page = 0
        self.pages = pages
        self.user = user
        self.length = len(self.pages)-1

    async def update(self, page:int):
        self.current_page = page
        if page == 0:
            self.children[0].disabled = True
            self.children[1].disabled = False
        elif page==self.length:
            self.children[0].disabled = False
            self.children[1].disabled = True
        else:
            self.children[0].disabled = False
            self.children[1].disabled = False

    async def getPage(self,page):
        if isinstance(page, str):
            return page,[],[]
        elif isinstance(page, disnake.Embed):
            return None,[page],[]
        elif isinstance(page, disnake.File):
            return None,[],[page]

    async def showPage(self, page:int, inter:disnake.Interaction):
        await self.update(page)
        content, embeds, files = await self.getPage(self.pages[page])
        await inter.response.edit_message(content=content, embeds=embeds, files=files, view=self)

    @ui.button(label="Up", style=disnake.ButtonStyle.blurple, custom_id="up")
    async def up(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        await self.showPage(self.current_page-1, interaction)
    @ui.button(label="Down",style=disnake.ButtonStyle.blurple, custom_id="down")
    async def down(self, button: disnake.ui.Button, inter: disnake.Interaction):
        await self.showPage(self.current_page+1, inter)

    @ui.button(label="Stop", style=disnake.ButtonStyle.red, custom_id="stop")
    async def stop(self, button: disnake.ui.Button, inter: disnake.Interaction):
        for i in self.children:
            i.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()

    async def interaction_check(self, inter: disnake.Interaction) -> bool:
        if self.user:
            if inter.user != self.user:
                await inter.response.send_message("You are not the one who started the menu", ephemeral=True)
                return False
        return True