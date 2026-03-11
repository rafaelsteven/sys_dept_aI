from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime
import uuid

from db.base_datos import ProyectoTabla, AgenteTabla, MensajeTabla, CommitPendienteTabla
from models.proyecto import Proyecto, EstadoProyecto, CommitPendiente, EstadoCommit, ArchivoCommit
from models.agente import Agente, RolAgente, EstadoAgente
from models.mensaje import Mensaje, CanalComunicacion, EtiquetaMensaje
from core.errores import ProyectoNoEncontrado


class RepositorioProyecto:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, proyecto: Proyecto) -> Proyecto:
        fila = ProyectoTabla(
            id=proyecto.id,
            nombre=proyecto.nombre,
            descripcion=proyecto.descripcion,
            prompt_inicial=proyecto.prompt_inicial,
            fecha_creacion=proyecto.fecha_creacion,
            estado=proyecto.estado,
            texto_pdf=proyecto.texto_pdf,
            archivos_pdf=proyecto.archivos_pdf,
            archivos_imagen=proyecto.archivos_imagen,
            url_repositorio=proyecto.url_repositorio,
            rama_desarrollo=proyecto.rama_desarrollo,
        )
        self._session.add(fila)
        await self._session.commit()
        return proyecto

    async def obtener_por_id(self, proyecto_id: str) -> Proyecto:
        resultado = await self._session.execute(
            select(ProyectoTabla).where(ProyectoTabla.id == proyecto_id)
        )
        fila = resultado.scalar_one_or_none()
        if not fila:
            raise ProyectoNoEncontrado(f"Proyecto {proyecto_id} no encontrado")
        return self._mapear_proyecto(fila)

    async def listar_todos(self) -> list[Proyecto]:
        resultado = await self._session.execute(
            select(ProyectoTabla).order_by(ProyectoTabla.fecha_creacion.desc())
        )
        return [self._mapear_proyecto(f) for f in resultado.scalars().all()]

    async def actualizar_estado(self, proyecto_id: str, estado: EstadoProyecto) -> None:
        proyecto = await self._session.get(ProyectoTabla, proyecto_id)
        if not proyecto:
            raise ProyectoNoEncontrado(f"Proyecto {proyecto_id} no encontrado")
        proyecto.estado = estado
        await self._session.commit()

    async def eliminar(self, proyecto_id: str) -> None:
        await self._session.execute(
            delete(ProyectoTabla).where(ProyectoTabla.id == proyecto_id)
        )
        await self._session.commit()

    def _mapear_proyecto(self, fila: ProyectoTabla) -> Proyecto:
        return Proyecto(
            id=fila.id,
            nombre=fila.nombre,
            descripcion=fila.descripcion,
            prompt_inicial=fila.prompt_inicial,
            fecha_creacion=fila.fecha_creacion,
            estado=fila.estado,
            texto_pdf=fila.texto_pdf,
            archivos_pdf=fila.archivos_pdf or [],
            archivos_imagen=fila.archivos_imagen or [],
            url_repositorio=fila.url_repositorio,
            rama_desarrollo=fila.rama_desarrollo,
        )


class RepositorioCommitPendiente:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, commit: CommitPendiente) -> CommitPendiente:
        fila = CommitPendienteTabla(
            id=commit.id,
            proyecto_id=commit.proyecto_id,
            descripcion=commit.descripcion,
            archivos=[a.model_dump() for a in commit.archivos],
            estado=commit.estado,
            revision_qa=commit.revision_qa,
            revision_lider=commit.revision_lider,
            hash_commit=commit.hash_commit,
            fecha_creacion=commit.fecha_creacion,
        )
        self._session.add(fila)
        await self._session.commit()
        return commit

    async def actualizar_estado(
        self,
        commit_id: str,
        estado: EstadoCommit,
        revision_qa: str | None = None,
        revision_lider: str | None = None,
        hash_commit: str | None = None,
    ) -> None:
        fila = await self._session.get(CommitPendienteTabla, commit_id)
        if not fila:
            return
        fila.estado = estado
        if revision_qa is not None:
            fila.revision_qa = revision_qa
        if revision_lider is not None:
            fila.revision_lider = revision_lider
        if hash_commit is not None:
            fila.hash_commit = hash_commit
        await self._session.commit()

    async def listar_por_proyecto(self, proyecto_id: str) -> list[CommitPendiente]:
        resultado = await self._session.execute(
            select(CommitPendienteTabla)
            .where(CommitPendienteTabla.proyecto_id == proyecto_id)
            .order_by(CommitPendienteTabla.fecha_creacion.desc())
        )
        return [self._mapear(f) for f in resultado.scalars().all()]

    def _mapear(self, fila: CommitPendienteTabla) -> CommitPendiente:
        return CommitPendiente(
            id=fila.id,
            proyecto_id=fila.proyecto_id,
            descripcion=fila.descripcion,
            archivos=[ArchivoCommit(**a) for a in (fila.archivos or [])],
            estado=fila.estado,
            revision_qa=fila.revision_qa,
            revision_lider=fila.revision_lider,
            hash_commit=fila.hash_commit,
            fecha_creacion=fila.fecha_creacion,
        )


class RepositorioAgente:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, agente: Agente) -> Agente:
        fila = AgenteTabla(
            id=agente.id,
            proyecto_id=agente.proyecto_id,
            rol=agente.rol,
            nombre=agente.nombre,
            especialidad=agente.especialidad,
            estado=agente.estado,
            fecha_incorporacion=agente.fecha_incorporacion,
        )
        self._session.add(fila)
        await self._session.commit()
        return agente

    async def listar_por_proyecto(self, proyecto_id: str) -> list[Agente]:
        resultado = await self._session.execute(
            select(AgenteTabla).where(AgenteTabla.proyecto_id == proyecto_id)
        )
        return [self._mapear_agente(f) for f in resultado.scalars().all()]

    async def actualizar_estado(self, agente_id: str, estado: EstadoAgente) -> None:
        agente = await self._session.get(AgenteTabla, agente_id)
        if agente:
            agente.estado = estado
            await self._session.commit()

    async def eliminar(self, proyecto_id: str, rol: RolAgente) -> None:
        await self._session.execute(
            delete(AgenteTabla).where(
                AgenteTabla.proyecto_id == proyecto_id,
                AgenteTabla.rol == rol,
            )
        )
        await self._session.commit()

    def _mapear_agente(self, fila: AgenteTabla) -> Agente:
        return Agente(
            id=fila.id,
            proyecto_id=fila.proyecto_id,
            rol=fila.rol,
            nombre=fila.nombre,
            especialidad=fila.especialidad,
            estado=fila.estado,
            fecha_incorporacion=fila.fecha_incorporacion,
        )


class RepositorioMensaje:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def guardar(self, mensaje: Mensaje) -> Mensaje:
        fila = MensajeTabla(
            id=mensaje.id,
            proyecto_id=mensaje.proyecto_id,
            canal=mensaje.canal,
            agente_origen=mensaje.agente_origen,
            agente_destino=mensaje.agente_destino,
            etiqueta=mensaje.etiqueta,
            contenido=mensaje.contenido,
            marca_tiempo=mensaje.marca_tiempo,
            es_typing=mensaje.es_typing,
        )
        self._session.add(fila)
        await self._session.commit()
        return mensaje

    async def listar_por_proyecto(
        self,
        proyecto_id: str,
        limite: int = 100,
        canal: CanalComunicacion | None = None,
    ) -> list[Mensaje]:
        consulta = select(MensajeTabla).where(
            MensajeTabla.proyecto_id == proyecto_id,
            MensajeTabla.es_typing == False,
        )
        if canal:
            consulta = consulta.where(MensajeTabla.canal == canal)
        consulta = consulta.order_by(MensajeTabla.marca_tiempo.desc()).limit(limite)
        resultado = await self._session.execute(consulta)
        mensajes = [self._mapear_mensaje(f) for f in resultado.scalars().all()]
        return list(reversed(mensajes))

    def _mapear_mensaje(self, fila: MensajeTabla) -> Mensaje:
        return Mensaje(
            id=fila.id,
            proyecto_id=fila.proyecto_id,
            canal=fila.canal,
            agente_origen=fila.agente_origen,
            agente_destino=fila.agente_destino,
            etiqueta=fila.etiqueta,
            contenido=fila.contenido,
            marca_tiempo=fila.marca_tiempo,
            es_typing=fila.es_typing,
        )
