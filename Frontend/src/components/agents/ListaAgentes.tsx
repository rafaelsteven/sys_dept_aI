import { useState } from 'react'
import { UserPlus } from 'lucide-react'
import { useAgentes } from '../../hooks/useAgentes'
import TarjetaAgente from './TarjetaAgente'
import ModalAgregarAgente from './ModalAgregarAgente'

interface ListaAgentesProps {
  proyectoId: string
}

export default function ListaAgentes({ proyectoId }: ListaAgentesProps) {
  const { data: agentes, isLoading } = useAgentes(proyectoId)
  const [modalAbierto, setModalAbierto] = useState(false)

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs font-semibold uppercase tracking-wider" style={{ color: '#6b7280' }}>
          Equipo
        </p>
        <button
          onClick={() => setModalAbierto(true)}
          className="flex items-center gap-1 text-xs px-2 py-1 rounded transition-all hover:opacity-80"
          style={{ backgroundColor: '#1e2530', color: '#00d4ff' }}
        >
          <UserPlus size={12} />
          Agregar
        </button>
      </div>

      {isLoading && (
        <p className="text-xs" style={{ color: '#6b7280' }}>Cargando equipo...</p>
      )}

      {agentes?.map((agente) => (
        <TarjetaAgente key={agente.id} agente={agente} />
      ))}

      <ModalAgregarAgente
        proyectoId={proyectoId}
        abierto={modalAbierto}
        onCerrar={() => setModalAbierto(false)}
      />
    </div>
  )
}
