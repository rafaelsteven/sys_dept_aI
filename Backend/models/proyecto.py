from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class EstadoProyecto(str, Enum):
    CREANDO = "creando"
    ANALIZANDO = "analizando"
    ACTIVO = "activo"
    PAUSADO = "pausado"
    COMPLETADO = "completado"


class Proyecto(BaseModel):
    id: str
    nombre: str
    descripcion: str
    prompt_inicial: str
    fecha_creacion: datetime
    estado: EstadoProyecto = EstadoProyecto.CREANDO
    texto_pdf: str | None = None
    archivos_pdf: list[str] = []
    archivos_imagen: list[str] = []
    url_repositorio: str | None = None
    rama_desarrollo: str | None = None

    class Config:
        from_attributes = True


class EstadoCommit(str, Enum):
    PENDIENTE = "pendiente"
    EN_REVISION_QA = "en_revision_qa"
    APROBADO_QA = "aprobado_qa"
    RECHAZADO_QA = "rechazado_qa"
    APROBADO_LIDER = "aprobado_lider"
    RECHAZADO_LIDER = "rechazado_lider"
    COMMITEADO = "commiteado"
    ERROR = "error"


class ArchivoCommit(BaseModel):
    ruta: str        # ruta relativa dentro del repo, ej: "src/api/usuarios.py"
    contenido: str   # contenido completo del archivo


class CommitPendiente(BaseModel):
    id: str
    proyecto_id: str
    descripcion: str
    archivos: list[ArchivoCommit]
    estado: EstadoCommit = EstadoCommit.PENDIENTE
    revision_qa: str | None = None
    revision_lider: str | None = None
    hash_commit: str | None = None
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class DatosNuevoProyecto(BaseModel):
    nombre: str
    descripcion: str
    prompt_inicial: str


class RespuestaProyecto(BaseModel):
    proyecto: Proyecto
    mensaje: str
