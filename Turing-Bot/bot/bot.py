import logging
import os
from fnmatch import fnmatch

import discord
from discord.ext import commands, tasks

# Setup logger.
logger = logging.getLogger(__name__)


# Create bot.
class Bot(commands.Bot):
    def __init__(self):
        # Get all intents available for the bot.
        intents = discord.Intents().all()

        # Add debug guilds because registering slash commands take upwards of an hour.
        super().__init__(
            debug_guilds=[1032677511278104606], intents=intents
        )

        # Load all cogs
        self.load_cogs()

    def load_cogs(self):
        # Get all available cogs in bot/cogs directory and load them.
        cog_list = [
            os.path.splitext(
                ".".join(os.path.join(os.path.relpath(path), name).split("/"))
            )[0]
            for path, sub_dirs, files in os.walk("bot/cogs")
            for name in files
            if fnmatch(name, "*.py")
        ]

        for cog in cog_list:
            if "__init__" in cog:
                continue

            logger.info(f"Loading {cog}...")

            try:
                self.load_extension(cog)
                logger.info(f"Successfully loaded {cog}!")

            except Exception as e:
                logger.error(f"Could not load {cog}! {str(e)}")

    async def on_ready(self):
        await self.wait_until_ready()

        logger.info(f"Logged in as {self.user}!")

        # Change presence
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                name=f"Participants In Regium Turing",
                type=discord.ActivityType.watching,
            ),
        )
