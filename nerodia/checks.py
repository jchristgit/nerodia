from discord.abc import PrivateChannel
from discord.ext.commands import Context


def dm_only(ctx: Context):
    """Returns whether the given context is from a private channel.

    Args:
        ctx (Context):
            The context which should be checked.

    Returns:
        bool:
            `True` if the channel is a private channel, `False` otherwise.
    """

    return isinstance(ctx.channel, PrivateChannel)
