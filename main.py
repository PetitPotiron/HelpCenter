import logging
import os
from collections import OrderedDict
import typing

import discord
from discord.ext import commands
from dotenv import load_dotenv

from cogs.utils import i18n, custom_errors

if typing.TYPE_CHECKING:
    from cogs.utils import Snowflake, Person
    from discord.ext.commands import Context


load_dotenv()

logging.basicConfig()
logger = logging.getLogger(__name__)


class HelpCenterBot(commands.Bot):

    def __init__(self) -> None:
        """A cool Discord bot."""
        self.bug_center_id: 'Snowflake' = 595218682670481418

        self.staff_roles: dict[str, 'Snowflake'] = {
            'administrator': 713434163587579986,
            'assistant': 627445515159732224,
            'screening': 713452724603191367,
            'brillant': 713452621196820510,
            'normal': 627836152350769163
        }

        self.help_channels_id: list['Snowflake'] = [
            692712497844584448,  # general_tech
            833077274458849340,  # tech_international
            870023524985761822   # ask_for_help
        ]
        self.test_channels_id: list['Snowflake'] = [
            595224241742413844,  # tests-1
            595224271132033024,  # tests-2
            595232117806333965,  # cmds-staff
            711599221220048989  # cmds-admin
        ]
        self.authorized_channels_id: list['Snowflake'] = self.test_channels_id + self.help_channels_id

        self.language_roles: OrderedDict['Snowflake', str] = OrderedDict((
            (797581355785125889, 'fr_FR'),
            (797581356749946930, 'en_EN')
        ))  # OrderedDict to make French in prior of English

        super().__init__(
            command_prefix=["/", "\\", "<@789210466492481597> ", "<@!789210466492481597> "],
            case_insensitive=True,
            member_cache_flags=discord.MemberCacheFlags.all(),
            chunk_guilds_at_startup=True,
            allowed_mentions=discord.AllowedMentions.none(),
            intents=discord.Intents.all()
        )

        self.logger: logging.Logger = logger

        extensions: list[str] = ['clash_of_code', 'event', 'tag', 'help', 'command_error', 'miscellaneous', 'lines', 'google_it', 'doc', 'auto_help_system']
        for extension in extensions:
            self.load_extension('cogs.' + extension)

        self.before_invoke(self.set_command_language)
        self.add_check(self.is_on_bug_center)

    async def on_ready(self) -> None:
        activity = discord.Game("/tag <category> <tag>")
        await self.change_presence(status=discord.Status.idle, activity=activity)
        print(f"Logged in as : {self.user.name}")
        print(f"ID : {self.user.id}")

    def is_on_bug_center(self, ctx: 'Context[HelpCenterBot]') -> bool:
        if ctx.guild and ctx.guild.id != self.bug_center_id:
            raise custom_errors.NotInBugCenter()
        return True

    async def set_command_language(self, ctx: 'Context[HelpCenterBot]') -> None:  # function called when a command is executed
        await self.set_actual_language(ctx.author)

    async def set_actual_language(self, person: 'Person') -> None:
        i18n.current_locale.set(self.get_user_language(person))

    def get_user_language(self, person: 'Person') -> str:
        if isinstance(person, discord.User) or person.guild.id != self.bug_center_id:  # if the function was executed in DM
            if guild := self.get_guild(self.bug_center_id):
                member = guild.get_member(person.id)
            else:
                member = None
        else:
            member = person

        if member:
            for role_id, lang in self.language_roles.items():
                if discord.utils.get(member.roles, id=role_id):
                    return lang

        return 'en_EN'

    def run(self) -> None:
        super().run(os.getenv("BOT_TOKEN"), reconnect=True)


if __name__ == "__main__":
    help_center_bot = HelpCenterBot()
    help_center_bot.run()
