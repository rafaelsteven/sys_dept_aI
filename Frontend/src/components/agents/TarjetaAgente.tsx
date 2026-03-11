import { COLOR_POR_ROL, NOMBRE_ROL, type Agente } from '../../types/Agente'
import { useAgenteStore } from '../../store/agenteStore'

const ICONO_ESTADO: Record<Agente['estado'], string> = {
  activo: '🟢',
  pensando: '🟡',
  inactivo: '⚪',
  error: '🔴',
}

interface TarjetaAgenteProps {
  agente: Agente
}

export default function TarjetaAgente({ agente }: TarjetaAgenteProps) {
  const { agentesTyping } = useAgenteStore()
  const estaEscribiendo = agentesTyping[agente.rol]

  const color = COLOR_POR_ROL[agente.rol]

  return (
    <div
      className="p-3 rounded-lg border mb-2"
      style={{ backgroundColor: '#0a0c10', borderColor: '#1e2530' }}
    >
      <div className="flex items-center gap-2">
        <div
          className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold font-mono flex-shrink-0"
          style={{ backgroundColor: color + '22', color, border: `1px solid ${color}44` }}
        >
          {agente.nombre.charAt(0)}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold truncate" style={{ color }}>
            {agente.nombre}
          </p>
          <p className="text-xs" style={{ color: '#6b7280' }}>
            {NOMBRE_ROL[agente.rol]}
          </p>
        </div>
        <span className="text-base flex-shrink-0">
          {estaEscribiendo ? '🟡' : ICONO_ESTADO[agente.estado]}
        </span>
      </div>
      {agente.especialidad && (
        <p className="text-xs mt-2 truncate" style={{ color: '#9ca3af' }}>
          {agente.especialidad}
        </p>
      )}
      {estaEscribiendo && (
        <p className="text-xs mt-1" style={{ color: '#ffd700' }}>
          escribiendo...
        </p>
      )}
    </div>
  )
}
