"""handle sessions

Revision ID: 7f317474332d
Revises: 225d9b2f0fb1
Create Date: 2016-08-30 11:47:35.513396

"""

# revision identifiers, used by Alembic.
revision = "7f317474332d"
down_revision = "225d9b2f0fb1"

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "session",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=256), nullable=True),
        sa.Column("user", sa.String(length=256), nullable=True),
        sa.Column("ip", sa.String(length=256), nullable=True),
        sa.Column("ua", sa.String(length=2048), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("expire", sa.DateTime(), nullable=True),
        sa.Column("permanent", sa.Boolean(), nullable=True),
        sa.Column("api", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("session")
    ### end Alembic commands ###
