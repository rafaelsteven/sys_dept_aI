export type CanalComunicacion = 'general' | 'arquitectura' | 'backend' | 'frontend' | 'qa' | 'directo'
export type EtiquetaMensaje = 'PREGUNTA' | 'APROBACION' | 'SEGURIDAD' | 'ACTUALIZACION' | 'BUG' | 'OK' | 'TAREA' | 'SISTEMA'

export interface Mensaje {
  id: string
  proyectoId: string
  canal: CanalComunicacion
  agenteOrigen: string
  agenteDestino: string
  etiqueta: EtiquetaMensaje
  contenido: string
  marcaTiempo: string
  esTyping: boolean
}

export interface EventoTyping {
  agente: string
  canal: CanalComunicacion
  escribiendo: boolean
}

export const COLOR_ETIQUETA: Record<EtiquetaMensaje, string> = {
  PREGUNTA: '#00d4ff',
  APROBACION: '#00ff88',
  SEGURIDAD: '#ff4466',
  ACTUALIZACION: '#ffd700',
  BUG: '#ff4466',
  OK: '#00ff88',
  TAREA: '#7c3aed',
  SISTEMA: '#6b7280',
}
