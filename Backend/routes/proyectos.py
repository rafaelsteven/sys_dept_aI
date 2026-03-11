import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.configuracion import configuracion
from core.errores import ProyectoNoEncontrado, LimiteArchivoExcedido, ExtensionNoPermitida
from core.orquestador import orquestador
from db.base_datos import obtener_session
from db.repositorio import RepositorioProyecto, RepositorioMensaje, RepositorioCommitPendiente
from models.mensaje import CanalComunicacion
from models.proyecto import Proyecto, DatosNuevoProyecto, EstadoProyecto, ArchivoCommit
from servicios import gestor_repositorio

router = APIRouter(prefix="/api/proyectos", tags=["proyectos"])


def _validar_extension_pdf(nombre: str) -> None:
    ext = Path(nombre).suffix.lower()
    if ext not in configuracion.extensiones_pdf_permitidas:
        raise ExtensionNoPermitida(f"Extensión no permitida: {ext}")


def _validar_extension_imagen(nombre: str) -> None:
    ext = Path(nombre).suffix.lower()
    if ext not in configuracion.extensiones_imagen_permitidas:
        raise ExtensionNoPermitida(f"Extensión no permitida: {ext}")


def _validar_tamano(contenido: bytes) -> None:
    limite_bytes = configuracion.tamano_max_archivo_mb * 1024 * 1024
    if len(contenido) > limite_bytes:
        raise LimiteArchivoExcedido(
            f"Archivo excede el límite de {configuracion.tamano_max_archivo_mb}MB"
        )


async def _extraer_texto_pdf(ruta: str) -> str:
    """Extrae texto de un PDF usando pdfplumber."""
    try:
        import pdfplumber
        with pdfplumber.open(ruta) as pdf:
            texto = "\n".join(
                pagina.extract_text() or "" for pagina in pdf.pages
            )
        return texto.strip()
    except Exception as e:
        raise Exception(f"Error extrayendo texto del PDF: {e}")


async def _guardar_archivo(
    contenido: bytes,
    nombre_original: str,
    directorio: Path,
) -> str:
    """Guarda un archivo y retorna su nombre único."""
    ext = Path(nombre_original).suffix.lower()
    nombre_unico = f"{uuid.uuid4()}{ext}"
    ruta = directorio / nombre_unico
    ruta.write_bytes(contenido)
    return nombre_unico


@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_proyecto(
    nombre: str = Form(...),
    descripcion: str = Form(...),
    prompt_inicial: str = Form(...),
    url_repositorio: str | None = Form(default=None),
    pdfs: list[UploadFile] = File(default=[]),
    imagenes: list[UploadFile] = File(default=[]),
    session: AsyncSession = Depends(obtener_session),
):
    proyecto_id = str(uuid.uuid4())

    # Crear directorios de uploads
    dir_base = Path(configuracion.directorio_uploads) / proyecto_id
    dir_docs = dir_base / "docs"
    dir_imgs = dir_base / "images"
    dir_docs.mkdir(parents=True, exist_ok=True)
    dir_imgs.mkdir(parents=True, exist_ok=True)

    # Procesar PDFs
    texto_pdf_total = ""
    archivos_pdf = []
    for pdf in pdfs:
        if not pdf.filename:
            continue
        try:
            _validar_extension_pdf(pdf.filename)
            contenido = await pdf.read()
            _validar_tamano(contenido)
            nombre_guardado = await _guardar_archivo(contenido, pdf.filename, dir_docs)
            archivos_pdf.append(nombre_guardado)
            ruta_completa = str(dir_docs / nombre_guardado)
            texto_extraido = await _extraer_texto_pdf(ruta_completa)
            texto_pdf_total += f"\n\n--- {pdf.filename} ---\n{texto_extraido}"
        except (ExtensionNoPermitida, LimiteArchivoExcedido) as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Procesar imágenes
    archivos_imagen = []
    for imagen in imagenes:
        if not imagen.filename:
            continue
        try:
            _validar_extension_imagen(imagen.filename)
            contenido = await imagen.read()
            _validar_tamano(contenido)
            nombre_guardado = await _guardar_archivo(contenido, imagen.filename, dir_imgs)
            archivos_imagen.append(nombre_guardado)
        except (ExtensionNoPermitida, LimiteArchivoExcedido) as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Determinar rama de desarrollo
    rama = configuracion.rama_desarrollo_default if url_repositorio else None

    # Crear proyecto
    proyecto = Proyecto(
        id=proyecto_id,
        nombre=nombre,
        descripcion=descripcion,
        prompt_inicial=prompt_inicial,
        fecha_creacion=datetime.utcnow(),
        estado=EstadoProyecto.CREANDO,
        texto_pdf=texto_pdf_total.strip() or None,
        archivos_pdf=archivos_pdf,
        archivos_imagen=archivos_imagen,
        url_repositorio=url_repositorio.strip() if url_repositorio else None,
        rama_desarrollo=rama,
    )

    repo = RepositorioProyecto(session)
    await repo.guardar(proyecto)

    # Clonar repositorio en background si se proporcionó URL
    if url_repositorio:
        import asyncio
        asyncio.create_task(
            _clonar_repositorio_background(proyecto_id, url_repositorio.strip(), rama)
        )

    # Lanzar análisis inicial en background
    await orquestador.iniciar_proyecto(proyecto)

    return {"proyecto": proyecto, "mensaje": "Proyecto creado. Iniciando análisis del equipo..."}


async def _clonar_repositorio_background(
    proyecto_id: str, url: str, rama: str
) -> None:
    """Clona el repositorio y notifica por WebSocket."""
    from core.bus_mensajes import bus_mensajes
    try:
        await bus_mensajes.publicar_sistema(
            proyecto_id, f"Clonando repositorio {url}..."
        )
        await gestor_repositorio.clonar_repositorio(url, proyecto_id, rama)
        await bus_mensajes.publicar_sistema(
            proyecto_id,
            f"Repositorio clonado. Rama de desarrollo: `{rama}`",
        )
    except Exception as e:
        await bus_mensajes.publicar_sistema(
            proyecto_id, f"Error al clonar repositorio: {e}"
        )


@router.get("/")
async def listar_proyectos(session: AsyncSession = Depends(obtener_session)):
    repo = RepositorioProyecto(session)
    proyectos = await repo.listar_todos()
    return {"proyectos": proyectos}


@router.get("/{proyecto_id}")
async def obtener_proyecto(
    proyecto_id: str,
    session: AsyncSession = Depends(obtener_session),
):
    repo = RepositorioProyecto(session)
    try:
        proyecto = await repo.obtener_por_id(proyecto_id)
        return {"proyecto": proyecto}
    except ProyectoNoEncontrado:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")


@router.delete("/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_proyecto(
    proyecto_id: str,
    session: AsyncSession = Depends(obtener_session),
):
    repo = RepositorioProyecto(session)
    try:
        await repo.eliminar(proyecto_id)
    except ProyectoNoEncontrado:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")


@router.post("/{proyecto_id}/tarea")
async def enviar_tarea(
    proyecto_id: str,
    tarea: str = Form(...),
    agente_destino: str | None = Form(default=None),
    session: AsyncSession = Depends(obtener_session),
):
    repo = RepositorioProyecto(session)
    try:
        await repo.obtener_por_id(proyecto_id)
    except ProyectoNoEncontrado:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    await orquestador.procesar_tarea(proyecto_id, tarea, agente_destino)
    return {"mensaje": "Tarea enviada al equipo"}


@router.get("/{proyecto_id}/mensajes")
async def obtener_mensajes(
    proyecto_id: str,
    canal: CanalComunicacion | None = None,
    limite: int = 100,
    session: AsyncSession = Depends(obtener_session),
):
    repo = RepositorioMensaje(session)
    mensajes = await repo.listar_por_proyecto(proyecto_id, limite=limite, canal=canal)
    return {"mensajes": mensajes}


from pydantic import BaseModel as _BaseModel


class DatosCodigo(_BaseModel):
    descripcion: str
    archivos: list[ArchivoCommit]


@router.post("/{proyecto_id}/codigo", status_code=status.HTTP_202_ACCEPTED)
async def enviar_codigo_para_revision(
    proyecto_id: str,
    datos: DatosCodigo,
    session: AsyncSession = Depends(obtener_session),
):
    """
    Envía código para el flujo de revisión: QA → Líder → commit+push.
    Retorna inmediatamente; el flujo ocurre en background vía WebSocket.
    """
    repo = RepositorioProyecto(session)
    try:
        await repo.obtener_por_id(proyecto_id)
    except ProyectoNoEncontrado:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    if not datos.archivos:
        raise HTTPException(status_code=400, detail="Debes enviar al menos un archivo")

    commit_id = await orquestador.revisar_y_commitear(
        proyecto_id=proyecto_id,
        descripcion=datos.descripcion,
        archivos=datos.archivos,
    )
    return {
        "commit_id": commit_id,
        "mensaje": "Código enviado a revisión. QA y el Líder lo revisarán por WebSocket.",
    }


@router.get("/{proyecto_id}/commits")
async def listar_commits(
    proyecto_id: str,
    session: AsyncSession = Depends(obtener_session),
):
    """Lista todos los commits pendientes y su estado de aprobación."""
    repo = RepositorioCommitPendiente(session)
    commits = await repo.listar_por_proyecto(proyecto_id)
    return {"commits": commits}
