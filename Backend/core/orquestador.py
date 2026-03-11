"""
Orquestador: cerebro del sistema.
Gestiona el flujo de conversación entre agentes y la transmisión por WebSocket.

Responsabilidades:
- Recibir una tarea y pasarla al Líder
- Encadenar respuestas entre agentes según palabras clave
- Broadcastear mensajes por WebSocket
- Persistir conversaciones en la DB
"""
import asyncio
import uuid
from datetime import datetime

from agents.agente_base import AgenteBase
from agents import crear_agente_instancia
from core.bus_mensajes import bus_mensajes
from core.configuracion import configuracion
from core.errores import ProyectoNoEncontrado
from db.base_datos import FabricaSession
from db.repositorio import RepositorioMensaje, RepositorioAgente, RepositorioProyecto, RepositorioCommitPendiente
from models.agente import RolAgente, EstadoAgente, Agente
from models.mensaje import CanalComunicacion, EtiquetaMensaje, Mensaje
from models.proyecto import Proyecto, EstadoProyecto, CommitPendiente, EstadoCommit, ArchivoCommit
from servicios import gestor_repositorio


# Keywords para encadenar agentes automáticamente
KEYWORDS_DBA = ["base de datos", "esquema", "tabla", "índice", "migración", "query", "bd"]
KEYWORDS_FRONTEND = ["endpoint", "api", "ruta", "respuesta json", "contrato"]
KEYWORDS_SEGURIDAD = ["seguridad", "vulnerabilidad", "xss", "csrf", "sql injection", "autenticación"]
KEYWORDS_QA = ["test", "prueba", "bug", "error", "caso de uso"]


class Orquestador:
    def __init__(self):
        # proyecto_id -> instancias de agentes activos
        self._equipos: dict[str, dict[str, AgenteBase]] = {}

    async def iniciar_proyecto(self, proyecto: Proyecto) -> None:
        """
        Crea el equipo base (Líder + Arquitecto) y lanza el análisis inicial.
        """
        async with FabricaSession() as session:
            repo_agente = RepositorioAgente(session)
            repo_proyecto = RepositorioProyecto(session)

            # Crear Líder y Arquitecto en DB si no existen
            agentes_existentes = await repo_agente.listar_por_proyecto(proyecto.id)
            roles_existentes = {a.rol for a in agentes_existentes}

            if RolAgente.LIDER not in roles_existentes:
                lider = Agente(
                    id=str(uuid.uuid4()),
                    proyecto_id=proyecto.id,
                    rol=RolAgente.LIDER,
                    nombre="Carlos López",
                    estado=EstadoAgente.ACTIVO,
                    fecha_incorporacion=datetime.utcnow(),
                )
                await repo_agente.guardar(lider)
                agentes_existentes.append(lider)

            if RolAgente.ARQUITECTO not in roles_existentes:
                arquitecto = Agente(
                    id=str(uuid.uuid4()),
                    proyecto_id=proyecto.id,
                    rol=RolAgente.ARQUITECTO,
                    nombre="Ana Reyes",
                    estado=EstadoAgente.ACTIVO,
                    fecha_incorporacion=datetime.utcnow(),
                )
                await repo_agente.guardar(arquitecto)
                agentes_existentes.append(arquitecto)

            # Actualizar estado del proyecto
            await repo_proyecto.actualizar_estado(proyecto.id, EstadoProyecto.ANALIZANDO)

        # Lanzar análisis inicial en background
        asyncio.create_task(self._ejecutar_analisis_inicial(proyecto))

    async def incorporar_agente(self, proyecto_id: str, agente: Agente) -> None:
        """
        Incorpora un nuevo agente al equipo y hace el briefing automático.
        """
        instancia = crear_agente_instancia(agente)
        if proyecto_id not in self._equipos:
            self._equipos[proyecto_id] = {}
        self._equipos[proyecto_id][agente.rol.value] = instancia

        asyncio.create_task(self._briefing_nuevo_miembro(proyecto_id, agente))

    async def procesar_tarea(
        self,
        proyecto_id: str,
        tarea: str,
        agente_destino: str | None = None,
    ) -> None:
        """
        El usuario envía una tarea. Va al Líder (o agente específico) para procesarla.
        """
        asyncio.create_task(
            self._ejecutar_tarea(proyecto_id, tarea, agente_destino)
        )

    async def _ejecutar_analisis_inicial(self, proyecto: Proyecto) -> None:
        """
        Conversación de análisis entre Líder y Arquitecto.
        Flujo: N turnos en canal #arquitectura, luego plan al #general.
        """
        proyecto_id = proyecto.id
        await bus_mensajes.publicar_sistema(
            proyecto_id, "Iniciando análisis del proyecto con el equipo de liderazgo..."
        )

        # Construir contexto del proyecto
        contexto = self._construir_contexto_proyecto(proyecto)

        # Obtener agentes de la DB
        async with FabricaSession() as session:
            repo_agente = RepositorioAgente(session)
            agentes_db = await repo_agente.listar_por_proyecto(proyecto_id)

        instancias = {}
        for agente_db in agentes_db:
            instancias[agente_db.rol.value] = crear_agente_instancia(agente_db)

        lider = instancias.get(RolAgente.LIDER.value)
        arquitecto = instancias.get(RolAgente.ARQUITECTO.value)

        if not lider or not arquitecto:
            await bus_mensajes.publicar_sistema(proyecto_id, "Error: no se encontraron Líder y Arquitecto")
            return

        # Guardar instancias activas
        if proyecto_id not in self._equipos:
            self._equipos[proyecto_id] = {}
        self._equipos[proyecto_id].update(instancias)

        # Mensaje inicial del Líder al Arquitecto
        prompt_inicial_lider = f"""
Tenemos un nuevo proyecto que analizar. Aquí está la información:

{contexto}

Ana, necesito tu análisis arquitectónico. ¿Qué ves de riesgos, qué tecnologías propones y cómo estructurarías esto?
"""

        for turno in range(configuracion.turnos_analisis_inicial):
            # Turno del Líder (turnos pares) o Arquitecto (turnos impares)
            if turno % 2 == 0:
                agente_actual = lider
                destino_rol = RolAgente.ARQUITECTO.value
            else:
                agente_actual = arquitecto
                destino_rol = RolAgente.LIDER.value

            canal = CanalComunicacion.ARQUITECTURA
            mensaje_entrada = prompt_inicial_lider if turno == 0 else "Continúa el análisis basándote en lo anterior."

            # Indicar que está pensando
            agente_actual.actualizar_estado(EstadoAgente.PENSANDO)
            await bus_mensajes.publicar_typing(proyecto_id, agente_actual.rol.value, canal, True)

            try:
                respuesta = await agente_actual.pensar(mensaje_entrada, contexto)
                agente_actual.actualizar_estado(EstadoAgente.ACTIVO)
                await bus_mensajes.publicar_typing(proyecto_id, agente_actual.rol.value, canal, False)

                mensaje = agente_actual.construir_mensaje(
                    proyecto_id=proyecto_id,
                    contenido=respuesta,
                    canal=canal,
                    agente_destino=destino_rol,
                    etiqueta=EtiquetaMensaje.ACTUALIZACION,
                )
                await self._guardar_y_publicar(mensaje)

            except Exception as e:
                await bus_mensajes.publicar_sistema(
                    proyecto_id, f"Error en análisis: {str(e)}"
                )
                break

            await asyncio.sleep(0.5)

        # Resumen final del Líder al canal general
        await bus_mensajes.publicar_typing(proyecto_id, lider.rol.value, CanalComunicacion.GENERAL, True)
        resumen_prompt = "Basándote en el análisis que acabas de hacer con Ana, escribe un plan resumido para el equipo en #general. Incluye: arquitectura elegida, prioridades, y quién debe hacer qué primero."

        try:
            resumen = await lider.pensar(resumen_prompt)
            await bus_mensajes.publicar_typing(proyecto_id, lider.rol.value, CanalComunicacion.GENERAL, False)

            mensaje_plan = lider.construir_mensaje(
                proyecto_id=proyecto_id,
                contenido=resumen,
                canal=CanalComunicacion.GENERAL,
                agente_destino="todos",
                etiqueta=EtiquetaMensaje.TAREA,
            )
            await self._guardar_y_publicar(mensaje_plan)
        except Exception as e:
            await bus_mensajes.publicar_sistema(proyecto_id, f"Error generando plan: {str(e)}")

        # Actualizar estado del proyecto
        async with FabricaSession() as session:
            repo_proyecto = RepositorioProyecto(session)
            await repo_proyecto.actualizar_estado(proyecto_id, EstadoProyecto.ACTIVO)

        await bus_mensajes.publicar_sistema(proyecto_id, "Analisis completado. El equipo esta listo.")

    async def _briefing_nuevo_miembro(self, proyecto_id: str, agente: Agente) -> None:
        """El Líder hace un briefing al nuevo miembro del equipo."""
        lider = self._equipos.get(proyecto_id, {}).get(RolAgente.LIDER.value)
        if not lider:
            return

        prompt = f"""
Un nuevo miembro acaba de unirse al equipo: {agente.nombre} ({agente.rol.value}).
{f'Especialidad: {agente.especialidad}' if agente.especialidad else ''}

Dale un briefing completo del estado actual del proyecto y asígnale su primera tarea según su rol.
Dirígete directamente a él/ella por nombre.
"""
        await bus_mensajes.publicar_typing(proyecto_id, lider.rol.value, CanalComunicacion.GENERAL, True)
        try:
            briefing = await lider.pensar(prompt)
            await bus_mensajes.publicar_typing(proyecto_id, lider.rol.value, CanalComunicacion.GENERAL, False)
            mensaje = lider.construir_mensaje(
                proyecto_id=proyecto_id,
                contenido=briefing,
                canal=CanalComunicacion.GENERAL,
                agente_destino=agente.rol.value,
                etiqueta=EtiquetaMensaje.TAREA,
            )
            await self._guardar_y_publicar(mensaje)
        except Exception:
            pass

    async def _ejecutar_tarea(
        self,
        proyecto_id: str,
        tarea: str,
        agente_destino_rol: str | None,
    ) -> None:
        """Procesa una tarea enviada por el usuario."""
        equipo = self._equipos.get(proyecto_id, {})

        if agente_destino_rol and agente_destino_rol in equipo:
            agente = equipo[agente_destino_rol]
        else:
            agente = equipo.get(RolAgente.LIDER.value)

        if not agente:
            await bus_mensajes.publicar_sistema(proyecto_id, "No hay agentes activos para procesar la tarea")
            return

        canal = CanalComunicacion.GENERAL
        await bus_mensajes.publicar_typing(proyecto_id, agente.rol.value, canal, True)

        try:
            respuesta = await agente.pensar(tarea)
            await bus_mensajes.publicar_typing(proyecto_id, agente.rol.value, canal, False)

            etiqueta = self._detectar_etiqueta(respuesta)
            mensaje = agente.construir_mensaje(
                proyecto_id=proyecto_id,
                contenido=respuesta,
                canal=canal,
                agente_destino="todos",
                etiqueta=etiqueta,
            )
            await self._guardar_y_publicar(mensaje)

            # Encadenar agentes según keywords
            await self._encadenar_por_keywords(proyecto_id, respuesta, equipo)

        except Exception as e:
            await bus_mensajes.publicar_sistema(proyecto_id, f"Error procesando tarea: {str(e)}")

    async def _encadenar_por_keywords(
        self,
        proyecto_id: str,
        texto: str,
        equipo: dict[str, AgenteBase],
    ) -> None:
        """Activa agentes adicionales si el texto contiene keywords relevantes."""
        texto_lower = texto.lower()

        # Activar DBA si se menciona base de datos
        if any(kw in texto_lower for kw in KEYWORDS_DBA):
            dba = equipo.get(RolAgente.DBA.value)
            if dba:
                await asyncio.sleep(1)
                await bus_mensajes.publicar_typing(proyecto_id, dba.rol.value, CanalComunicacion.BACKEND, True)
                respuesta_dba = await dba.pensar(
                    f"El equipo está discutiendo sobre base de datos. Comparte tu perspectiva como DBA: {texto[:500]}"
                )
                await bus_mensajes.publicar_typing(proyecto_id, dba.rol.value, CanalComunicacion.BACKEND, False)
                mensaje = dba.construir_mensaje(
                    proyecto_id=proyecto_id,
                    contenido=respuesta_dba,
                    canal=CanalComunicacion.BACKEND,
                    agente_destino="todos",
                    etiqueta=EtiquetaMensaje.ACTUALIZACION,
                )
                await self._guardar_y_publicar(mensaje)

    def _detectar_etiqueta(self, texto: str) -> EtiquetaMensaje:
        texto_lower = texto.lower()
        if "seguridad" in texto_lower or "vulnerabilidad" in texto_lower:
            return EtiquetaMensaje.SEGURIDAD
        if "?" in texto:
            return EtiquetaMensaje.PREGUNTA
        if "bug" in texto_lower or "error" in texto_lower:
            return EtiquetaMensaje.BUG
        if "tarea" in texto_lower or "asigno" in texto_lower:
            return EtiquetaMensaje.TAREA
        return EtiquetaMensaje.ACTUALIZACION

    def _construir_contexto_proyecto(self, proyecto: Proyecto) -> str:
        partes = [
            f"NOMBRE: {proyecto.nombre}",
            f"DESCRIPCIÓN: {proyecto.descripcion}",
            f"PROMPT INICIAL:\n{proyecto.prompt_inicial}",
        ]
        if proyecto.texto_pdf:
            partes.append(f"DOCUMENTO ADJUNTO (PDF):\n{proyecto.texto_pdf[:3000]}")
        if proyecto.archivos_imagen:
            partes.append(f"IMÁGENES ADJUNTAS: {', '.join(proyecto.archivos_imagen)}")
        return "\n\n".join(partes)

    async def revisar_y_commitear(
        self,
        proyecto_id: str,
        descripcion: str,
        archivos: list[ArchivoCommit],
    ) -> str:
        """
        Flujo completo de revisión y commit:
        1. QA revisa el código propuesto
        2. Si QA aprueba → Líder da el visto bueno final
        3. Si Líder aprueba → commit + push a la rama dev

        Retorna el ID del CommitPendiente creado.
        """
        commit_id = str(uuid.uuid4())

        # Persistir el commit pendiente
        commit = CommitPendiente(
            id=commit_id,
            proyecto_id=proyecto_id,
            descripcion=descripcion,
            archivos=archivos,
            estado=EstadoCommit.PENDIENTE,
            fecha_creacion=datetime.utcnow(),
        )
        async with FabricaSession() as session:
            repo_commit = RepositorioCommitPendiente(session)
            await repo_commit.guardar(commit)

        asyncio.create_task(self._ejecutar_flujo_commit(commit))
        return commit_id

    async def _ejecutar_flujo_commit(self, commit: CommitPendiente) -> None:
        """Orquesta el flujo QA → Líder → git commit+push."""
        proyecto_id = commit.proyecto_id
        equipo = self._equipos.get(proyecto_id, {})

        qa = equipo.get(RolAgente.QA.value)
        lider = equipo.get(RolAgente.LIDER.value)

        # Construir resumen del código para los agentes
        resumen_archivos = "\n".join(
            f"### {a.ruta}\n```\n{a.contenido[:800]}\n```" for a in commit.archivos
        )
        descripcion_commit = commit.descripcion

        # ── Paso 1: Revisión QA ──────────────────────────────────────────────
        await bus_mensajes.publicar_sistema(
            proyecto_id,
            f"[COMMIT #{commit.id[:8]}] QA iniciando revisión de código...",
        )

        async with FabricaSession() as session:
            await RepositorioCommitPendiente(session).actualizar_estado(
                commit.id, EstadoCommit.EN_REVISION_QA
            )

        if not qa:
            # Sin QA en el equipo, el Líder revisa directamente
            revision_qa = "Sin agente QA en el equipo. El Líder revisará directamente."
            aprobado_qa = True
        else:
            prompt_qa = f"""
Se propone el siguiente commit al repositorio del proyecto.

DESCRIPCIÓN: {descripcion_commit}

ARCHIVOS MODIFICADOS:
{resumen_archivos}

Revisa el código como QA:
- ¿Hay bugs evidentes o riesgos de calidad?
- ¿El código sigue los estándares del proyecto?
- ¿Faltan casos de prueba importantes?

Termina tu revisión con una línea: "APROBADO" o "RECHAZADO" seguido del motivo.
"""
            await bus_mensajes.publicar_typing(proyecto_id, RolAgente.QA.value, CanalComunicacion.QA, True)
            try:
                revision_qa = await qa.pensar(prompt_qa)
            except Exception as e:
                revision_qa = f"Error en revisión QA: {e}"
            await bus_mensajes.publicar_typing(proyecto_id, RolAgente.QA.value, CanalComunicacion.QA, False)

            aprobado_qa = "APROBADO" in revision_qa.upper()

            mensaje_qa = qa.construir_mensaje(
                proyecto_id=proyecto_id,
                contenido=f"**Revisión de commit `{commit.id[:8]}`**\n\n{revision_qa}",
                canal=CanalComunicacion.QA,
                agente_destino=RolAgente.LIDER.value,
                etiqueta=EtiquetaMensaje.APROBACION if aprobado_qa else EtiquetaMensaje.BUG,
            )
            await self._guardar_y_publicar(mensaje_qa)

        nuevo_estado_qa = EstadoCommit.APROBADO_QA if aprobado_qa else EstadoCommit.RECHAZADO_QA
        async with FabricaSession() as session:
            await RepositorioCommitPendiente(session).actualizar_estado(
                commit.id, nuevo_estado_qa, revision_qa=revision_qa
            )

        if not aprobado_qa:
            await bus_mensajes.publicar_sistema(
                proyecto_id,
                f"[COMMIT #{commit.id[:8]}] Rechazado por QA. No se hará commit.",
            )
            return

        # ── Paso 2: Aprobación del Líder ─────────────────────────────────────
        await bus_mensajes.publicar_sistema(
            proyecto_id,
            f"[COMMIT #{commit.id[:8]}] QA aprobó. Esperando visto bueno del Líder...",
        )

        if not lider:
            revision_lider = "Sin Líder en el equipo. Aprobación automática."
            aprobado_lider = True
        else:
            prompt_lider = f"""
El QA ha aprobado el siguiente commit. Necesito tu aprobación final como Líder.

DESCRIPCIÓN: {descripcion_commit}

REVISIÓN QA:
{revision_qa}

ARCHIVOS:
{resumen_archivos}

¿Apruebas este commit para hacer push a la rama de desarrollo?
Responde con "APROBADO" o "RECHAZADO" y tu razonamiento.
"""
            await bus_mensajes.publicar_typing(proyecto_id, RolAgente.LIDER.value, CanalComunicacion.GENERAL, True)
            try:
                revision_lider = await lider.pensar(prompt_lider)
            except Exception as e:
                revision_lider = f"Error en revisión del Líder: {e}"
            await bus_mensajes.publicar_typing(proyecto_id, RolAgente.LIDER.value, CanalComunicacion.GENERAL, False)

            aprobado_lider = "APROBADO" in revision_lider.upper()

            mensaje_lider = lider.construir_mensaje(
                proyecto_id=proyecto_id,
                contenido=f"**Decisión sobre commit `{commit.id[:8]}`**\n\n{revision_lider}",
                canal=CanalComunicacion.GENERAL,
                agente_destino="todos",
                etiqueta=EtiquetaMensaje.APROBACION if aprobado_lider else EtiquetaMensaje.OK,
            )
            await self._guardar_y_publicar(mensaje_lider)

        nuevo_estado_lider = EstadoCommit.APROBADO_LIDER if aprobado_lider else EstadoCommit.RECHAZADO_LIDER
        async with FabricaSession() as session:
            await RepositorioCommitPendiente(session).actualizar_estado(
                commit.id, nuevo_estado_lider, revision_lider=revision_lider
            )

        if not aprobado_lider:
            await bus_mensajes.publicar_sistema(
                proyecto_id,
                f"[COMMIT #{commit.id[:8]}] Rechazado por el Líder. No se hará commit.",
            )
            return

        # ── Paso 3: Commit + Push ────────────────────────────────────────────
        await bus_mensajes.publicar_sistema(
            proyecto_id,
            f"[COMMIT #{commit.id[:8]}] Líder aprobó. Haciendo commit y push...",
        )

        # Obtener datos del proyecto para la rama
        async with FabricaSession() as session:
            repo_proyecto = RepositorioProyecto(session)
            try:
                proyecto = await repo_proyecto.obtener_por_id(proyecto_id)
            except Exception:
                await bus_mensajes.publicar_sistema(proyecto_id, "Error: proyecto no encontrado para el commit")
                return

        if not proyecto.url_repositorio or not proyecto.rama_desarrollo:
            await bus_mensajes.publicar_sistema(
                proyecto_id,
                f"[COMMIT #{commit.id[:8]}] El proyecto no tiene repositorio configurado. Commit omitido.",
            )
            async with FabricaSession() as session:
                await RepositorioCommitPendiente(session).actualizar_estado(
                    commit.id, EstadoCommit.ERROR
                )
            return

        try:
            hash_commit = await gestor_repositorio.escribir_y_commitear(
                proyecto_id=proyecto_id,
                archivos=commit.archivos,
                mensaje_commit=f"{descripcion_commit}\n\nAprobado por: QA + Líder\nCommit ID: {commit.id[:8]}",
                rama=proyecto.rama_desarrollo,
            )
            async with FabricaSession() as session:
                await RepositorioCommitPendiente(session).actualizar_estado(
                    commit.id,
                    EstadoCommit.COMMITEADO,
                    hash_commit=hash_commit,
                )
            await bus_mensajes.publicar_sistema(
                proyecto_id,
                f"[COMMIT #{commit.id[:8]}] Push exitoso a `{proyecto.rama_desarrollo}` — hash: `{hash_commit[:8]}`",
            )
        except Exception as e:
            async with FabricaSession() as session:
                await RepositorioCommitPendiente(session).actualizar_estado(
                    commit.id, EstadoCommit.ERROR
                )
            await bus_mensajes.publicar_sistema(
                proyecto_id,
                f"[COMMIT #{commit.id[:8]}] Error al hacer push: {e}",
            )

    async def _guardar_y_publicar(self, mensaje: Mensaje) -> None:
        async with FabricaSession() as session:
            repo = RepositorioMensaje(session)
            await repo.guardar(mensaje)
        await bus_mensajes.publicar_mensaje(mensaje)


# Singleton global
orquestador = Orquestador()
