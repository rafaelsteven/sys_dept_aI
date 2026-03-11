import { useAgenteStore } from '../../store/agenteStore'
import { COLOR_POR_ROL, NOMBRE_ROL, type RolAgente } from '../../types/Agente'

export default function IndicadorTyping() {
  const { agentesTyping } = useAgenteStore()

  const agentesEscribiendo = Object.entries(agentesTyping)
    .filter(([, escribiendo]) => escribiendo)
    .map(([rol]) => rol as RolAgente)

  if (agentesEscribiendo.length === 0) return null

  return (
    <div className="flex items-center gap-2 px-4 py-2">
      {agentesEscribiendo.map((rol) => (
        <div key={rol} className="flex items-center gap-1.5">
          <div
            className="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold"
            style={{ backgroundColor: COLOR_POR_ROL[rol] + '22', color: COLOR_POR_ROL[rol] }}
          >
            {(NOMBRE_ROL[rol] ?? rol).charAt(0)}
          </div>
          <span className="text-xs" style={{ color: '#6b7280' }}>
            {NOMBRE_ROL[rol] ?? rol} está escribiendo
          </span>
          <div className="flex gap-0.5">
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                className="w-1 h-1 rounded-full animate-bounce"
                style={{
                  backgroundColor: COLOR_POR_ROL[rol],
                  animationDelay: `${i * 0.15}s`,
                }}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
