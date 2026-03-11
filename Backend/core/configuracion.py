from pydantic_settings import BaseSettings
from pydantic import Field


class Configuracion(BaseSettings):
    # Anthropic
    anthropic_api_key: str
    modelo_agente: str = "claude-sonnet-4-6"
    max_tokens_agente: int = 2000

    # Conversación
    turnos_analisis_inicial: int = 6
    turnos_max_conversacion: int = 8
    ventana_historial_mensajes: int = 20

    # Archivos
    directorio_uploads: str = "./uploads"
    tamano_max_archivo_mb: int = 50
    extensiones_pdf_permitidas: list[str] = [".pdf"]
    extensiones_imagen_permitidas: list[str] = [".png", ".jpg", ".jpeg", ".webp", ".gif"]

    # Servidor
    puerto_api: int = 8000
    origenes_permitidos: list[str] = ["http://localhost:5173"]

    # Base de datos PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/sysdept"

    # Agentes — reintentos
    max_reintentos_agente: int = 2
    segundos_espera_reintento: int = 3

    class Config:
        env_file = ".env"


configuracion = Configuracion()
