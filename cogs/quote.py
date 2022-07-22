
import discord
import tweepy

from tweepy.asynchronous import AsyncStreamingClient, AsyncClient
from discord.ext import commands, tasks
from beanie.odm.operators.update.general import Inc
from discord import app_commands
from discord.app_commands import Group

from data.config import Config, Channel, Assets, Emoji
from modules.config import Env
from modules.utils import success_embed, split_tweet
from modules.models import QuoteModel


class QuoteFeed(AsyncStreamingClient):
    def __init__(self, *args, **kwargs):
        super().__init__(
            bearer_token=Env.TWITTER_BEARER_TOKEN,
            wait_on_rate_limit=True,
            max_retries=3
        )
    async def on_connect(self):
        print('> Twitter Streaming API connected.')

    async def on_tweet(self, tweet):
        quote_text, quote_game, quote_character = split_tweet(tweet)
        if quote_text:
            if len(quote_text) >= 40:
                if await QuoteModel.count() > 1000:
                    quotes = await QuoteModel.find(sort='-display_count', limit=1).to_list()
                    await quotes[0].delete()
                quote = QuoteModel(
                    character=quote_character,
                    quote=quote_text,
                    game=quote_game,
                )
                print(quote)
                await quote.save()

class Quote(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

        self.twitter_client = AsyncClient(Env.TWITTER_BEARER_TOKEN)
        
        self.client.loop.create_task(self._initialize_quotes())
        self.client.loop.create_task(self._inizialize_twitter_stream())

    quote = Group(name="quote-mod", description="🗿 Quote moderator commands (admin only)", guild_ids=[Config.SERVER_ID])

    async def _inizialize_twitter_stream(self):
        feed_tweet_client = QuoteFeed()
        await feed_tweet_client.add_rules(
            add=tweepy.StreamRule(f'from:{Config.TWITTER_QUOTES_FEED_USERNAME}')
        )
        await feed_tweet_client.filter()
    
    async def _initialize_quotes(self):
        if await QuoteModel.count() == 0:
            user_result = await self.twitter_client.get_user(username=Config.TWITTER_QUOTES_FEED_USERNAME)
            user_id = user_result.data.id
            results = await self.twitter_client.get_users_tweets(user_id, max_results=20)
            for tweet in results.data:
                quote_text, quote_game, quote_character = split_tweet(tweet)
                if quote_text:
                    if len(quote_text) >= 40:
                        quote = QuoteModel(
                            character=quote_character,
                            quote=quote_text,
                            game=quote_game,
                        )
                        await quote.save()
        self.daily_quote_task.start()
        

    @quote.command(name='resend', description='🗿 Restart quote task')
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
            description += f'{Emoji.RS + Emoji.Q1 + Emoji.LS + (Emoji.LL * 13)}\n\n'
            description += f'*{quote.quote}*\n\n'
            description += f'{(Emoji.LL * 13) + Emoji.RS + Emoji.Q2 + Emoji.LS}\n\nㅤㅤ{Emoji.CIRCLE} From **{quote.game}** game\n'

            quote_embed = discord.Embed(
                title=f'💬  {quote.character}',
                description=description,
                color=embed_color,
            )
            banner_embed = discord.Embed(color=embed_color, type='image')
            banner_embed.set_image(url=Assets.QUOTE_BANNER)

            quote_message = await quote_channel.send(embeds=[banner_embed, quote_embed])
            await quote_message.add_reaction('\U0001f5ff')
            await quote.update(
                Inc({QuoteModel.display_count: 1})
            )


async def setup(client:commands.Bot):
    await client.add_cog(Quote(client))