"""
Contains the definition for the
Discord Bot which is used as a
simpler frontend to the Reddit
bot for easier configuration.
"""

from discord.ext import commands


DESCRIPTION = "Hello! I am a bot made by Volcyy#2359"


class NerodiaDiscordBot(commands.AutoShardedBot):
    def __init__(self, token: str):
        super().__init__(
            command_prefix=commands.when_mentioned_or("n!"),
            description=DESCRIPTION,
            pm_help=True
        )
        self._token = token

    async def on_ready(self):
        print("[DISCORD] Logged in.")
        print(f"ID: {self.user.id}")
        print(f"Total: {len(self.guilds)} Guilds, {len(self.users)} users.")
        print("Invite Link:\n"
              f"https://discordapp.com/oauth2/authorize?&client_id={self.user.id}&scope=bot")

    def run(self):
        super().run(self._token)
