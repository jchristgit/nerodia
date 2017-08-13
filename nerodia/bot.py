"""
Contains the definition for the
Discord Bot which is used as a
simpler frontend to the Reddit
bot for easier configuration.
"""

from discord.ext import commands


DESCRIPTION = (
    "Hello! I am a bot made by Volcyy#2359 to be used as a frontend to the Reddit Bot "
    "/u/Botyy. The Reddit Bot is made to update the sidebar of a subreddit when one "
    "of many streams that a subreddit's moderators can follow goes online or offline.\n\n"
    "Please note that since it is not possible for bots to read any connected "
    "accounts from your Discord profile, it is necesary to manually verify your "
    "reddit identity - this has nothing to do with your connection to Reddit on Discord.\n\n"
    "Nerodia isn't endorsed by Discord, Reddit or Twitch and does not "
    "reflect the views or opinions of Discord, Reddit or Twitch."
)


class NerodiaDiscordBot(commands.AutoShardedBot):
    def __init__(self, token: str):
        super().__init__(
            command_prefix=commands.when_mentioned_or("n!"),
            description=DESCRIPTION,
            pm_help=True
        )
        self.load_extension("nerodia.cog")
        self._token = token

    async def on_ready(self):
        print("[DISCORD] Logged in.")
        print(f"ID: {self.user.id}")
        print(f"Total: {len(self.guilds)} Guilds, {len(self.users)} users.")
        print("Invite Link:\n"
              f"https://discordapp.com/oauth2/authorize?&client_id={self.user.id}&scope=bot")

    def run(self):
        super().run(self._token)
