import discord

from discord.ext import commands, tasks
from beanie.odm.operators.update.general import Set

from data.config import Config
from modules.models import MemberModel
from modules.utils import set_level
from modules.view import StartSurveyView


class Survey(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

        self.send_survey_loop.start()


    @tasks.loop(seconds=30)
    async def send_survey_loop(self):
        guild = await self.client.fetch_guild(Config.SERVER_ID)
        target_users = await MemberModel.survey_users()

        if target_users != []:
            for user in target_users:
                member = await guild.fetch_member(user.member_id)
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False),
                    member: discord.PermissionOverwrite(view_channel=True, send_messages=False, read_messages=True)
                }
                survey_channel = await guild.create_text_channel(
                    name= 'Hey ' + member.display_name + '👋',
                    position=0,
                    overwrites=overwrites
                )
                em = discord.Embed(
                    description= f'***Hey there {member.mention}***,\nThank you for supporting us so far, We need your help to conduct a survey, this will help us a lot in improving the ***user experience*** and thus ***expanding the community***. \n\n' + set_level(1),
                    color=Config.BRAND_COLOR
                )
                em.set_thumbnail(url=member.display_avatar.url)
                await survey_channel.send(embed=em, content=f'{member.mention}', view=StartSurveyView())

                await user.update(
                    Set({MemberModel.is_surveyed: True})
                )



async def setup(client:commands.Bot):
    await client.add_cog(Survey(client))