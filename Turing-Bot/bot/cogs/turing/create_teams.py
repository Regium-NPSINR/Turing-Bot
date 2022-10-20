import json
import logging

import anvil.server
import discord
from bot.utils.embed import format_embed
from discord.ext import commands

logger = logging.getLogger(__name__)


class CreateTeams(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="create_teams", description="Create teams based on categories."
    )
    @commands.has_permissions(administrator=True)
    async def _create_teams(self, ctx):
        await ctx.defer()

        data = {"current_question": "", "solved_questions": []}

        for team in ctx.guild.categories:
            data_file_path = f"bot/data/{team.name}.json"

            with open(data_file_path, "w+") as data_file:
                json.dump(data, data_file)
                data_file.close()

            anvil.server.call("add_team", team.name)

            logger.info(f"Created team {team.name}")

        logger.info("Created all teams!")

        title = "Created teams!"
        description = "Successfully created teams using categories!"

        embed = format_embed(title, description)
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(CreateTeams(bot))
