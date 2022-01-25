"""Make username lower case

Peek Plugin Database Migration Script

Revision ID: b09fe7b3b31b
Revises: 73d65f042834
Create Date: 2022-01-14 13:11:12.040873

"""

# revision identifiers, used by Alembic.
revision = "b09fe7b3b31b"
down_revision = "73d65f042834"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "InternalUser",
        sa.Column(
            "userKey",
            sa.String(length=50),
            unique=True,
            nullable=True,
        ),
        schema="core_user",
    )
    op.execute(
        """
        UPDATE "core_user"."InternalUser" SET "userKey" = LOWER("userName");
        """
    )
    op.alter_column(
        "InternalUser", "userKey", nullable=False, schema="core_user"
    )

    op.add_column(
        "UserLoggedIn",
        sa.Column(
            "userKey",
            sa.String(length=50),
            unique=True,
            nullable=True,
        ),
        schema="core_user",
    )

    op.add_column(
        "UserLoggedIn",
        sa.Column(
            "userUuid",
            sa.String(length=50),
            unique=True,
            nullable=True,
        ),
        schema="core_user",
    )

    op.execute(
        """
        UPDATE "core_user"."UserLoggedIn" SET "userKey" = LOWER("userName");
        """
    )

    op.execute(
        """
        -- delete users that are no longer in `InternalUser` table
        DELETE FROM "core_user"."UserLoggedIn" uli
        WHERE uli."userName" in (
        SELECT uli."userName" FROM "core_user"."UserLoggedIn" uli
            LEFT OUTER JOIN "core_user"."InternalUser" iu
                ON iu."userName" = uli."userName"
            WHERE uli."userName" IS NOT NULL AND iu."userName" IS NULL
        );  

        -- add `userUuid` to logged in users
        UPDATE "core_user"."UserLoggedIn" uli SET "userUuid" = iu."userUuid"
        FROM "core_user"."InternalUser" iu
        WHERE iu."userName" = uli."userName";
        """
    )
    op.alter_column(
        "UserLoggedIn", "userKey", nullable=False, schema="core_user"
    )
    op.alter_column(
        "UserLoggedIn", "userUuid", nullable=False, schema="core_user"
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("InternalUser", "userKey", schema="core_user")
    op.drop_column("UserLoggedIn", "userKey", schema="core_user")
    op.drop_column("UserLoggedIn", "userUuid", schema="core_user")
    # ### end Alembic commands ###
