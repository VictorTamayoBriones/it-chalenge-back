"""1 Generando nueva estructura de la bd.

Revision ID: 2a5919e074f5
Revises: 
Create Date: 2023-02-13 00:07:48.356186

"""
from alembic import op
from app import models
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a5919e074f5"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Commands auto generated by Alembic - please adjust!."""
    op.create_table(
        "modules",
        sa.Column("id", models.enable_uuid.BinaryUUID(length=16), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=250), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column(
            "created_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.Column(
            "updated_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_modules_name"), "modules", ["name"], unique=False)
    op.create_table(
        "roles",
        sa.Column("id", models.enable_uuid.BinaryUUID(length=16), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=250), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column(
            "created_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.Column(
            "updated_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=False)
    op.create_table(
        "actions",
        sa.Column("id", models.enable_uuid.BinaryUUID(length=16), nullable=False),
        sa.Column("action_name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=250), nullable=True),
        sa.Column("module_id", models.enable_uuid.BinaryUUID(length=16), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column(
            "created_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.Column(
            "updated_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["module_id"],
            ["modules.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_actions_action_name"), "actions", ["action_name"], unique=False
    )
    op.create_table(
        "users",
        sa.Column("id", models.enable_uuid.BinaryUUID(length=16), nullable=False),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("password", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("role_id", models.enable_uuid.BinaryUUID(length=16), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column(
            "created_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.Column(
            "updated_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_table(
        "role_actions",
        sa.Column("id", models.enable_uuid.BinaryUUID(length=16), nullable=False),
        sa.Column("role_id", models.enable_uuid.BinaryUUID(length=16), nullable=True),
        sa.Column(
            "actions_id", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.Column("description", sa.String(length=250), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), nullable=True),
        sa.Column("created_on", sa.DateTime(), nullable=False),
        sa.Column(
            "created_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.Column("updated_on", sa.DateTime(), nullable=True),
        sa.Column(
            "updated_by", models.enable_uuid.BinaryUUID(length=16), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["actions_id"],
            ["actions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Commands auto generated by Alembic - please adjust!."""
    op.drop_table("role_actions")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_actions_action_name"), table_name="actions")
    op.drop_table("actions")
    op.drop_index(op.f("ix_roles_name"), table_name="roles")
    op.drop_table("roles")
    op.drop_index(op.f("ix_modules_name"), table_name="modules")
    op.drop_table("modules")
    # ### end Alembic commands ###
