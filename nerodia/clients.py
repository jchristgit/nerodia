"""
Initializes various clients
from the authorization data
in the `config.json` file.
"""

from .config import CONFIG
from .twitch import TwitchClient


# reddit = praw.Reddit(
    # client_id=REDDIT_CFG["client_id"],
    # client_secret=REDDIT_CFG["client_secret"],
    # username=REDDIT_CFG["username"],
    # password=REDDIT_CFG["password"],
    # user_agent=REDDIT_CFG["user_agent"],
# )

twitch = TwitchClient(client_id=CONFIG["producers"]["poller"]["client-id"])
