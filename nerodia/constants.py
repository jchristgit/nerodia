"""
Contains various constants that
are used in the various cogs,
mainly embeds that are sent when
various errors occur, for example
with the discord <=> reddit
connection authentication, or
for various other issues.
"""

from .clients import reddit

BOT_REDDIT_NAME = reddit.user.me()

PM_URL = "https://www.reddit.com/message/compose?to=Botyy&subject=verification&message="

# The timeout for the reddit verification, in minutes
VERIFY_TIMEOUT = 5
