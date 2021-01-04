"""Added vehical to LoggedIn

Peek Plugin Database Migration Script

Revision ID: 45c62f8acd87
Revises: 2c6728ebc562
Create Date: 2018-12-08 19:21:47.019204

"""

# revision identifiers, used by Alembic.
revision = "45c62f8acd87"
down_revision = "2c6728ebc562"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "UserLoggedIn",
        sa.Column("vehicle", sa.String(), nullable=True),
        schema="core_user",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("UserLoggedIn", "vehicle", schema="core_user")
    # ### end Alembic commands ###
