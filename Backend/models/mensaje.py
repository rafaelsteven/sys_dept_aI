from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from .agente import RolAgente


class CanalComunicacion(str, Enum):
    GENERAL = "general"
    ARQUITECTURA = "arquitectura"
    BACKEND = "backend"
    FRONTEND = "frontend"
    QA = "qa"
    DIRECTO = "directo"


class EtiquetaMensaje(str, Enum):
    PREGUNTA = "PREGUNTA"
    APROBACION = "APROBACION"
    SEGURIDAD = "SEGURIDAD"
    ACTUALIZACION = "ACTUALIZACION"
    BUG = "BUG"
    OK = "OK"
    TAREA = "TAREA"
    SISTEMA = "SISTEMA"


class Mensaje(BaseModel):
    id: str
    proyecto_id: str
    canal: CanalComunicacion
    agente_origen: str  # RolAgente o "sistema"
    agente_destino: str  # RolAgente o "todos"
    etiqueta: EtiquetaMensaje
    contenido: str
    marca_tiempo: datetime
    es_typing: bool = False

    class Config:
        from_attributes = True


class EventoWebSocket(BaseModel):
    tipo: str  # "mensaje" | "typing" | "estado_agente" | "proyecto_listo"
    datos: dict
