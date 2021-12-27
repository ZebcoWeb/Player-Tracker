import asyncio
from datetime import datetime

import discord
from discord.commands import ApplicationContext, Option
from discord.ext import commands

from data.config import Assets, Channel, Config, Todoist
from modules.utils import is_ban
from modules.view import TaskView


class TaskCog(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.description = 'Task system (only admins)'

    @commands.slash_command(name='addtask', description='Add new task (only admins)', guild_ids=[Config.SERVER_ID])
    async def new_task(
        self,
        ctx: ApplicationContext,
        priority: Option(str, "Choose task priority", choices=["Low", "Medium", "High"]),
        task: Option(str, "Enter the task", required=True)
        ) -> None:

        if priority.lower() == 'low':
            embed_color = 0xFEE75C
            #todoist_label = Todoist.LABEL_LOW
        elif priority.lower() == 'medium':
            embed_color = 0xe67e22
            #todoist_label = Todoist.LABEL_MEDIUM
        elif priority.lower() == 'high':
            embed_color = 0xe74c3c
            #todoist_label = Todoist.LABEL_HIGH

        embed = discord.Embed(
            description = task + '\n',
            color = embed_color,
            timestamp = datetime.now()
        )
        embed.set_author(
            name = f'New Task by {ctx.author.name} | {priority} Priority',
            icon_url = Assets.TASK_ICON
        )
        embed.set_footer(
            text = 'Player Tracker Task System',
            icon_url = Assets.LOGO_PURPLE_MINI
        )


        task_channel = self.client.get_channel(Channel.TASK_SYSTEM)
        await ctx.delete()
        view = TaskView()
        await view.interaction_check(is_ban)
        await task_channel.send(
            embed = embed,
            view = TaskView(),
        )

def setup(client: commands.Bot):
    client.add_cog(TaskCog(client))