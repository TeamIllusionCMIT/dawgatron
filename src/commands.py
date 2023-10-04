from discord.ext.commands.cog import Cog
from discord import ApplicationContext
from .bot import DawgtaviousVandross
from discord.ext.commands import slash_command


class Commands(Cog):
    __slots__ = "bot"

    def __init__(self, bot: DawgtaviousVandross):
        self.bot = bot

    @slash_command(description="add a user to the whitelist")
    async def whitelist(self, ctx: ApplicationContext, user: str):
        if await self.bot.redis.sismember("whitelist", user):
            return await ctx.respond(f"{user} is already whitelisted.")
        await self.bot.redis.sadd("whitelist", user)
        await ctx.respond(f"added {user} to the whitelist.")

    @slash_command(description="remove a user from the whitelist")
    async def unwhitelist(self, ctx: ApplicationContext, user: str):
        if not await self.bot.redis.sismember("whitelist", user):
            return await ctx.respond(f"{user} is not whitelisted.")
        await self.bot.redis.srem("whitelist", user)
        await ctx.respond(f"removed {user} from the whitelist.")

    @slash_command(description="list all whitelisted users")
    async def whitelist_list(self, ctx: ApplicationContext):
        await ctx.respond(", ".join(member.decode() for member in await self.bot.redis.smembers("whitelist")), ephemeral=True)

    @slash_command(description="check if a user is whitelisted")
    async def whitelist_check(self, ctx: ApplicationContext, user: str):
        if await self.bot.redis.sismember("whitelist", user):
            return await ctx.respond(f"{user} is whitelisted.")
        await ctx.respond(f"{user} is not whitelisted.")

    @slash_command(description="lock the server")
    async def lock(self, ctx: ApplicationContext):
        if await self.bot.redis.hget("config", "lock"):
            return await ctx.respond("the server is already locked.")
        await self.bot.redis.hset("config", "lock", 1)
        await ctx.respond("locked the server.")

    @slash_command(description="unlock the server")
    async def unlock(self, ctx: ApplicationContext):
        if not await self.bot.redis.hget("config", "lock"):
            return await ctx.respond("the server is not locked.")
        await self.bot.redis.hset("config", "lock", 1)
        await ctx.respond("unlocked the server.")

    @slash_command(description="add all current members to the whitelist")
    async def sync_whitelist(self, ctx: ApplicationContext):
        await self.bot.redis.sadd("whitelist", [member.name for member in ctx.guild.members])
        await ctx.respond("synced whitelist.")

def setup(bot):
    bot.add_cog(Commands(bot))
