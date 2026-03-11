import { useState } from 'react'
import { useProyectos } from '../hooks/useProyectos'
import TarjetaProyecto from '../components/project/TarjetaProyecto'
import ModalNuevoProyecto from '../components/project/ModalNuevoProyecto'
import { Plus, Loader2 } from 'lucide-react'

export default function Dashboard() {
  const [modalAbierto, setModalAbierto] = useState(false)
  const { data: proyectos, isLoading } = useProyectos()

  return (
    <div className="min-h-screen p-6" style={{ backgroundColor: '#0a0c10' }}>
      {/* Header */}
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold font-ui" style={{ color: '#00d4ff' }}>
              SysDept <span style={{ color: '#7c3aed' }}>AI</span>
            </h1>
            <p className="text-sm mt-1" style={{ color: '#6b7280' }}>
              Tu departamento de sistemas virtual
            </p>
          </div>
          <button
            onClick={() => setModalAbierto(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all hover:opacity-90"
            style={{ backgroundColor: '#00d4ff', color: '#0a0c10' }}
          >
            <Plus size={18} />
            Nuevo Proyecto
          </button>
        </div>

        {/* Grid de proyectos */}
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 size={32} className="animate-spin" style={{ color: '#00d4ff' }} />
          </div>
        ) : proyectos && proyectos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {proyectos.map((proyecto) => (
              <TarjetaProyecto key={proyecto.id} proyecto={proyecto} />
            ))}
          </div>
        ) : (
          <div
            className="flex flex-col items-center justify-center py-20 rounded-2xl border"
            style={{ borderColor: '#1e2530', borderStyle: 'dashed' }}
          >
            <p className="text-4xl mb-4">🏢</p>
            <h2 className="text-lg font-semibold font-ui mb-2" style={{ color: '#e2e8f0' }}>
              Sin proyectos aún
            </h2>
            <p className="text-sm mb-6" style={{ color: '#6b7280' }}>
              Crea tu primer proyecto y el equipo de IA comenzará a trabajar
            </p>
            <button
              onClick={() => setModalAbierto(true)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm"
              style={{ backgroundColor: '#00d4ff', color: '#0a0c10' }}
            >
              <Plus size={18} />
              Crear Primer Proyecto
            </button>
          </div>
        )}
      </div>

      <ModalNuevoProyecto
        abierto={modalAbierto}
        onCerrar={() => setModalAbierto(false)}
      />
    </div>
  )
}
