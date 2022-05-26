import discord

from data.config import Emoji


class Paginator(discord.ui.View):
    """
    Embed Paginator.

    Parameters:
    ----------
    timeout: int
        How long the Paginator should timeout in, after the last interaction. (In seconds) (Overrides default of 60)
    PreviousButton: discord.ui.Button
        Overrides default previous button.
    NextButton: discord.ui.Button
        Overrides default next button.
    PageCounterStyle: discord.ButtonStyle
        Overrides default page counter style.
    InitialPage: int
        Page to start the pagination on.
    """

    def __init__(self, *,
        timeout: int = 60,
        client: discord.Client,
        InitialPage: int = 0
    ) -> None:
        self.client = client
        self.PreviousButton = discord.ui.Button(emoji=discord.PartialEmoji.from_str(Emoji.ARROW_BACK), style=discord.ButtonStyle.green)
        self.NextButton = discord.ui.Button(emoji=discord.PartialEmoji.from_str(Emoji.ARROW_FORWARD), style=discord.ButtonStyle.green)
        self.PageCounterStyle = discord.ButtonStyle.blurple
        self.InitialPage = InitialPage

        self.pages = None
        self.ctx = None
        self.message = None
        self.current_page = None
        self.page_counter = None
        self.total_page_count = None

        super().__init__(timeout=timeout)

    async def start(self, interaction: discord.Interaction, pages: list[discord.Embed]):
        self.pages = pages
        self.total_page_count = len(pages)
        
        if self.total_page_count == 1:
            await interaction.response.send_message(embed=self.pages[0])
        else:
            self.interaction = interaction
            self.current_page = self.InitialPage
            self.creator = interaction.user

            self.PreviousButton.callback = self.previous_button_callback
            self.NextButton.callback = self.next_button_callback

            self.page_counter = SimplePaginatorPageCounter(style=self.PageCounterStyle,
                                                        client=self.client,
                                                        TotalPages=self.total_page_count,
                                                        InitialPage=self.InitialPage)

            self.add_item(self.PreviousButton)
            self.add_item(self.page_counter)
            self.add_item(self.NextButton)

            await interaction.response.send_message(embed=self.pages[self.InitialPage], view=self)

    async def previous(self):
        if self.current_page == 0:
            self.current_page = self.total_page_count - 1
        else:
            self.current_page -= 1

        self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
        await self.interaction.edit_original_message(embed=self.pages[self.current_page], view=self)

    async def next(self):
        if self.current_page == self.total_page_count - 1:
            self.current_page = 0
        else:
            self.current_page += 1

        self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
        await self.interaction.edit_original_message(embed=self.pages[self.current_page], view=self)

    async def next_button_callback(self, interaction: discord.Interaction):
        if self.creator == interaction.user:
            await self.next()
        await interaction.response.defer()

    async def previous_button_callback(self, interaction: discord.Interaction):
        if self.creator == interaction.user:
            await self.previous()
        await interaction.response.defer()


class SimplePaginatorPageCounter(discord.ui.Button):
    def __init__(self, style: discord.ButtonStyle, client: discord.Client, TotalPages, InitialPage):
        super().__init__(label=f"{InitialPage + 1}/{TotalPages}", style=style, emoji=discord.PartialEmoji.from_str(Emoji.CURSOR))
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()