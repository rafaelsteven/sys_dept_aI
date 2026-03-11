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

    class Config:
        from_attributes = True


class DatosNuevoProyecto(BaseModel):
    nombre: str
    descripcion: str
    prompt_inicial: str


class RespuestaProyecto(BaseModel):
    proyecto: Proyecto
    mensaje: str
