import json


with open("config.json") as f:
    as_json = json.load(f)
    DISCORD_CFG = as_json["discord"]
    REDDIT_CFG = as_json["reddit_auth"]
    TWITCH_CFG = as_json["twitch"]
