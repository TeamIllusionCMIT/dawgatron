from discord.ext.bridge import Bot
from discord import Intents, MemberCacheFlags, Member, Embed
from redis.asyncio import Redis


class DawgtaviousVandross(Bot):
    __slots__ = ("redis", "token", "kick_embed")

    def __init__(self, token: str, redis_url: str):
        self.redis = Redis.from_url(redis_url)

        # turn off all but a few intents to save bandwith and resources
        intents = Intents.none()
        intents.message_content = True
        intents.guild_messages = True
        intents.members = True
        intents.guilds = True

        # we dont need to cache members so turn it off to save memory
        member_cache_flags = MemberCacheFlags.none()

        # build the embed notifying people how and why they were kicked
        # we can do it in advance just to be more efficient

        self.kick_embed = (
            Embed(
                description="you aren't whitelisted in this server! ask someone in the server to whitelist your username."
            )
            .set_author(name="server security")
        )
        self.kick_embed.color = 0x2F3136 # type: ignore

        super().__init__(
            command_prefix="dawg ",  # for using jishaku
            member_cache_flags=member_cache_flags,
            intents=intents,
        )
        self.token = token

    async def on_ready(self):
        print(f"[i] logged in as {self.user.name} ({self.user.id})")
        print("------")
        self.kick_embed.set_footer(text=f"womp womp, {self.user.name}")

    async def on_member_join(self, member: Member):
        if not await self.redis.sismember("whitelist", member.name) and await self.redis.hget("config", "lock"):
            await member.send(embed=self.kick_embed)
            await member.kick(reason="server is locked")
            print(f"[x] kicked {member.name} ({member.id})")



    def run(self):
        super().run(self.token)
