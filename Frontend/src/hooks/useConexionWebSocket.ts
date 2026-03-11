import { useEffect, useRef, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { CONFIG } from '../configuracion/api'
import { useAgenteStore } from '../store/agenteStore'
import type { Mensaje } from '../types/Mensaje'

export function useConexionWebSocket(proyectoId: string | undefined) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconectarRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const queryClient = useQueryClient()
  const { establecerTyping } = useAgenteStore()

  const conectar = useCallback(() => {
    if (!proyectoId) return

    const ws = new WebSocket(`${CONFIG.urlWebSocket}/ws/${proyectoId}`)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket conectado')
    }

    ws.onmessage = (evento) => {
      try {
        const datos = JSON.parse(evento.data)

        if (datos.tipo === 'mensaje') {
          const mensaje: Mensaje = {
            id: datos.datos.id,
            proyectoId: datos.datos.proyecto_id,
            canal: datos.datos.canal,
            agenteOrigen: datos.datos.agente_origen,
            agenteDestino: datos.datos.agente_destino,
            etiqueta: datos.datos.etiqueta,
            contenido: datos.datos.contenido,
            marcaTiempo: datos.datos.marca_tiempo,
            esTyping: datos.datos.es_typing ?? false,
          }
          // Actualizar cache de React Query
          queryClient.setQueryData<Mensaje[]>(
            ['mensajes', proyectoId, undefined],
            (anterior) => [...(anterior ?? []), mensaje]
          )
          // Actualizar también el canal específico si corresponde
          queryClient.setQueryData<Mensaje[]>(
            ['mensajes', proyectoId, mensaje.canal],
            (anterior) => [...(anterior ?? []), mensaje]
          )
        } else if (datos.tipo === 'typing') {
          establecerTyping(datos.datos.agente, datos.datos.escribiendo)
        } else if (datos.tipo === 'sistema') {
          const mensajeSistema: Mensaje = {
            id: `sistema-${Date.now()}`,
            proyectoId: proyectoId,
            canal: 'general',
            agenteOrigen: 'sistema',
            agenteDestino: 'todos',
            etiqueta: 'SISTEMA',
            contenido: datos.datos.texto,
            marcaTiempo: datos.datos.marca_tiempo,
            esTyping: false,
          }
          queryClient.setQueryData<Mensaje[]>(
            ['mensajes', proyectoId, undefined],
            (anterior) => [...(anterior ?? []), mensajeSistema]
          )
          queryClient.setQueryData<Mensaje[]>(
            ['mensajes', proyectoId, 'general'],
            (anterior) => [...(anterior ?? []), mensajeSistema]
          )
        }
      } catch {
        // Ignorar mensajes malformados
      }
    }

    ws.onclose = () => {
      // Reconectar automáticamente en 3 segundos
      reconectarRef.current = setTimeout(conectar, 3000)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [proyectoId, queryClient, establecerTyping])

  useEffect(() => {
    conectar()
    return () => {
      if (reconectarRef.current) clearTimeout(reconectarRef.current)
      wsRef.current?.close()
    }
  }, [conectar])
}
