

import discord
from discord.channel import TextChannel
from discord.commands import ApplicationContext, Option
from discord.ext import commands

from data.config import Assets, Channel, Config
from modules.utils import error_embed, success_embed
from modules.view import CreateRoomView


class MainModeration(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

    @commands.slash_command(name='room_msg', description='Send create new room Embed', guild_ids=[Config.SERVER_ID])
    async def room_msg(
        self,
        ctx: ApplicationContext,
        coach_button: Option(bool, 'is coach active?', required=False, default=True),
        loop_button: Option(bool, 'is loop button active?', required=False, default=True),
        delete_msg: Option(bool, 'is delete all messeges?', required=False, default=True),
        ) -> None:
        
        try:
            channel: TextChannel = await ctx.guild.fetch_channel(Channel.CREATE_ROOM)

            if delete_msg:
                async for m in channel.history():
                    await m.delete()
                
            em = discord.Embed(
                description = 'CONTEXT_CREATE_ROOM_DES',
                color = Config.BRAND_COLOR
            )
            em.set_author(name='CONTEXT_CREATE_ROOM_HEADER', icon_url=Assets.ADD_ICON)
            em.set_image(url=Assets.LFG_BANNER)

            view = CreateRoomView(client = self.client)
            # view.interaction_check = is_ban

            if coach_button:
                # view.add_item(None) #TODO: create coach
                pass
            if loop_button:
                # view.add_item(None)
                pass

            await channel.send(
                embed=em,
                view=view
            )
            await ctx.response.send_message(
            embed=success_embed(f'Message sent.'),
            ephemeral=True,
            )

        except Exception as e:
            await ctx.response.send_message(
                embed=error_embed(f'Message not sent. error:\n {e}'),
                ephemeral=True,
                )
            raise e

        finally:
            if not ctx.response.is_done:
                ctx.defer()


    @commands.slash_command(name='clear', description='clear msgs', guild_ids=[Config.SERVER_ID])
    async def clear(
        self,
        ctx: ApplicationContext,
        limit: Option(int, 'Enter the value'),
        oldest_first: Option(bool, 'oldest first', required=False, default=False),
        ) -> None:
        async with ctx.typing():
            await ctx.channel.purge(limit=limit, oldest_first=oldest_first )
        await ctx.delete()
        
async def setup(client:commands.Bot):
    await client.add_cog(MainModeration(client))