from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from core.bus_mensajes import bus_mensajes

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{proyecto_id}")
async def websocket_proyecto(proyecto_id: str, websocket: WebSocket):
    await bus_mensajes.conectar(proyecto_id, websocket)
    try:
        while True:
            # Mantener la conexión activa; el cliente puede enviar ping
            await websocket.receive_text()
    except WebSocketDisconnect:
        await bus_mensajes.desconectar(proyecto_id, websocket)
