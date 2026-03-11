from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, DateTime, Text, Enum as SAEnum, Boolean, JSON
from datetime import datetime
import uuid
from core.configuracion import configuracion
from models.agente import RolAgente, EstadoAgente
from models.mensaje import CanalComunicacion, EtiquetaMensaje
from models.proyecto import EstadoProyecto


motor = create_async_engine(
    configuracion.database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
)

FabricaSession = async_sessionmaker(
    bind=motor,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


class ProyectoTabla(Base):
    __tablename__ = "proyectos"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    prompt_inicial = Column(Text, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    estado = Column(SAEnum(EstadoProyecto), default=EstadoProyecto.CREANDO)
    texto_pdf = Column(Text, nullable=True)
    archivos_pdf = Column(JSON, default=list)
    archivos_imagen = Column(JSON, default=list)


class AgenteTabla(Base):
    __tablename__ = "agentes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    proyecto_id = Column(String, nullable=False)
    rol = Column(SAEnum(RolAgente), nullable=False)
    nombre = Column(String(255), nullable=False)
    especialidad = Column(String(500), nullable=True)
    estado = Column(SAEnum(EstadoAgente), default=EstadoAgente.INACTIVO)
    fecha_incorporacion = Column(DateTime, default=datetime.utcnow)


class MensajeTabla(Base):
    __tablename__ = "mensajes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    proyecto_id = Column(String, nullable=False)
    canal = Column(SAEnum(CanalComunicacion), nullable=False)
    agente_origen = Column(String(50), nullable=False)
    agente_destino = Column(String(50), nullable=False)
    etiqueta = Column(SAEnum(EtiquetaMensaje), nullable=False)
    contenido = Column(Text, nullable=False)
    marca_tiempo = Column(DateTime, default=datetime.utcnow)
    es_typing = Column(Boolean, default=False)


async def crear_tablas():
    async with motor.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def obtener_session():
    async with FabricaSession() as session:
        yield session
