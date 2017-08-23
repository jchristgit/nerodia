"""
Imports various modules from the cogs
package for easier access from upper
packages, for example for adding
the cogs to the Discord Bot.
"""

from . import cog, constants


def setup(bot):
    """
    Adds all cogs that are inside of this
    package to the given Bot.

    Arguments:
        bot: discord.ext.commands.Bot
            The bot to which the cogs should be added.
    """

    bot.add_cog(cog.Nerodia(bot))
