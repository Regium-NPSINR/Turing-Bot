import json
import logging

import discord
from bot.utils.embed import format_embed
from discord.ext import commands

logger = logging.getLogger(__name__)


class ScorerModal(discord.ui.Modal):
    def __init__(self, answer, channel, *args, **kwargs):
        super().__init__(*args, **kwargs, title="Enter your custom response.")

        self.answer = answer
        self.channel = channel

        self.add_item(
            discord.ui.InputText(
                label="Custom response: ", style=discord.InputTextStyle.long
            )
        )

    async def callback(self, interaction):
        if self.answer.lower() == "correct":
            color = discord.Color.from_rgb(89, 227, 128)

        else:
            color = discord.Color.from_rgb(227, 68, 68)

        title = f"Your answer was {self.answer}!"
        description = f"\n{self.children[0].value}"

        embed = format_embed(title, description, color)

        await self.channel.send(embed=embed)

        title = "Submit"
        description = "The message was successfully sent!"

        embed = format_embed(title, description)

        await interaction.response.send_message(embed=embed)


class ScorerButtons(discord.ui.View):
    def __init__(self, channel, team_name, question_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.channel = channel
        self.team_name = team_name
        self.question_name = question_name

    @discord.ui.button(label="Correct!", style=discord.ButtonStyle.green)
    async def correct_button_callback(self, button, interaction):
        with open(f"bot/data/{self.team_name}.json", "r") as data_file:
            data = json.load(data_file)
            data_file.close()

        role = discord.utils.get(
            interaction.guild.roles, name=f"{self.team_name}-{self.question_name}"
        )
        try:
            await role.delete()

        except discord.errors.NotFound:
            pass

        except commands.RoleNotFound:
            pass

        except AttributeError:
            pass

        await interaction.response.send_modal(
            ScorerModal(answer="correct", channel=self.channel)
        )

        data["solved_questions"].append(self.question_name)
        data["current_question"] = ""

        with open(f"bot/data/{self.team_name}.json", "w") as data_file:
            json.dump(data, data_file)
            data_file.close()

    @discord.ui.button(label="Incorrect!", style=discord.ButtonStyle.danger)
    async def incorrect_button_callback(self, button, interaction):
        await interaction.response.send_modal(
            ScorerModal(answer="incorrect", channel=self.channel)
        )


class AnswerModal(discord.ui.Modal):
    def __init__(self, question_name, *args, **kwargs):
        super().__init__(*args, **kwargs, title=f"Answer for {question_name}.")

        self.question_name = question_name

        self.add_item(
            discord.ui.InputText(label="Answer: ", style=discord.InputTextStyle.long)
        )

    async def callback(self, interaction):
        title = "Submission"
        description = (
            f"Team: {interaction.channel.category.name}"
            f"\nQuestion: {self.question_name}"
            f"\nAnswer: {self.children[0].value}"
        )

        embed = format_embed(title, description)

        # Get the submissions channel where all submissions will go.
        submissions_channel = discord.utils.get(
            interaction.guild.channels, name="submissions"
        )

        await submissions_channel.send(
            embed=embed,
            view=ScorerButtons(
                channel=interaction.channel,
                question_name=self.question_name,
                team_name=interaction.channel.category.name,
            ),
        )

        logger.info(
            f"The answer by {interaction.channel.category.name} has been sent to a scorer!"
        )

        title = "Submit: Success!"
        description = f"Your answer for {self.question_name} has been sent to a scorer!"

        embed = format_embed(title, description)
        await interaction.response.send_message(embed=embed)


class Submit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="submit", description="Submit your answer for the current problem."
    )
    async def _submit(self, ctx):
        # Do not allow invoking of command outside the submit channel.
        if not ctx.channel.name == "submit":
            title = "Submit: Failure!"
            description = "You cannot use this command here! Use this command in the submit channel only."

            embed = format_embed(title, description)

            await ctx.respond(embed=embed)

        # Get the team name from channel category.
        team_name = ctx.channel.category.name

        # Read the question status data file.
        with open(f"bot/data/{team_name}.json", "r") as data_file:
            data = json.load(data_file)
            data_file.close()

        # Get the current question.
        question_name = data["current_question"]

        # If there is no current question, prompt to generate a new question.
        if question_name == "":
            title = "Submit: Error!"
            description = "There is no available question to answer! Generate a new question using the /question "

            embed = format_embed(title, description)
            await ctx.respond(embed=embed)

            return

        # Create a modal for answering the question.
        await ctx.send_modal(AnswerModal(question_name=question_name))


def setup(bot):
    bot.add_cog(Submit(bot))
