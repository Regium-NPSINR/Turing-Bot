import asyncio
import datetime
import logging

import discord
from bot.utils.converters import DurationConverter
from bot.utils.embed import format_embed
from discord.ext import commands

logger = logging.getLogger(__name__)


class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="timeout",
        description="Time-out a member so they can't type in chat or join voice channels.",
    )
    @commands.has_permissions(moderate_members=True)
    async def _timeout(
        self,
        ctx,
        member: discord.Option(
            discord.Member, description="The member of your server to time-out."
        ),
        duration: discord.Option(
            DurationConverter,
            description="The duration to time-out the member of the server. Example: 30s, 15m, 12h, 7d.",
        ),
        *,
        reason: discord.Option(
            str,
            description="The reason for the time-out. Shows up in audit log. Defaults to None provided.",
            default="None provided.",
        ),
    ):
        await ctx.defer()

        multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        amount, unit = duration

        # Time the member out.
        await member.timeout_for(
            datetime.timedelta(seconds=(amount * multiplier[unit])), reason=reason
        )

        title = "Time-out: Success!"
        description = f"{member} was timed-out!\nDuration: {''.join((str(duration[0]), duration[-1]))}\nReason: {reason} "

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)

        logger.info(f"{ctx.guild.name} -> {member} was timed-out!")

        await asyncio.sleep((amount * multiplier[unit]))

        # Discord automatically un-times the member out.
        title = "Un-time-out: Success!"
        description = f"{member} was un-timed-out!\nReason: Time-out duration of {''.join((str(duration[0]), duration[-1]))} has passed! "

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)

        logger.info(f"{ctx.guild.name} -> {member} was un-timed-out!")

    @_timeout.error
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = "Time-out: Error!"
            description = f"Unable to time-out: The user has insufficient permissions to time-out!"

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)

        if isinstance(error, commands.BotMissingPermissions):
            title = "Time-out: Error!"
            description = (
                f"Unable to time-out: The target user has a higher role than the bot!"
            )

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Timeout(bot))
