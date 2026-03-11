from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from core.configuracion import configuracion
from routes.proyectos import router as router_proyectos
from routes.agentes import router as router_agentes
from routes.websocket import router as router_websocket


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Las tablas se crean con Alembic: `alembic upgrade head`
    # Solo aseguramos que exista el directorio de uploads
    Path(configuracion.directorio_uploads).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="SysDept AI",
    description="Sistema de departamento de sistemas virtual con agentes de IA",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_proyectos)
app.include_router(router_agentes)
app.include_router(router_websocket)

# Servir uploads estáticos
uploads_dir = Path(configuracion.directorio_uploads)
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
