export type RolAgente = 'lider' | 'arquitecto' | 'backend' | 'frontend' | 'qa' | 'dba'
export type EstadoAgente = 'activo' | 'pensando' | 'inactivo' | 'error'

export interface Agente {
  id: string
  proyectoId: string
  rol: RolAgente
  nombre: string
  especialidad?: string
  estado: EstadoAgente
  fechaIncorporacion: string
}

export interface DatosNuevoAgente {
  rol: RolAgente
  nombre: string
  especialidad?: string
}

export const COLOR_POR_ROL: Record<RolAgente, string> = {
  lider: '#00d4ff',
  arquitecto: '#7c3aed',
  backend: '#ff8c42',
  frontend: '#ec4899',
  qa: '#00ff88',
  dba: '#ffd700',
}

export const NOMBRE_ROL: Record<RolAgente, string> = {
  lider: 'Líder',
  arquitecto: 'Arquitecto',
  backend: 'Backend Dev',
  frontend: 'Frontend Dev',
  qa: 'QA Engineer',
  dba: 'DBA',
}
