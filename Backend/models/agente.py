from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class RolAgente(str, Enum):
    LIDER = "lider"
    ARQUITECTO = "arquitecto"
    BACKEND = "backend"
    FRONTEND = "frontend"
    QA = "qa"
    DBA = "dba"


class EstadoAgente(str, Enum):
    ACTIVO = "activo"
    PENSANDO = "pensando"
    INACTIVO = "inactivo"
    ERROR = "error"


class Agente(BaseModel):
    id: str
    proyecto_id: str
    rol: RolAgente
    nombre: str
    especialidad: str | None = None
    estado: EstadoAgente = EstadoAgente.INACTIVO
    fecha_incorporacion: datetime

    class Config:
        from_attributes = True


class DatosNuevoAgente(BaseModel):
    rol: RolAgente
    nombre: str
    especialidad: str | None = None


class RespuestaAgente(BaseModel):
    agente: Agente
    mensaje: str | None = None
