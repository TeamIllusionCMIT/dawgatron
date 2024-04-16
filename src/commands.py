from discord.ext.commands.cog import Cog
from discord import ApplicationContext, User
from .bot import DawgtaviousVandross
from discord.ext.commands import slash_command
from discord.channel import TextChannel
from discord.object import Object
from discord.embeds import Embed


class Commands(Cog):
    __slots__ = "bot"

    def __init__(self, bot: DawgtaviousVandross):
        self.bot = bot

    @slash_command(description="help")
    async def help(self, ctx: ApplicationContext):
        embed = Embed(description="commands")
        for command in self.get_commands():
            embed.add_field(name=f"/{command.name}", value=command.description)

        await ctx.respond(embed=embed)

    async def check_bypass_roles(self, ctx: ApplicationContext) -> bool:
        return any([role.id in (await self.bot.redis.hget("config", "bypass_roles") or []) for role in ctx.author.roles]) or ctx.author.guild_permissions.manage_guild

    @slash_command(description="ban someone who's not even in the server")
    async def deathray(self, ctx: ApplicationContext, user: str):
        if not ctx.author.guild_permissions.ban_members:
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        await ctx.guild.ban(Object(id=352193480489172995), reason=f"killed off by {ctx.author.global_name or ctx.author.display_name}")
        await ctx.respond(f"banned <@!{user}>.")

    @slash_command(description="add bypass role")
    async def add_bypass_role(self, ctx: ApplicationContext, role: str):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        new_value = (await self.bot.redis.hget("config", "bypass_roles") or []) + [role]
        await self.bot.redis.hset("config", "bypass_roles", new_value)
        await ctx.respond(f"added {role} to the bypass roles.")

    @slash_command(description="remove bypass role")
    async def remove_bypass_role(self, ctx: ApplicationContext, role: str):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        new_value = (await self.bot.redis.hget("config", "bypass_roles") or []) - [role]
        await self.bot.redis.hset("config", "bypass_roles", new_value)
        await ctx.respond(f"removed {role} from the bypass roles.")

    @slash_command(description="add a user to the whitelist")
    async def set_log_channel(self, ctx: ApplicationContext, channel: TextChannel):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        await self.bot.redis.hset("config", "log_channel", channel.id)
        try:
            await channel.send("this channel is now the log channel.")
        except:
            return await ctx.respond(f"something went wrong. i can't send messages there", ephemeral=True)
        
        await ctx.respond(f"set the log channel to {channel.mention}.")

    @slash_command(description="add a user to the whitelist")
    async def whitelist(self, ctx: ApplicationContext, user: str):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        if await self.bot.redis.sismember("whitelist", user):
            return await ctx.respond(f"{user} is already whitelisted.")
        await self.bot.redis.sadd("whitelist", user)
        await ctx.respond(f"added {user} to the whitelist.")

    @slash_command(description="remove a user from the whitelist")
    async def unwhitelist(self, ctx: ApplicationContext, user: str):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        if not await self.bot.redis.sismember("whitelist", user):
            return await ctx.respond(f"{user} is not whitelisted.", ephemeral=True)
        
        await self.bot.redis.srem("whitelist", user)
        await ctx.respond(f"removed {user} from the whitelist.")

    @slash_command(description="list all whitelisted users")
    async def whitelist_list(self, ctx: ApplicationContext):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        await ctx.respond(", ".join(member.decode() for member in await self.bot.redis.smembers("whitelist")), ephemeral=True)

    @slash_command(description="check if a user is whitelisted")
    async def whitelist_check(self, ctx: ApplicationContext, user: str):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        if await self.bot.redis.sismember("whitelist", user):
            return await ctx.respond(f"{user} is whitelisted.")
        await ctx.respond(f"{user} is not whitelisted.", ephemeral=True)

    @slash_command(description="lock the server")
    async def lock(self, ctx: ApplicationContext):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        if await self.bot.redis.hget("config", "lock"):
            return await ctx.respond("the server is already locked.")
        await self.bot.redis.hset("config", "lock", 1)
        await ctx.respond("locked the server.", ephemeral=True)

    @slash_command(description="unlock the server")
    async def unlock(self, ctx: ApplicationContext):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        if not await self.bot.redis.hget("config", "lock"):
            return await ctx.respond("the server is not locked.")
        await self.bot.redis.hset("config", "lock", 1)
        await ctx.respond("unlocked the server.", ephemeral=True)

    @slash_command(description="add all current members to the whitelist")
    async def sync_whitelist(self, ctx: ApplicationContext):
        if not await self.check_bypass_roles(ctx):
            return await ctx.respond("you don't have permission to use this command.", ephemeral=True)
        
        await self.bot.redis.sadd("whitelist", *[member._user.name async for member in ctx.guild.fetch_members(limit=None) if not member.bot])
        await ctx.respond("synced whitelist.", ephemeral=True)

def setup(bot):
    bot.add_cog(Commands(bot))
