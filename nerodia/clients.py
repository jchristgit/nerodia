"""
Initializes various clients
from the authorization data
in the `config.json` file.
For Discord, only a token
is saved instead of the
client itself, because discord.py
initializes a client session
on bot creation, and no proper
cleanup is done when the bot
is never run (e.g. in tests).
"""

import praw

from .config import DISCORD_CFG, REDDIT_CFG, TWITCH_CFG
from .twitch import TwitchClient


reddit = praw.Reddit(
    client_id=REDDIT_CFG["client_id"],
    client_secret=REDDIT_CFG["client_secret"],
    username=REDDIT_CFG["username"],
    password=REDDIT_CFG["password"],
    user_agent=REDDIT_CFG["user_agent"]
)

twitch = TwitchClient(client_id=TWITCH_CFG["client_id"])
