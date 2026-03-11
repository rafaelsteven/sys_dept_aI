"""
Entorno de Alembic con soporte para SQLAlchemy async (asyncpg).
Lee la DATABASE_URL desde la configuración del proyecto.
"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Importamos Base y todos los modelos para que Alembic los detecte
from db.base_datos import Base  # noqa: F401 — necesario para que metadata tenga las tablas
import models.proyecto  # noqa: F401
import models.agente    # noqa: F401
import models.mensaje   # noqa: F401

from core.configuracion import configuracion

# Configuración de logging desde alembic.ini
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de todos los modelos — Alembic la usa para autogenerar migraciones
target_metadata = Base.metadata

# Sobreescribir la URL desde configuracion.py (nunca desde alembic.ini)
config.set_main_option("sqlalchemy.url", configuracion.database_url)


def correr_migraciones_offline() -> None:
    """
    Modo offline: genera SQL sin conectarse a la DB.
    Útil para revisar los scripts antes de aplicarlos.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def ejecutar_migraciones(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def correr_migraciones_online() -> None:
    """
    Modo online: se conecta a la DB y aplica las migraciones.
    Usa engine async para compatibilidad con asyncpg.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(ejecutar_migraciones)

    await connectable.dispose()


if context.is_offline_mode():
    correr_migraciones_offline()
else:
    asyncio.run(correr_migraciones_online())
