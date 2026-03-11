import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CONFIG } from '../configuracion/api'
import type { Agente, DatosNuevoAgente } from '../types/Agente'

const mapearAgente = (datos: Record<string, unknown>): Agente => ({
  id: datos.id as string,
  proyectoId: datos.proyecto_id as string,
  rol: datos.rol as Agente['rol'],
  nombre: datos.nombre as string,
  especialidad: datos.especialidad as string | undefined,
  estado: datos.estado as Agente['estado'],
  fechaIncorporacion: datos.fecha_incorporacion as string,
})

export function useAgentes(proyectoId: string) {
  return useQuery({
    queryKey: ['agentes', proyectoId],
    queryFn: async () => {
      const res = await fetch(
        `${CONFIG.urlApi}/api/proyectos/${proyectoId}/agentes/`
      )
      if (!res.ok) throw new Error('Error obteniendo agentes')
      const datos = await res.json()
      return (datos.agentes as Record<string, unknown>[]).map(mapearAgente)
    },
    enabled: !!proyectoId,
  })
}

export function useAgregarAgente(proyectoId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (datos: DatosNuevoAgente) => {
      const res = await fetch(
        `${CONFIG.urlApi}/api/proyectos/${proyectoId}/agentes/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            rol: datos.rol,
            nombre: datos.nombre,
            especialidad: datos.especialidad,
          }),
        }
      )
      if (!res.ok) throw new Error('Error agregando agente')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agentes', proyectoId] })
    },
  })
}
