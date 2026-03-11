"""Agrega url_repositorio/rama_desarrollo a proyectos y crea tabla commits_pendientes

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Columnas nuevas en proyectos ---
    op.add_column("proyectos", sa.Column("url_repositorio", sa.String(500), nullable=True))
    op.add_column("proyectos", sa.Column("rama_desarrollo", sa.String(100), nullable=True))

    # --- Tabla: commits_pendientes ---
    op.create_table(
        "commits_pendientes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("proyecto_id", sa.String(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("archivos", sa.JSON(), nullable=False),
        sa.Column(
            "estado",
            sa.Enum(
                "pendiente",
                "en_revision_qa",
                "aprobado_qa",
                "rechazado_qa",
                "aprobado_lider",
                "rechazado_lider",
                "commiteado",
                "error",
                name="estadocommit",
            ),
            nullable=False,
        ),
        sa.Column("revision_qa", sa.Text(), nullable=True),
        sa.Column("revision_lider", sa.Text(), nullable=True),
        sa.Column("hash_commit", sa.String(100), nullable=True),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["proyecto_id"], ["proyectos.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_commits_proyecto_id", "commits_pendientes", ["proyecto_id"])
    op.create_index("ix_commits_estado", "commits_pendientes", ["estado"])
    op.create_index("ix_commits_fecha", "commits_pendientes", ["fecha_creacion"])


def downgrade() -> None:
    op.drop_table("commits_pendientes")
    op.execute("DROP TYPE IF EXISTS estadocommit")
    op.drop_column("proyectos", "rama_desarrollo")
    op.drop_column("proyectos", "url_repositorio")
