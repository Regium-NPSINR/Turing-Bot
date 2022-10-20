import logging

import discord
from bot.utils.embed import format_embed
from discord.ext import commands

logger = logging.getLogger(__name__)


class Purge(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="purge", description="Purge a given number of messages."
    )
    @commands.has_permissions(manage_messages=True)
    async def _purge(
        self,
        ctx,
        amount: discord.Option(
            int,
            description="The number of messages to purge.",
        ),
    ):
        await ctx.defer()

        # Purge the channel.
        await ctx.channel.purge(limit=amount + 1)

        title = "Purge: Success!"
        description = f"Purged {amount} messages!"

        embed = format_embed(title, description)

        await ctx.send(embed=embed, delete_after=5)

        logger.info(f"{ctx.guild.name} -> Purged {amount} messages!")

    @_purge.error
    async def on_application_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            title = "Purge: Error!"
            description = (
                f"Unable to purge: The user has insufficient permissions to purge!"
            )

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Purge(bot))
