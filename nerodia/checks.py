from discord.abc import PrivateChannel


def dm_only(ctx):
    return isinstance(ctx.channel, PrivateChannel)
