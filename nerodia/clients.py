import json

import praw
from twitch import TwitchClient

with open("config.json", 'r') as f:
    as_json = json.load(f)
    REDDIT_AUTH = as_json["reddit_auth"]
    TWITCH_AUTH = as_json["twitch_auth"]

reddit = praw.Reddit(
    client_id=REDDIT_AUTH["client_id"],
    client_secret=REDDIT_AUTH["client_secret"],
    username=REDDIT_AUTH["username"],
    password=REDDIT_AUTH["password"],
    user_agent=REDDIT_AUTH["user_agent"]
)

twitch = TwitchClient(client_id=TWITCH_AUTH["client_id"])
