import copy
import discord

from typing import List
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Group, ContextMenu

from data.config import Channel, Config, Assets, Emoji
from modules.utils.validation import is_ban, is_inviter
from modules.view import QandaForm
from modules.utils import error_embed, success_embed, smart_truncate, Paginator, is_ban
from modules.models import QandaModel, MemberModel

class Qanda(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.client.ctx_menus.append(
            ContextMenu(name='🤔 Best Answer', callback=self.qanda_choose_answer, guild_ids=[Config.SERVER_ID])
        )

    # Commands Group
    ask = Group(name="ask", description="🤔 Q&A commands", guild_ids=[Config.SERVER_ID])

    ask_mod = Group(name="ask-mod", description="🤔 Q&A moderator commands", guild_ids=[Config.SERVER_ID])

    # Auto-completes
    async def qanda_games_autocomplete(
    self,
    interaction: discord.Interaction,
    current: str,
    ) -> List[app_commands.Choice[str]]:
        games = self.client.qanda_games
        return [app_commands.Choice(name=game, value=game) for game in games if game.startswith(current.lower())]
    

    async def qanda_search_autocomplete(
    self,
    interaction: discord.Interaction,
    current: str,
    ) -> List[app_commands.Choice[str]]:
        results = await QandaModel.search(current=current)
        return [app_commands.Choice(
            name=('✅' if result.is_answered else '❔') + ' ' + result.title,
            value=result.title
        ) for result in results]
    

    # General commands
    @ask.command(name='new', description = '🤔 Ask a new gaming question')
    @app_commands.checks.cooldown(1, 10)
    @is_ban()
    @is_inviter()
    async def ask_new(self, interaction: discord.Interaction):
        await interaction.response.send_modal(QandaForm(self.client))


    @ask.command(name='search', description='🤔 Search for a question')
    @app_commands.autocomplete(query=qanda_search_autocomplete)
    @app_commands.describe(query='Search query...')
    @app_commands.checks.cooldown(1, 15)
    @is_ban()
    @is_inviter()
    async def ask_search(
        self, 
        interaction: discord.Interaction,
        *,
        query: str
    ):
            
        result = await QandaModel.find_one(
            QandaModel.title == query, 
            QandaModel.is_active == True,
            fetch_links=True
        )

        if result:
            status = '✅' if result.is_answered else '❔'
            em = discord.Embed(
                title=f'{status} {query}', 
                description=result.question, 
                color=Config.BRAND_COLOR
            )
            if result.is_answered:
                em.description += f'\n\n**Answer:**\n>>> *{smart_truncate(result.answer, length=350)}*'
            em.set_author(name='🔎 Search results for:')
            em.set_footer(text=f"Ask new question with /ask new", icon_url=Assets.LOGO_PURPLE_MINI)
            em.add_field(name='\u200b', value=f'[⤵️ Jump to question](https://discord.com/channels/{Config.SERVER_ID}/{Channel.QA_CHANNEL}/{result.question_message_id})\n\u200b')

            await interaction.response.send_message(embed=em)
        else:
            await interaction.response.send_message(embed=error_embed(title='No results found'))


    @ask.command(name='list', description='🤔 List latest questions')
    @app_commands.autocomplete(game=qanda_games_autocomplete)
    @app_commands.describe(game='Enter game for list filter (Optional)')
    @app_commands.checks.cooldown(1, 15)
    @is_ban()
    @is_inviter()
    async def ask_list(
        self,
        interaction: discord.Interaction,
        game: str = None
    ):
        query = {'is_active': True,}
        if game:
            query['game'] = game

        result = await QandaModel.find(query, fetch_links=True).sort('-created_at').limit(25).to_list()
        if not result:
            if game:
                await interaction.response.send_message(embed=error_embed(f"No questions found for {game}"))
            await interaction.response.send_message(embed=error_embed('No questions found'))
        else:
            em = discord.Embed(title=f"🤔 Latest Q&As - {len(result)} Questions found", color=Config.BRAND_COLOR)
            em.description = ''
            em.set_footer(text=f"Ask new question with /ask new", icon_url=Assets.LOGO_PURPLE_MINI)
            
            embeds = []
            item_counter = 0
            loop_counter = 0
            item_embed = copy.deepcopy(em)
            for i in result:
                answers_count = interaction.guild.get_thread(i.thread_id).message_count
                questioner = await interaction.guild.fetch_member(i.questioner.member_id)
                stats = '✅' if i.is_answered else '❔'
                item_embed.description += f"[{stats} {smart_truncate(i.title, length=60)}](https://discord.com/channels/{Config.SERVER_ID}/{Channel.QA_CHANNEL}/{i.question_message_id}) \n *{smart_truncate(i.question, length=80)}*\n<:text:959194994944659496>⠀⠀<:gamepad:959104522058362880>⠀{i.game}⠀⠀<:comments:959104521655701535>⠀{answers_count}⠀⠀<:user:959104521844428830>⠀{questioner.display_name}\n\n"
                item_counter += 1
                loop_counter += 1
                if item_counter == 7:
                    embeds.append(item_embed)
                    item_counter = 0
                    item_embed = copy.deepcopy(em)
                elif loop_counter == len(result):
                    embeds.append(item_embed)

            print(embeds)
            paginate = Paginator(timeout=600, client=self.client)
            await paginate.start(interaction, embeds)


    @ask.command(name='top', description='🤔 List of top respondents')
    @app_commands.checks.cooldown(1, 10)
    @is_ban()
    @is_inviter()
    async def top_list(
        self,         
        interaction: discord.Interaction
    ):
        result = await MemberModel.find(
            MemberModel.question_answered_count > 0,
            MemberModel.is_ban_forever == False,
        ).limit(30).sort('-question_answered_count').to_list()

        if not result:
            await interaction.response.send_message(embed=error_embed('No members found'))
        else:
            em = discord.Embed(title=f"🏆 List of top respondents", color=Config.BRAND_COLOR)
            em.description = ''
            em.set_footer(text=f"Ask new question with /ask new", icon_url=Assets.LOGO_PURPLE_MINI)

            embeds = []
            item_counter = 0
            loop_counter = 0
            item_embed = copy.deepcopy(em)

            for i in result:
                if user:=interaction.guild.get_member(i.member_id):
                    display_name = user.display_name
                else:
                    display_name = i.latest_discord_id
                rank = loop_counter + 1
                if rank == 1:
                    item_embed.description += f"{Emoji.UR + (3 * Emoji.HC)} **`[Ⅰ]` {display_name}**⠀{Emoji.ARROW_FORWARD}⠀**{i.question_answered_count}** *answers*\n"
                elif rank == 2:
                    item_embed.description += f"{Emoji.VC}\n{Emoji.CR + (2 * Emoji.HC)} **`[Ⅱ]` {display_name}**⠀{Emoji.ARROW_FORWARD}⠀**{i.question_answered_count}** *answers*\n"
                elif rank == 3:
                    item_embed.description += f"{Emoji.VC}\n{Emoji.CR + Emoji.HC} **`[Ⅲ]` {display_name}**⠀{Emoji.ARROW_FORWARD}⠀**{i.question_answered_count}** *answers*\n"
                elif rank == len(result):
                    item_embed.description += f"{Emoji.VC}\n{Emoji.DR} **`[#{rank}]` {display_name}**⠀{Emoji.ARROW_FORWARD}⠀**{i.question_answered_count}** *answers*\n"
                else:
                    item_embed.description += f"{Emoji.VC}\n{Emoji.CR} **`[#{rank}]` {display_name}**⠀{Emoji.ARROW_FORWARD}⠀**{i.question_answered_count}** *answers*\n"

                item_counter += 1
                loop_counter += 1
                if item_counter == 5:
                    embeds.append(item_embed)
                    item_counter = 0
                    item_embed = copy.deepcopy(em)
                elif loop_counter == len(result):
                    embeds.append(item_embed)
            paginate = Paginator(timeout=600, client=self.client)
            await paginate.start(interaction, embeds)


    async def qanda_choose_answer(self, interaction: discord.Interaction, message: discord.Message):
        if message.channel.type == discord.ChannelType.public_thread and message.channel.parent_id == Channel.QA_CHANNEL:
            qanda_model = await QandaModel.find_one(QandaModel.thread_id == message.channel.id, fetch_links=True)
            if qanda_model and qanda_model.questioner.member_id == interaction.user.id:    

                if qanda_model.is_answered:
                    old_reply = await interaction.channel.fetch_message(qanda_model.answer_message_reply_id)
                    await old_reply.delete()

                # Reply the best answer
                answer_reply = discord.Embed(description=f'✅ Accepted answer', color=discord.Color.green())
                reply_message = await message.reply(embed=answer_reply)
                qanda_model.answer_message_reply_id = reply_message.id
                await interaction.response.send_message(
                    embed=success_embed('You choose the best answer'),
                    ephemeral=True
                )

                # Update the question embed
                question = await message.channel.parent.fetch_message(qanda_model.question_message_id)
                new_embed = question.embeds[0].copy()
                new_embed.color = discord.Color.green()
                new_embed.set_author(name=f'Answered ✅', icon_url=message.author.avatar.url)
                await question.edit(embed=new_embed)

                # Update database
                member_model = await MemberModel.find_one(MemberModel.member_id == interaction.user.id, fetch_links=True)
                member_model.question_answered_count += 1
                
                qanda_model.answer = message.content.strip()
                qanda_model.answer_message_id = message.id
                qanda_model.answerer = member_model
                qanda_model.is_answered = True
                await qanda_model.save()
                await member_model.save()


    # Moderator commands
    @ask_mod.command(name='delete', description='🤔 Delete a question')
    @app_commands.describe(question_id='Question Message ID', db_remove='Delete the question from database')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ask_delete(
        self, 
        interaction: discord.Interaction, 
        question_id: str,
        db_remove: bool = False
    ):
        question_id = int(question_id)
        qanda_model = await QandaModel.find_one(QandaModel.question_message_id == question_id, fetch_links=True)
        if qanda_model:
            try:
                qanda_channel = interaction.guild.get_channel(Channel.QA_CHANNEL)
                question_message = await qanda_channel.fetch_message(qanda_model.question_message_id)
                question_thread = qanda_channel.get_thread(qanda_model.thread_id)
                await question_message.delete()
                await question_thread.delete()
            except:
                pass
            
            if db_remove:
                await qanda_model.delete()
                await interaction.response.send_message(embed=success_embed(f'Question deleted'), ephemeral=True)
            else:
                if qanda_model.is_active:
                    qanda_model.is_active = False
                    await qanda_model.save()
                    await interaction.response.send_message(embed=success_embed(f'Question deactivated'), ephemeral=True)
        else:
            await interaction.response.send_message(embed=error_embed('Question not found'), ephemeral=True)

    
    @ask_new.error
    @ask_search.error
    @ask_list.error
    @top_list.error
    async def on_commands_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                embed=error_embed(f'You are on cooldown for `{round(error.retry_after, 2)}` seconds'), 
                ephemeral=True
            )

async def setup(client: commands.Bot):
    await client.add_cog(Qanda(client))