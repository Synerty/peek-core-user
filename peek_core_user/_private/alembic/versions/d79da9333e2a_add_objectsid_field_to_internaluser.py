"""Add objectSid field to InternalUser

Peek Plugin Database Migration Script

Revision ID: d79da9333e2a
Revises: 43df0e05c728
Create Date: 2022-07-26 15:24:24.408496

"""

# revision identifiers, used by Alembic.
revision = "d79da9333e2a"
down_revision = "43df0e05c728"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    op.add_column(
        "InternalUser",
        sa.Column(
            "objectSid",
            sa.String(),
            unique=True,
            nullable=True,
        ),
        "core_user",
    )

    op.execute(
        """
        UPDATE core_user."InternalUser"
        SET "objectSid" = NULL;
        """
    )


def downgrade():
    op.drop_column("InternalUser", "objectSid", "core_user")
