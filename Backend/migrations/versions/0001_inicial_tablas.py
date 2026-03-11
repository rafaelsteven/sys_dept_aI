"""Creación inicial de tablas: proyectos, agentes, mensajes

Revision ID: 0001
Revises:
Create Date: 2026-03-10

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Tabla: proyectos ---
    op.create_table(
        "proyectos",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False),
        sa.Column("prompt_inicial", sa.Text(), nullable=False),
        sa.Column("fecha_creacion", sa.DateTime(), nullable=True),
        sa.Column(
            "estado",
            sa.Enum(
                "creando", "analizando", "activo", "pausado", "completado",
                name="estadoproyecto",
            ),
            nullable=True,
        ),
        sa.Column("texto_pdf", sa.Text(), nullable=True),
        sa.Column("archivos_pdf", sa.JSON(), nullable=True),
        sa.Column("archivos_imagen", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_proyectos_fecha_creacion", "proyectos", ["fecha_creacion"])

    # --- Tabla: agentes ---
    op.create_table(
        "agentes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("proyecto_id", sa.String(), nullable=False),
        sa.Column(
            "rol",
            sa.Enum(
                "lider", "arquitecto", "backend", "frontend", "qa", "dba",
                name="rolagente",
            ),
            nullable=False,
        ),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("especialidad", sa.String(500), nullable=True),
        sa.Column(
            "estado",
            sa.Enum(
                "activo", "pensando", "inactivo", "error",
                name="estadoagente",
            ),
            nullable=True,
        ),
        sa.Column("fecha_incorporacion", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["proyecto_id"], ["proyectos.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_agentes_proyecto_id", "agentes", ["proyecto_id"])

    # --- Tabla: mensajes ---
    op.create_table(
        "mensajes",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("proyecto_id", sa.String(), nullable=False),
        sa.Column(
            "canal",
            sa.Enum(
                "general", "arquitectura", "backend", "frontend", "qa", "directo",
                name="canalcomunicacion",
            ),
            nullable=False,
        ),
        sa.Column("agente_origen", sa.String(50), nullable=False),
        sa.Column("agente_destino", sa.String(50), nullable=False),
        sa.Column(
            "etiqueta",
            sa.Enum(
                "PREGUNTA", "APROBACION", "SEGURIDAD", "ACTUALIZACION",
                "BUG", "OK", "TAREA", "SISTEMA",
                name="etiquetamensaje",
            ),
            nullable=False,
        ),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("marca_tiempo", sa.DateTime(), nullable=True),
        sa.Column("es_typing", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["proyecto_id"], ["proyectos.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_mensajes_proyecto_id", "mensajes", ["proyecto_id"])
    op.create_index("ix_mensajes_canal", "mensajes", ["canal"])
    op.create_index("ix_mensajes_marca_tiempo", "mensajes", ["marca_tiempo"])
    # Índice compuesto para filtrar por proyecto + canal (query más frecuente)
    op.create_index(
        "ix_mensajes_proyecto_canal",
        "mensajes",
        ["proyecto_id", "canal"],
    )


def downgrade() -> None:
    op.drop_table("mensajes")
    op.drop_table("agentes")
    op.drop_table("proyectos")

    # Eliminar los tipos ENUM de PostgreSQL
    op.execute("DROP TYPE IF EXISTS etiquetamensaje")
    op.execute("DROP TYPE IF EXISTS canalcomunicacion")
    op.execute("DROP TYPE IF EXISTS estadoagente")
    op.execute("DROP TYPE IF EXISTS rolagente")
    op.execute("DROP TYPE IF EXISTS estadoproyecto")
