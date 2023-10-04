from discord.ext.commands.cog import Cog
from discord import ApplicationContext, Member
from .bot import DawgtaviousVandross
from discord.ext.commands import slash_command


class Commands(Cog):
    __slots__ = "bot"

    def __init__(self, bot: DawgtaviousVandross):
        self.bot = bot
        self.redis = bot.redis

    @Cog.listener("on_member_join")
    async def ban_unwhitelisted(self, member: Member):
        if self.redis.hget("config", "lock") and not self.redis.sismember(
            "whitelist", member.name
        ):
            await member.send(self.bot._build_kick_embed())
            await member.kick(reason="server is locked")

    @slash_command(description="add a user to the whitelist")
    async def whitelist(self, ctx: ApplicationContext, user: str):
        if self.bot.redis.sismember("whitelist", user):
            return await ctx.respond(f"{user} is already whitelisted.")
        await self.bot.redis.sadd("whitelist", user)
        await ctx.respond(f"added {user} to the whitelist.")

    @slash_command(description="remove a user from the whitelist")
    async def unwhitelist(self, ctx: ApplicationContext, user: str):
        if not self.bot.redis.sismember("whitelist", user):
            return await ctx.respond(f"{user} is not whitelisted.")
        await self.bot.redis.srem("whitelist", user)
        await ctx.respond(f"removed {user} from the whitelist.")

    @slash_command(description="list all whitelisted users")
    async def whitelist_list(self, ctx: ApplicationContext):
        await ctx.respond(", ".join(self.bot.redis.smembers("whitelist")), ephemeral=True)

    @slash_command(description="check if a user is whitelisted")
    async def whitelist_check(self, ctx: ApplicationContext, user: str):
        if self.bot.redis.sismember("whitelist", user):
            return await ctx.respond(f"{user} is whitelisted.")
        await ctx.respond(f"{user} is not whitelisted.")

    @slash_command(description="lock the server")
    async def lock(self, ctx: ApplicationContext):
        if self.bot.redis.hget("config", "lock"):
            return await ctx.respond("the server is already locked.")
        self.bot.redis.hset("config", "lock", True)

    @slash_command(description="unlock the server")
    async def unlock(self, ctx: ApplicationContext):
        if not self.bot.redis.hget("config", "lock"):
            return await ctx.respond("the server is not locked.")
        self.bot.redis.hset("config", "lock", True)

    @slash_command(description="add all current members to the whitelist")
    async def sync_whitelist(self, ctx: ApplicationContext):
        for member in ctx.guild.members:
            await self.bot.redis.sadd("whitelist", member.name)
        await ctx.respond("synced whitelist.")

def setup(bot):
    bot.add_cog(Commands(bot))
