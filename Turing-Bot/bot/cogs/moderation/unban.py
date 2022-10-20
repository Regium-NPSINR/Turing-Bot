import logging

import discord
from bot.utils.embed import format_embed
from discord.ext import commands

logger = logging.getLogger(__name__)


class Unban(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    @commands.slash_command(name="unban", description="Un-ban a member on your server.")
    @commands.has_permissions(ban_members=True)
    async def _unban(
        self,
        ctx,
        member: discord.Option(
            discord.Member,
            description="The user id of the member of your server to un-ban. Example: 917304348420231208",
        ),
        *,
        reason: discord.Option(
            str,
            description="The reason for the un-ban. Shows up in audit log. Defaults to None provided.",
            default="None provided.",
        ),
    ):
        await ctx.defer()

        # Unban the member.
        await member.unban(reason=reason)

        title = "Un-ban: Success!"
        description = f"{member} was un-banned!\nReason: {reason}"

        embed = format_embed(title, description)

        await ctx.respond(embed=embed)

        logger.info(f"{ctx.guild.name} -> {member} was un-banned!")

    @_unban.error
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = "Un-ban: Error!"
            description = (
                f"Unable to un-ban: The user has insufficient permissions to un-ban!"
            )

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)

        if isinstance(error, commands.BotMissingPermissions):
            title = "Un-ban: Error!"
            description = (
                f"Unable to un-ban: The target user has a higher role than the bot!"
            )

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Unban(bot))
