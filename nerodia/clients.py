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

import json

import praw
from twitch import TwitchClient


with open("config.json", 'r') as f:
    as_json = json.load(f)
    DISCORD_AUTH = as_json["discord_auth"]
    REDDIT_AUTH = as_json["reddit_auth"]
    TWITCH_AUTH = as_json["twitch_auth"]

discord_token = DISCORD_AUTH["token"]

reddit = praw.Reddit(
    client_id=REDDIT_AUTH["client_id"],
    client_secret=REDDIT_AUTH["client_secret"],
    username=REDDIT_AUTH["username"],
    password=REDDIT_AUTH["password"],
    user_agent=REDDIT_AUTH["user_agent"]
)

twitch = TwitchClient(client_id=TWITCH_AUTH["client_id"])
