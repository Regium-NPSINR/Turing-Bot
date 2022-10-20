import logging

import discord
from bot.utils.embed import format_embed
from discord.ext import commands

logger = logging.getLogger(__name__)


class Untimeout(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="untimeout", description="Un-time-out a member on your server."
    )
    @commands.has_permissions(moderate_members=True)
    async def _untimeout(
        self,
        ctx,
        member: discord.Option(
            discord.Member, description="The member of your server to un-time-out."
        ),
        *,
        reason: discord.Option(
            str,
            description="The reason for the un-time-out. Shows up in audit log. Defaults to None "
            "provided.",
            default="None provided.",
        ),
    ):
        await ctx.defer()

        # Removed timeout from the member.
        await member.remove_timeout(reason=reason)

        title = "Un-time-out: Success!"
        description = f"{member} was un-timed-out!\nReason: {reason}"

        embed = format_embed(title, description)

        await ctx.respond(embed=embed)

        logger.info(f"{ctx.guild.name} -> {member} was un-timed-out!")

    @_untimeout.error
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = "Un-time-out: Error!"
            description = f"Unable to un-time-out: The user has insufficient permissions to un-time-out!"

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)

        if isinstance(error, commands.BotMissingPermissions):
            title = "Un-time-out: Error!"
            description = f"Unable to un-time-out: The target user has a higher role than the bot!"

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Untimeout(bot))
