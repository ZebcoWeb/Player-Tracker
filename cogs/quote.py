
import discord
import aiohttp
import random

from bs4 import BeautifulSoup
from html2text import html2text
from discord.ext import commands, tasks
from discord import Asset, app_commands
from discord.app_commands import Group

from data.config import Config, Channel, Assets, Emoji
from modules.utils import error_embed, success_embed
from modules.database.models import QuoteModel


class Quote(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.daily_quote_task.start()

    quote = Group(name="quote", description="💬 Quote commands", guild_ids=[Config.SERVER_ID])
    
    @quote.command(name='update', description='💬 Fetch & update quotes (admin only)')
    @app_commands.checks.has_permissions(administrator=True)
    async def quote_fetch(self, interaction: discord.Interaction):

        BASE_URL = 'https://game-quotes.com/en'

        em = discord.Embed(
            title='Fetching quotes...', 
            description='Please wait...',
            color=discord.Colour.yellow()
        )
        await interaction.response.send_message(embed=em)
        
        await QuoteModel.delete_all()
        page_number = 1
        quote_number = 1
        while True:
            try:
                async with aiohttp.ClientSession(loop=self.client.loop) as session:
                    async with session.get(BASE_URL + f'?page={page_number}') as resp:
                        body = await resp.read()
                        soup = BeautifulSoup(body.decode('utf-8'), 'html5lib')
                        quote_list_html = soup.find_all('div', attrs={'itemtype': 'http://schema.org/Quotation'})
                        if quote_list_html:
                            quote_model_objects = []
                            for quote_html in quote_list_html:
                                character_name = quote_html.find('div', attrs={'itemtype': 'http://schema.org/Person'}).find('span').text
                                quote_content = quote_html.find('div', {"class": "quote-content"}).find('p')
                                if quote_content:
                                    quote = html2text(quote_content.prettify())
                                    quote = quote[:-2]
                                else:
                                    continue
                                game = quote_html.find('div', attrs={'itemtype': 'http://schema.org/VideoGame'}).find('span').text
                                quote_model_objects.append(
                                    QuoteModel(
                                        character=character_name,
                                        quote=quote,
                                        game=game,
                                    )
                                )
                                quote_number += 1
                            await QuoteModel.insert_many(quote_model_objects)
                            em.description = f'**{str(quote_number)}** quote loaded...'
                            await interaction.edit_original_message(embed=em)
                            page_number += 1
                        else:
                            break
            except Exception as e:
                print(e)
                break
        em.description = f'**{str(quote_number)}** quote loaded, Done ✅'
        em.color = discord.Colour.green()
        await interaction.edit_original_message(embed=em)
        self.daily_quote_task.restart()
    

    @quote.command(name='restart', description='💬 Restart quote task (admin only)')
    @app_commands.checks.has_permissions(administrator=True)
    async def quote_task(self, interaction: discord.Interaction):
        self.daily_quote_task.restart()
        await interaction.response.send_message(embed=success_embed('Quote task restarted'), ephemeral=True)


    @tasks.loop(hours=24)
    async def daily_quote_task(self):
        quote_channel = await self.client.fetch_channel(Channel.QUOTE)
        async for message in quote_channel.history():
            await message.delete()
        quotes = await QuoteModel.find(QuoteModel.is_active == True, sort='+display_count', limit=1).to_list()
        if quotes:
            quote = quotes[0]
            embed_color = Config.COLOR_DISCORD

            description = ''
            description += f'{Emoji.RS + Emoji.Q1 + Emoji.LS + (Emoji.L * 13)}\n'
            description += f'*{quote.quote}*\n'
            description += f'{(Emoji.L * 13) + Emoji.RS + Emoji.Q2 + Emoji.LS}\n\nㅤㅤ{Emoji.CIRCLE} From **{quote.game}** game\n'

            quote_embed = discord.Embed(
                title=f'💬  {quote.character}',
                description=description,
                color=embed_color,
            )
            banner_embed = discord.Embed(color=embed_color, type='image')
            banner_embed.set_image(url=Assets.QUOTE_BANNER)

            quote_message = await quote_channel.send(embeds=[banner_embed, quote_embed])
            await quote_message.add_reaction('\U0001f5ff')
            quote.display_count += 1
            await quote.save()


async def setup(client:commands.Bot):
    await client.add_cog(Quote(client))