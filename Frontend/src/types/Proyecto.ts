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
  urlRepositorio?: string
  ramaDesarrollo?: string
}

export type EstadoCommit =
  | 'pendiente'
  | 'en_revision_qa'
  | 'aprobado_qa'
  | 'rechazado_qa'
  | 'aprobado_lider'
  | 'rechazado_lider'
  | 'commiteado'
  | 'error'

export interface ArchivoCommit {
  ruta: string
  contenido: string
}

export interface CommitPendiente {
  id: string
  proyectoId: string
  descripcion: string
  archivos: ArchivoCommit[]
  estado: EstadoCommit
  revisionQa?: string
  revisionLider?: string
  hashCommit?: string
  fechaCreacion: string
}

export interface DatosNuevoProyecto {
  nombre: string
  descripcion: string
  promptInicial: string
}
