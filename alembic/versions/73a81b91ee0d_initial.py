"""initial

Revision ID: 73a81b91ee0d
Revises:
Create Date: 2018-04-25 21:33:13.841514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "73a81b91ee0d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "follow",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("guild_id", sa.BigInteger),
        sa.Column("sub_name", sa.String(30)),
        sa.Column("follows", sa.String(30), nullable=False),
    )
    op.create_table(
        "updatechannel",
        sa.Column("guild_id", sa.BigInteger, primary_key=True),
        sa.Column("channel_id", sa.BigInteger, primary_key=True),
    )
    op.create_table(
        "drmapping",
        sa.Column("discord_id", sa.BigInteger, primary_key=True),
        sa.Column("reddit_name", sa.String(30), primary_key=True),
    )
    op.create_table(
        "sidebartemplate",
        sa.Column("subreddit", sa.String(30), primary_key=True),
        sa.Column("template", sa.String(10_240), nullable=False),
    )


def downgrade():
    op.drop_table("follow")
    op.drop_table("updatechannel")
    op.drop_table("drmapping")
    op.drop_table("sidebartemplate")
