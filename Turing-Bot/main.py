import logging
import os

import anvil.server
from bot.bot import Bot
from dotenv import load_dotenv
from rich.logging import RichHandler

load_dotenv()

# Get discord token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ANVIL_CLIENT_KEY = os.getenv("ANVIL_CLIENT_KEY")

# Setup logging using rich's logging handler.
FORMAT = "%(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(markup=True)],
)

logger = logging.getLogger()


def main(token):
    # Connect to the anvil leaderboards server.
    # TODO: uncomment anvil
    # anvil.server.connect(ANVIL_CLIENT_KEY, url="ws://turing.regium22.com/_/uplink")

    # Run the bot.
    bot = Bot()
    bot.run(token)


if __name__ == "__main__":
    main(DISCORD_TOKEN)
