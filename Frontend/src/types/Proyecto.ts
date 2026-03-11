export type EstadoProyecto = 'creando' | 'analizando' | 'activo' | 'pausado' | 'completado'

export interface Proyecto {
  id: string
  nombre: string
  descripcion: string
  promptInicial: string
  fechaCreacion: string
  estado: EstadoProyecto
  textoPdf?: string
  archivosPdf: string[]
  archivosImagen: string[]
}

export interface DatosNuevoProyecto {
  nombre: string
  descripcion: string
  promptInicial: string
}
