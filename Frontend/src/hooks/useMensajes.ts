import { useQuery, useMutation } from '@tanstack/react-query'
import { CONFIG } from '../configuracion/api'
import type { Mensaje, CanalComunicacion } from '../types/Mensaje'

const mapearMensaje = (datos: Record<string, unknown>): Mensaje => ({
  id: datos.id as string,
  proyectoId: datos.proyecto_id as string,
  canal: datos.canal as CanalComunicacion,
  agenteOrigen: datos.agente_origen as string,
  agenteDestino: datos.agente_destino as string,
  etiqueta: datos.etiqueta as Mensaje['etiqueta'],
  contenido: datos.contenido as string,
  marcaTiempo: datos.marca_tiempo as string,
  esTyping: (datos.es_typing as boolean) ?? false,
})

export function useMensajes(proyectoId: string, canal?: CanalComunicacion) {
  return useQuery({
    queryKey: ['mensajes', proyectoId, canal],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (canal) params.set('canal', canal)
      params.set('limite', '200')
      const res = await fetch(
        `${CONFIG.urlApi}/api/proyectos/${proyectoId}/mensajes?${params}`
      )
      if (!res.ok) throw new Error('Error obteniendo mensajes')
      const datos = await res.json()
      return (datos.mensajes as Record<string, unknown>[]).map(mapearMensaje)
    },
    enabled: !!proyectoId,
    staleTime: Infinity, // WebSocket maneja las actualizaciones
  })
}

export function useEnviarTarea(proyectoId: string) {
  return useMutation({
    mutationFn: async ({
      tarea,
      agenteDestino,
    }: {
      tarea: string
      agenteDestino?: string
    }) => {
      const formData = new FormData()
      formData.append('tarea', tarea)
      if (agenteDestino) formData.append('agente_destino', agenteDestino)

      const res = await fetch(
        `${CONFIG.urlApi}/api/proyectos/${proyectoId}/tarea`,
        { method: 'POST', body: formData }
      )
      if (!res.ok) throw new Error('Error enviando tarea')
      return res.json()
    },
  })
}
