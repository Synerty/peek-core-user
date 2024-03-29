"""Added settings table

Peek Plugin Database Migration Script

Revision ID: 3a9cddaf05e5
Revises: 0498d92479c8
Create Date: 2017-10-14 14:58:46.523021

"""

# revision identifiers, used by Alembic.
revision = "3a9cddaf05e5"
down_revision = "0498d92479c8"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "Setting",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="core_user",
    )
    op.create_table(
        "SettingProperty",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("settingId", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=50), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=True),
        sa.Column("int_value", sa.Integer(), nullable=True),
        sa.Column("char_value", sa.String(), nullable=True),
        sa.Column("boolean_value", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["settingId"],
            ["core_user.Setting.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="core_user",
    )
    op.drop_index(
        "idx_InternalUserGroup_map", table_name="InternalUserGroup", schema="core_user"
    )
    op.create_index(
        "idx_SettingProperty_settingId",
        "SettingProperty",
        ["settingId"],
        unique=False,
        schema="core_user",
    )
    op.create_index(
        "idx_InternalUserGroup_map",
        "InternalUserGroup",
        ["userId", "groupId"],
        unique=True,
        schema="core_user",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        "idx_InternalUserGroup_map", table_name="InternalUserGroup", schema="core_user"
    )
    op.drop_index(
        "idx_SettingProperty_settingId",
        table_name="SettingProperty",
        schema="core_user",
    )
    op.drop_table("SettingProperty", schema="core_user")
    op.drop_table("Setting", schema="core_user")
    op.create_index(
        "idx_InternalUserGroup_map",
        "InternalUserGroup",
        ["userId", "groupId"],
        unique=True,
        schema="core_user",
    )
    # ### end Alembic commands ###
