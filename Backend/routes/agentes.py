import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.errores import RolNoPermitido
from core.orquestador import orquestador
from db.base_datos import obtener_session
from db.repositorio import RepositorioAgente
from models.agente import Agente, DatosNuevoAgente, EstadoAgente, RolAgente

router = APIRouter(prefix="/api/proyectos/{proyecto_id}/agentes", tags=["agentes"])

# Roles que no se pueden remover
ROLES_PROTEGIDOS = {RolAgente.LIDER, RolAgente.ARQUITECTO}


@router.get("/")
async def listar_agentes(
    proyecto_id: str,
    session: AsyncSession = Depends(obtener_session),
):
    repo = RepositorioAgente(session)
    agentes = await repo.listar_por_proyecto(proyecto_id)
    return {"agentes": agentes}


@router.post("/", status_code=201)
async def agregar_agente(
    proyecto_id: str,
    datos: DatosNuevoAgente,
    session: AsyncSession = Depends(obtener_session),
):
    agente = Agente(
        id=str(uuid.uuid4()),
        proyecto_id=proyecto_id,
        rol=datos.rol,
        nombre=datos.nombre,
        especialidad=datos.especialidad,
        estado=EstadoAgente.ACTIVO,
        fecha_incorporacion=datetime.utcnow(),
    )

    repo = RepositorioAgente(session)
    await repo.guardar(agente)

    # Incorporar al orquestador y hacer briefing
    await orquestador.incorporar_agente(proyecto_id, agente)

    return {"agente": agente, "mensaje": f"{agente.nombre} se ha unido al equipo"}


@router.delete("/{rol}", status_code=204)
async def remover_agente(
    proyecto_id: str,
    rol: RolAgente,
    session: AsyncSession = Depends(obtener_session),
):
    if rol in ROLES_PROTEGIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"El rol {rol.value} no puede ser removido del equipo",
        )
    repo = RepositorioAgente(session)
    await repo.eliminar(proyecto_id, rol)
