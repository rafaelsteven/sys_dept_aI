import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CONFIG } from '../configuracion/api'
import type { Proyecto } from '../types/Proyecto'

const mapearProyecto = (datos: Record<string, unknown>): Proyecto => ({
  id: datos.id as string,
  nombre: datos.nombre as string,
  descripcion: datos.descripcion as string,
  promptInicial: datos.prompt_inicial as string,
  fechaCreacion: datos.fecha_creacion as string,
  estado: datos.estado as Proyecto['estado'],
  textoPdf: datos.texto_pdf as string | undefined,
  archivosPdf: (datos.archivos_pdf as string[]) ?? [],
  archivosImagen: (datos.archivos_imagen as string[]) ?? [],
})

const obtenerProyectos = async (): Promise<Proyecto[]> => {
  const res = await fetch(`${CONFIG.urlApi}/api/proyectos/`)
  if (!res.ok) throw new Error('Error obteniendo proyectos')
  const datos = await res.json()
  return (datos.proyectos as Record<string, unknown>[]).map(mapearProyecto)
}

const obtenerProyecto = async (id: string): Promise<Proyecto> => {
  const res = await fetch(`${CONFIG.urlApi}/api/proyectos/${id}`)
  if (!res.ok) throw new Error('Proyecto no encontrado')
  const datos = await res.json()
  return mapearProyecto(datos.proyecto as Record<string, unknown>)
}

export function useProyectos() {
  return useQuery({
    queryKey: ['proyectos'],
    queryFn: obtenerProyectos,
  })
}

export function useProyecto(id: string | undefined) {
  return useQuery({
    queryKey: ['proyecto', id],
    queryFn: () => obtenerProyecto(id!),
    enabled: !!id,
  })
}

export function useCrearProyecto() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (formData: FormData) => {
      const res = await fetch(`${CONFIG.urlApi}/api/proyectos/`, {
        method: 'POST',
        body: formData,
      })
      if (!res.ok) {
        const error = await res.json()
        throw new Error((error.detail as string) ?? 'Error creando proyecto')
      }
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proyectos'] })
    },
  })
}

export function useEliminarProyecto() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`${CONFIG.urlApi}/api/proyectos/${id}`, {
        method: 'DELETE',
      })
      if (!res.ok) throw new Error('Error eliminando proyecto')
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['proyectos'] })
    },
  })
}
