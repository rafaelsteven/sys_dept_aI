import { create } from 'zustand'
import type { Proyecto } from '../types/Proyecto'
import type { CanalComunicacion } from '../types/Mensaje'

interface EstadoProyectoStore {
  proyectoActivo: Proyecto | null
  canalActivo: CanalComunicacion
  establecerProyectoActivo: (proyecto: Proyecto | null) => void
  establecerCanalActivo: (canal: CanalComunicacion) => void
}

export const useProyectoStore = create<EstadoProyectoStore>((set) => ({
  proyectoActivo: null,
  canalActivo: 'general',
  establecerProyectoActivo: (proyecto) => set({ proyectoActivo: proyecto }),
  establecerCanalActivo: (canal) => set({ canalActivo: canal }),
}))
