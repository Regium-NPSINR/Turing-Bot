import json
import logging

import anvil.server
import discord
from bot.utils.embed import format_embed
from discord.ext import commands

logger = logging.getLogger(__name__)


class Scoring(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    scoring = discord.SlashCommandGroup("scoring", "Scoring related commands.")

    @scoring.command(name="easy", description="Score an easy question.")
    @commands.has_permissions(administrator=True)
    @discord.option(
        "team",
        discord.CategoryChannel,
        description="The team to increment score.",
    )
    async def _easy(self, ctx, team: discord.CategoryChannel):
        await ctx.defer()

        anvil.server.call("solve_easy", team.name)

        logger.info(f"Updated the score of {team.name} for solving an easy question!")

        title = "Scoring - Easy: Success!"
        description = f"Updated the score of {team.name} for solving an easy question!"

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)

    @scoring.command(name="hard", description="Score a hard question.")
    @commands.has_permissions(administrator=True)
    @discord.option(
        "team_1",
        discord.CategoryChannel,
        description="The team to increment score to.",
    )
    @discord.option(
        "team_2",
        discord.CategoryChannel,
        description="The team to decrement score from.",
    )
    async def _hard(
        self, ctx, team_1: discord.CategoryChannel, team_2: discord.CategoryChannel
    ):
        await ctx.defer()

        anvil.server.call("solve_hard", team_1.name, team_2.name)

        logger.info(
            f"Updated the score of {team_1.name} and {team_2.name} for solving a hard question!"
        )

        title = "Scoring - Easy: Success!"
        description = f"Updated the scores of {team_1.name} and {team_2.name} for solving a hard question!"

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)

    @scoring.command(name="set", description="Manually set the score for a team.")
    @commands.has_permissions(administrator=True)
    @discord.option(
        "team",
        discord.CategoryChannel,
        description="The team to set score for.",
    )
    @discord.option("score", int, description="The score to set.")
    async def _set(self, ctx, team: discord.CategoryChannel, score: int):
        await ctx.defer()

        anvil.server.call("set_score", team.name, score)

        logger.info(f"Set the score of {team.name} to {score}!")

        title = "Scoring - Set: Success!"
        description = f"Updated the score of {team.name} to {score}!"

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(Scoring(bot))
