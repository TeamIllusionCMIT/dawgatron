from discord.bot import Bot
from discord import Intents, MemberCacheFlags

class DawgtaviousVandross(Bot):
    def __init__(self, token: str):
        if not token:
            raise ValueError(
                "no discord API token provided; set the TOKEN environment variable or pass one into the bot"
            )

        intents = Intents.none()
        intents.message_content = True
        intents.guild_messages = True
        intents.members = True

        member_cache_flags = MemberCacheFlags.none()
        member_cache_flags.joined = True

        super().__init__(
            command_prefix="dawg ",
            member_cache_flags=member_cache_flags,
            intents=intents,
        )
        self.token = token

    async def on_ready(self):
        print(f"logged in as {self.user.name} ({self.user.id})")
        print("------")

    def run(self):
        super().run(self.token)
