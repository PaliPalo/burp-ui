"""user prefs

Revision ID: 56de018f4d88
Revises: fc07e3fa0086
Create Date: 2017-02-12 14:51:38.147422

"""

# revision identifiers, used by Alembic.
revision = "56de018f4d88"
down_revision = "fc07e3fa0086"

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pref",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user", sa.String(length=256), nullable=True),
        sa.Column("key", sa.String(length=256), nullable=False),
        sa.Column("value", sa.String(length=256), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("pref")
    ### end Alembic commands ###
