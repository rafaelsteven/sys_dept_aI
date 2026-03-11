"""
Base abstracta para todos los agentes del sistema.
Principio L (Liskov): cualquier agente puede sustituir a AgenteBase.
Principio O (Abierto/Cerrado): extender, no modificar.
"""
import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime

import anthropic

from core.configuracion import configuracion
from core.errores import AgenteNoDisponible
from models.agente import RolAgente, EstadoAgente, Agente
from models.mensaje import Mensaje, CanalComunicacion, EtiquetaMensaje


class AgenteBase(ABC):
    def __init__(self, agente: Agente):
        self._agente = agente
        self._cliente_anthropic = anthropic.AsyncAnthropic(
            api_key=configuracion.anthropic_api_key
        )
        self._historial: list[dict] = []

    @property
    def id(self) -> str:
        return self._agente.id

    @property
    def nombre(self) -> str:
        return self._agente.nombre

    @property
    def rol(self) -> RolAgente:
        return self._agente.rol

    @property
    def estado(self) -> EstadoAgente:
        return self._agente.estado

    @property
    @abstractmethod
    def prompt_sistema(self) -> str:
        """System prompt con personalidad del agente."""
        ...

    def actualizar_estado(self, estado: EstadoAgente) -> None:
        self._agente = self._agente.model_copy(update={"estado": estado})

    async def pensar(
        self,
        mensaje_usuario: str,
        contexto_extra: str | None = None,
    ) -> str:
        """
        Genera una respuesta del agente usando el modelo configurado.
        Implementa reintentos según configuracion.max_reintentos_agente.
        """
        if self._agente.estado == EstadoAgente.ERROR:
            raise AgenteNoDisponible(f"Agente {self.nombre} en estado de error")

        self._historial.append({"role": "user", "content": mensaje_usuario})

        # Limitamos el historial para no exceder el contexto del modelo
        historial_reciente = self._historial[-configuracion.ventana_historial_mensajes:]

        system = self.prompt_sistema
        if contexto_extra:
            system = f"{system}\n\nCONTEXTO ADICIONAL:\n{contexto_extra}"

        for intento in range(configuracion.max_reintentos_agente + 1):
            try:
                respuesta = await self._cliente_anthropic.messages.create(
                    model=configuracion.modelo_agente,
                    max_tokens=configuracion.max_tokens_agente,
                    system=system,
                    messages=historial_reciente,
                )
                texto = respuesta.content[0].text
                self._historial.append({"role": "assistant", "content": texto})
                return texto
            except Exception as e:
                if intento < configuracion.max_reintentos_agente:
                    await asyncio.sleep(configuracion.segundos_espera_reintento)
                else:
                    self.actualizar_estado(EstadoAgente.ERROR)
                    raise AgenteNoDisponible(
                        f"Agente {self.nombre} falló después de {configuracion.max_reintentos_agente} reintentos: {e}"
                    )

    def construir_mensaje(
        self,
        proyecto_id: str,
        contenido: str,
        canal: CanalComunicacion,
        agente_destino: str,
        etiqueta: EtiquetaMensaje = EtiquetaMensaje.ACTUALIZACION,
    ) -> Mensaje:
        return Mensaje(
            id=str(uuid.uuid4()),
            proyecto_id=proyecto_id,
            canal=canal,
            agente_origen=self.rol.value,
            agente_destino=agente_destino,
            etiqueta=etiqueta,
            contenido=contenido,
            marca_tiempo=datetime.utcnow(),
        )

    def limpiar_historial(self) -> None:
        self._historial = []
