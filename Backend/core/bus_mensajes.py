"""
Bus de mensajes para comunicación en tiempo real.
Gestiona las conexiones WebSocket activas por proyecto.
"""
import asyncio
import json
from datetime import datetime
from typing import Callable
from fastapi import WebSocket

from models.mensaje import Mensaje, EventoWebSocket, CanalComunicacion, EtiquetaMensaje
from models.agente import EstadoAgente


class BusMensajes:
    def __init__(self):
        # proyecto_id -> lista de conexiones WebSocket
        self._conexiones: dict[str, list[WebSocket]] = {}
        # callbacks de guardado de mensajes
        self._manejadores_guardado: list[Callable] = []

    async def conectar(self, proyecto_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if proyecto_id not in self._conexiones:
            self._conexiones[proyecto_id] = []
        self._conexiones[proyecto_id].append(websocket)

    async def desconectar(self, proyecto_id: str, websocket: WebSocket) -> None:
        if proyecto_id in self._conexiones:
            self._conexiones[proyecto_id].remove(websocket)

    async def publicar_mensaje(self, mensaje: Mensaje) -> None:
        evento = EventoWebSocket(
            tipo="mensaje",
            datos=mensaje.model_dump(mode="json"),
        )
        await self._broadcast(mensaje.proyecto_id, evento)

    async def publicar_typing(
        self,
        proyecto_id: str,
        agente_origen: str,
        canal: CanalComunicacion,
        escribiendo: bool,
    ) -> None:
        evento = EventoWebSocket(
            tipo="typing",
            datos={
                "agente": agente_origen,
                "canal": canal.value,
                "escribiendo": escribiendo,
            },
        )
        await self._broadcast(proyecto_id, evento)

    async def publicar_estado_agente(
        self,
        proyecto_id: str,
        agente_id: str,
        estado: EstadoAgente,
    ) -> None:
        evento = EventoWebSocket(
            tipo="estado_agente",
            datos={"agente_id": agente_id, "estado": estado.value},
        )
        await self._broadcast(proyecto_id, evento)

    async def publicar_sistema(self, proyecto_id: str, texto: str) -> None:
        evento = EventoWebSocket(
            tipo="sistema",
            datos={"texto": texto, "marca_tiempo": datetime.utcnow().isoformat()},
        )
        await self._broadcast(proyecto_id, evento)

    async def _broadcast(self, proyecto_id: str, evento: EventoWebSocket) -> None:
        conexiones = self._conexiones.get(proyecto_id, [])
        payload = evento.model_dump_json()
        desconectados = []
        for ws in conexiones:
            try:
                await ws.send_text(payload)
            except Exception:
                desconectados.append(ws)
        for ws in desconectados:
            await self.desconectar(proyecto_id, ws)


# Singleton global
bus_mensajes = BusMensajes()
