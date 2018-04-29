"""initial

Revision ID: 62ac6fa275d4
Revises:
Create Date: 2018-04-29 23:21:36.327262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "62ac6fa275d4"
down_revision = "3eb43612fe5f"
branch_labels = ("discordbot",)
depends_on = None


def upgrade():
    op.create_table(
        "discordbot_follow",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("guild_id", sa.BigInteger, nullable=False),
        sa.Column("follows", sa.String(30), nullable=False),
    )
    op.create_table(
        "discordbot_updatechannel",
        sa.Column("guild_id", sa.BigInteger, primary_key=True),
        sa.Column("channel_id", sa.BigInteger, primary_key=True),
    )


def downgrade():
    op.drop_table("discordbot_follow")
    op.drop_table("discordbot_updatechannel")
