from discord import Interaction

from modules.database.models import MemberModel
from modules.utils import error_embed, i18n


async def is_ban(interaction: Interaction):

        member_model = MemberModel.objects.get(member_id=interaction.user.id)
        
        locate = i18n(
            domain='general', 
        lang= member_model.lang
        )
        locate.install()
        _ = locate.gettext

        if member_model.is_ban:

            await interaction.response.send_message(
                embed= error_embed(msg = _('BAN_REPLY_CONTEXT'))
            )
            return False
        return True