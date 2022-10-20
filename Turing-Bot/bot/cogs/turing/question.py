import asyncio
import json
import logging
import os
import random

import discord
from bot.utils.embed import format_embed
from discord.ext import commands

logger = logging.getLogger(__name__)


class Question(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="question",
        description="Provide a question to solve. Has a timeout for 15 minutes.",
    )
    @discord.option(
        "difficulty",
        str,
        description="The difficulty of the question.",
        choices=["easy", "hard"],
    )
    async def _question(self, ctx, difficulty: str):
        await ctx.defer()

        # Do not allow invoking of command outside the problems channel.
        if not ctx.channel.name == "problems":
            title = "Question: Failure!"
            description = "You cannot use this command here! Use this command in the problems channel only."

            embed = format_embed(title, description)

            await ctx.respond(embed=embed)

            return

        # Get the team name from channel category.
        team_name = ctx.channel.category.name

        # Get the data file path for the current team.
        data_file_path = f"bot/data/{team_name}.json"

        # Load the data file.
        with open(data_file_path, "r") as data_file:
            data = json.load(data_file)
            data_file.close()

        # If the team skipped a question, add it to solved_questions and clear the current question.
        if data["current_question"] != "":
            data["solved_questions"].append(data["current_question"])
            data["current_question"] = ""

            with open(data_file_path, "w") as data_file:
                json.dump(data, data_file)
                data_file.close()

        # Store all available questions into a dictionary, sorting by difficulty.
        questions_list = {
            "easy": [
                os.path.join(os.path.relpath(path), name)
                for path, sub_dirs, files in os.walk("bot/questions/easy")
                for name in files
            ],
            "hard": [
                os.path.join(os.path.relpath(path), name)
                for path, sub_dirs, files in os.walk("bot/questions/hard")
                for name in files
            ],
        }

        # Get the path of the randomly chosen question from questions_list.
        question_path = random.choice(
            [
                question
                for question in questions_list[difficulty]
                if question.split("/")[-1].split(".")[0] not in data["solved_questions"]
            ]
        )

        question_name = question_path.split("/")[-1].split(".")[0]

        # Store the random question as the current question and write to data file.
        data["current_question"] = question_name

        with open(data_file_path, "w") as data_file:
            json.dump(data, data_file)
            data_file.close()

        # Send the question pdf as an attachment.
        file = discord.File(question_path)
        await ctx.respond(file=file)

        logger.info(f"Sent {question_name} to {team_name}!")

        # Set timeout.
        await ctx.guild.create_role(name=f"{team_name}-{question_name}")

        role = discord.utils.get(ctx.guild.roles, name=f"{team_name}-{question_name}")
        logger.info(role)
        await ctx.channel.set_permissions(role, read_messages=True, send_messages=False)
        await ctx.user.add_roles(role)

        # Sleep for 15 minutes.
        await asyncio.sleep(900)

        # Send the timeout removal message if the timeout is still present.
        try:
            logger.info(f"The timeout for {team_name} has passed!")
            await ctx.user.remove_roles(role)
            await role.delete()

        # If the role doesn't exist (it was deleted after submission), don't do anything.
        except discord.errors.NotFound:
            pass

        except commands.RoleNotFound:
            pass


def setup(bot):
    bot.add_cog(Question(bot))
