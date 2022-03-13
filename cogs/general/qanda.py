import discord

from discord import slash_command, message_command
from discord.ext import commands

from data.config import Channel, Config
from modules.view import QandaForm
from modules.database.models import QandaModel, MemberModel
        

class Qanda(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        
    @slash_command(description = 'Ask a gaming question', guild_ids=[Config.SERVER_ID]) 
    async def qanda(self, ctx):
        await ctx.send_modal(QandaForm(self.client))
    

    @message_command(name='🤔 Best Answer', guild_ids=[Config.SERVER_ID])
    async def qanda_choose_answer(self, ctx: discord.ApplicationContext, message: discord.Message):
        if message.channel.type == discord.ChannelType.public_thread and message.channel.parent_id == Channel.QA_CHANNEL_ID:
            qanda_model = await QandaModel.find_one(QandaModel.thread_id == message.channel.id, fetch_links=True)
            if qanda_model and not qanda_model.is_answered and qanda_model.questioner.member_id == ctx.respond.user.id:
                
                # Reply the best answer
                answer_reply = discord.Embed(description=f'✅ Accepted answer', color=discord.Color.green())
                await message.reply(embed=answer_reply)

                # Update the question embed
                question = await message.channel.parent.fetch_message(qanda_model.question_message_id)
                new_embed = question.embeds[0].copy()
                new_embed.color = discord.Color.green()
                new_embed.set_author(name=f'Answered ✅', icon_url=message.author.avatar.url)
                await question.edit(embed=new_embed)

                # Update database
                qanda_model.answer = message.content.strip()
                qanda_model.answer_message_id = message.id
                qanda_model.answerer = await MemberModel.find_one(MemberModel.member_id == message.author.id)
                qanda_model.is_answered = True
                await qanda_model.replace()

        await ctx.delete()
            

def setup(client:commands.Bot):
    client.add_cog(Qanda(client))