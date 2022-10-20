import asyncio
import logging

import discord
from bot.utils.converters import DurationConverter
from bot.utils.embed import format_embed
from discord.ext import commands

logger = logging.getLogger()


class Ban(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="ban",
        description="Ban a member from your server, with an optional time limit.",
    )
    @commands.has_permissions(ban_members=True)
    async def _ban(
        self,
        ctx,
        member: discord.Option(
            discord.Member, description="The member of your server to ban."
        ),
        duration: discord.Option(
            DurationConverter,
            description="The duration to ban the member of the server. Defaults to permanent. Example: "
            "30s, 15m, 12h, 7d.",
            default="Permanent",
        ),
        *,
        reason: discord.Option(
            str,
            description="The reason for the ban. Shows up in audit log. Defaults to None provided.",
            default="None provided.",
        ),
    ):
        await ctx.defer()

        # Ban the member.
        await member.ban(reason=reason)

        title = "Ban: Success!"
        description = f"{member} was banned!\nDuration: {''.join((str(duration[0]), duration[-1])) if duration != 'Permanent' else duration}\nReason: {reason}"

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)

        logger.info(f"{ctx.guild.name} -> {member} was banned!")

        if duration != "Permanent":
            multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            amount, unit = duration

            # Sleep for the required duration for unban.

            await asyncio.sleep(amount * multiplier[unit])

            # Unban the member.
            await member.unban(
                reason=f"Ban duration of {''.join((str(duration[0]), duration[-1]))} has passed!"
            )

            title = "Un-ban: Success!"
            description = f"{member} was un-banned!\nReason: Ban duration of {''.join((str(duration[0]), duration[-1]))} has passed."

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)

            logger.info(f"{ctx.guild.name} -> {member} was un-banned!")

    @_ban.error
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = "Ban: Error!"
            description = (
                f"Unable to ban: The user has insufficient permissions to ban!"
            )

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)

        if isinstance(error, commands.BotMissingPermissions):
            title = "Ban: Error!"
            description = (
                f"Unable to ban: The target user has a higher role than the bot!"
            )

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Ban(bot))
