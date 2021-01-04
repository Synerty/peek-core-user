"""Removed string limits

Peek Plugin Database Migration Script

Revision ID: 3fd59734e444
Revises: 45c62f8acd87
Create Date: 2019-06-07 09:42:17.692382

"""

# revision identifiers, used by Alembic.
revision = "3fd59734e444"
down_revision = "45c62f8acd87"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "idx_InternalUserPassword_userId",
        "InternalUserPassword",
        ["userId"],
        unique=True,
        schema="core_user",
    )
    # ### end Alembic commands ###

    op.alter_column(
        "InternalGroup",
        "groupName",
        type_=sa.String(),
        nullable=False,
        schema="core_user",
    )
    op.alter_column(
        "InternalGroup",
        "importHash",
        type_=sa.String(),
        nullable=True,
        schema="core_user",
    )

    op.alter_column(
        "InternalUserPassword",
        "password",
        type_=sa.String(),
        nullable=False,
        schema="core_user",
    )

    op.alter_column(
        "InternalUser",
        "userName",
        type_=sa.String(),
        nullable=False,
        schema="core_user",
    )
    op.alter_column(
        "InternalUser",
        "userTitle",
        type_=sa.String(),
        nullable=False,
        schema="core_user",
    )
    op.alter_column(
        "InternalUser",
        "userUuid",
        type_=sa.String(),
        nullable=False,
        schema="core_user",
    )
    op.alter_column(
        "InternalUser",
        "importHash",
        type_=sa.String(),
        nullable=True,
        schema="core_user",
    )
    op.alter_column(
        "InternalUser", "mobile", type_=sa.String(), nullable=True, schema="core_user"
    )
    op.alter_column(
        "InternalUser", "email", type_=sa.String(), nullable=True, schema="core_user"
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "idx_InternalUserPassword_userId",
        table_name="InternalUserPassword",
        schema="core_user",
    )
    # ### end Alembic commands ###
