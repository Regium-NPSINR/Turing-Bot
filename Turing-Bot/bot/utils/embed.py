import datetime

import discord


def format_embed(title, description, color=discord.Color.from_rgb(0, 0, 0), image=None):
    embed = discord.Embed(
        title=title,
        description=description,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        color=color,
    )

    embed.set_author(
        name="Turing Bot",
        icon_url="https://cdn.discordapp.com/avatars/1029010619527090286/9cf445911fbf3beb8e1fc3d4aa945181.png",
    )

    if image is not None:
        embed.set_image(url=image)

    return embed
