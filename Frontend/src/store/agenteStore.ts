import { create } from 'zustand'
import type { Agente } from '../types/Agente'

interface EstadoAgenteStore {
  agentesTyping: Record<string, boolean>
  establecerTyping: (agenteRol: string, escribiendo: boolean) => void
  actualizarEstadoAgente: (agenteId: string, estado: Agente['estado']) => void
}

export const useAgenteStore = create<EstadoAgenteStore>((set) => ({
  agentesTyping: {},
  establecerTyping: (agenteRol, escribiendo) =>
    set((s) => ({
      agentesTyping: { ...s.agentesTyping, [agenteRol]: escribiendo },
    })),
  actualizarEstadoAgente: () => {},
}))
