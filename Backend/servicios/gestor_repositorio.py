"""
Servicio de gestión de repositorios Git.

Responsabilidades:
- Clonar el repositorio del proyecto
- Crear la rama de desarrollo
- Escribir archivos y hacer commit+push tras la aprobación del Líder

GitPython es síncrono, por eso todas las operaciones de disco/git
se ejecutan en un ThreadPoolExecutor para no bloquear el event loop.
"""
import asyncio
from pathlib import Path
from functools import partial

import git
from git import Repo, GitCommandError

from core.configuracion import configuracion
from core.errores import SysDeptError
from models.proyecto import ArchivoCommit


class ErrorRepositorio(SysDeptError):
    pass


def _ruta_repo(proyecto_id: str) -> Path:
    return Path(configuracion.directorio_uploads) / proyecto_id / "repo"


# ---------------------------------------------------------------------------
# Operaciones síncronas (se envuelven con run_in_executor)
# ---------------------------------------------------------------------------

def _clonar_sync(url: str, proyecto_id: str, rama: str) -> str:
    """
    Clona el repositorio y crea (o verifica) la rama de desarrollo.
    Retorna la ruta local del clon.
    """
    ruta = _ruta_repo(proyecto_id)
    ruta.mkdir(parents=True, exist_ok=True)

    try:
        repo = Repo.clone_from(url, str(ruta))
    except GitCommandError as e:
        raise ErrorRepositorio(f"No se pudo clonar el repositorio: {e}")

    # Crear la rama de desarrollo si no existe en remoto
    ramas_remotas = [r.name.split("/")[-1] for r in repo.remote().refs]
    if rama in ramas_remotas:
        repo.git.checkout(rama)
    else:
        repo.git.checkout("-b", rama)

    return str(ruta)


def _escribir_y_commitear_sync(
    proyecto_id: str,
    archivos: list[ArchivoCommit],
    mensaje_commit: str,
    rama: str,
) -> str:
    """
    Escribe los archivos en el repo local, hace add+commit y push a la rama.
    Retorna el hash del commit generado.
    """
    ruta_repo = _ruta_repo(proyecto_id)
    if not ruta_repo.exists():
        raise ErrorRepositorio("El repositorio no ha sido clonado para este proyecto")

    repo = Repo(str(ruta_repo))

    # Asegurarse de estar en la rama correcta
    if repo.active_branch.name != rama:
        repo.git.checkout(rama)

    # Escribir cada archivo
    archivos_modificados = []
    for archivo in archivos:
        ruta_archivo = ruta_repo / archivo.ruta
        ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
        ruta_archivo.write_text(archivo.contenido, encoding="utf-8")
        archivos_modificados.append(archivo.ruta)

    if not archivos_modificados:
        raise ErrorRepositorio("No hay archivos para commitear")

    # Configurar autor
    with repo.config_writer() as cfg:
        cfg.set_value("user", "name", configuracion.git_autor_nombre)
        cfg.set_value("user", "email", configuracion.git_autor_email)

    # Stage + commit
    repo.index.add(archivos_modificados)
    commit = repo.index.commit(mensaje_commit)

    # Push a la rama remota
    try:
        repo.remote("origin").push(refspec=f"{rama}:{rama}")
    except GitCommandError as e:
        raise ErrorRepositorio(f"Commit local ok, pero falló el push: {e}")

    return commit.hexsha


def _obtener_diff_sync(proyecto_id: str) -> str:
    """Retorna el diff de los cambios no commiteados (para contexto del QA)."""
    ruta_repo = _ruta_repo(proyecto_id)
    if not ruta_repo.exists():
        return "(repositorio no disponible)"
    repo = Repo(str(ruta_repo))
    diff = repo.git.diff("HEAD")
    return diff or "(sin cambios pendientes)"


# ---------------------------------------------------------------------------
# Interfaz async pública
# ---------------------------------------------------------------------------

async def clonar_repositorio(url: str, proyecto_id: str, rama: str) -> str:
    """Clona el repo en un thread y retorna la ruta local."""
    loop = asyncio.get_event_loop()
    ruta = await loop.run_in_executor(
        None, partial(_clonar_sync, url, proyecto_id, rama)
    )
    return ruta


async def escribir_y_commitear(
    proyecto_id: str,
    archivos: list[ArchivoCommit],
    mensaje_commit: str,
    rama: str,
) -> str:
    """Escribe archivos, hace commit y push. Retorna el hash del commit."""
    loop = asyncio.get_event_loop()
    hash_commit = await loop.run_in_executor(
        None,
        partial(_escribir_y_commitear_sync, proyecto_id, archivos, mensaje_commit, rama),
    )
    return hash_commit


async def obtener_diff(proyecto_id: str) -> str:
    """Retorna el diff actual del repo (para el QA)."""
    loop = asyncio.get_event_loop()
    diff = await loop.run_in_executor(
        None, partial(_obtener_diff_sync, proyecto_id)
    )
    return diff
