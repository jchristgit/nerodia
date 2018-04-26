"""initial

Revision ID: 17850806ed9d
Revises: 
Create Date: 2018-04-26 22:58:43.127593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '17850806ed9d'
down_revision = None
branch_labels = ('discordbot',)
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
