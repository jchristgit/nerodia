"""
Contains the command group
for the Discord Bot.
"""

import asyncio
import datetime
import discord
from typing import Optional

from discord.ext import commands

from . import util
from .util import token_dict, token_lock, verify_dict, verify_lock


DM_ONLY_EMBED = discord.Embed(
    title="Cannot connect accounts:",
    description="For safety reasons, this command can "
                "only be used in private messages.",
    colour=discord.Colour.red()
)
PM_URL = "https://www.reddit.com/message/compose?to=Botyy&subject=verification"

# The timeout for the reddit verification, in minutes
VERIFY_TIMEOUT = 5


def create_instructions() -> discord.Embed:
    """
    Creates an Embed containing the disclaimer
    for adding a Reddit account to your Discord account.
    This should be used for adding a field with the token
    which the user should send to the bot via a direct message.

    Returns:
        discord.Embed: An embed with a disclaimer about user data.
    """

    return discord.Embed(
        title="Connect your Reddit Account",
        colour=discord.Colour.blue(),
        timestamp=datetime.datetime.now()
    ).add_field(
        name="Disclaimer",
        value="By connecting your account, you agree that your "
              "**Discord ID is stored unencrypted for an indefinite "
              "time, along with your reddit name, and this information "
              "may appear in the bot's log messages**. You can "
              "disconnect a connected account at any time.",
        inline=False
    ).set_footer(
        text="⏲ You have five minutes time."
    )


async def wait_for_add(user_id: str, timeout: int = VERIFY_TIMEOUT) -> Optional[str]:
    """
    Waits for the given user to add his reddit
    account. It is highly recommended to set
    a timeout, this defaults to five minutes.
    The dictionary which contains data about
    verification is checked in intervals,
    accomplished by sleeping for five seconds
    between checking the dictionary.

    Arguments:
        user_id (str):
            The Discord user ID for the user
            who wants to add his reddit account.
        timeout (int):
            The timeout (in minutes) after which
            `None` should be returned indicating
            that the user did not send a direct
            message for adding his reddit account
            in time. The user is removed from the
            verification dictionary. Defaults to
            the value of `VERIFY_TIMEOUT`.

    Returns:
        Optional[str]:
            The reddit name of the user if successful,
            `None` if no direct message containing the
            token was received in time.
    """

    timeout_ctr = timeout * 60
    while timeout_ctr > 0:
        await asyncio.sleep(5)
        with verify_lock:
            user = verify_dict.get(user_id)

        if user is not None:
            with verify_lock:
                del verify_dict[user]
            return user

        timeout_ctr -= 5
    return None


class Nerodia:
    """Commands for interacting with the Nerodia reddit bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        print("[DISCORD] Loaded Commands.")

    @commands.command(name="connectreddit")
    async def connect_reddit(self, ctx):
        """
        Connects your Discord account to your reddit account.
        Please make sure to carefully read through the
        instructions that this command sends upon invocation.

        This command can only be used in private messages
        to prevent other people connecting their reddit account
        to yours, for whatever reason.
        """

        if not isinstance(ctx.message.channel, discord.abc.PrivateChannel):
            return await ctx.send(embed=DM_ONLY_EMBED)

        token = util.random_string()
        await ctx.send(embed=create_instructions().add_field(
            name="Instructions",
            value=f"Send me a [Reddit Message]({PM_URL}) containing"
                  f"`{token}` to add your reddit account.",
            inline=False
        ))

        author_id = str(ctx.message.author.id)
        with token_lock:
            token_dict[author_id] = token

        reddit_name = await wait_for_add(author_id)


def setup(bot):
    bot.add_cog(Nerodia(bot))
