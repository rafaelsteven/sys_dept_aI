import { Link } from 'react-router-dom'
import { Plus, Folder, Loader2 } from 'lucide-react'
import { useProyectos } from '../../hooks/useProyectos'
import { useProyectoStore } from '../../store/proyectoStore'
import type { Proyecto } from '../../types/Proyecto'

const COLORES_ESTADO: Record<Proyecto['estado'], string> = {
  creando: '#6b7280',
  analizando: '#ffd700',
  activo: '#00ff88',
  pausado: '#ff8c42',
  completado: '#00d4ff',
}

interface SidebarProps {
  onNuevoProyecto: () => void
}

export default function Sidebar({ onNuevoProyecto }: SidebarProps) {
  const { data: proyectos, isLoading } = useProyectos()
  const { proyectoActivo } = useProyectoStore()

  return (
    <aside
      className="flex flex-col h-full border-r"
      style={{
        width: 260,
        minWidth: 260,
        backgroundColor: '#0f1318',
        borderColor: '#1e2530',
      }}
    >
      {/* Logo */}
      <div className="p-4 border-b" style={{ borderColor: '#1e2530' }}>
        <h1 className="text-lg font-bold font-ui" style={{ color: '#00d4ff' }}>
          SysDept <span style={{ color: '#7c3aed' }}>AI</span>
        </h1>
        <p className="text-xs mt-0.5" style={{ color: '#6b7280' }}>
          Departamento Virtual
        </p>
      </div>

      {/* Botón nuevo proyecto */}
      <div className="p-3">
        <button
          onClick={onNuevoProyecto}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all hover:opacity-90"
          style={{ backgroundColor: '#00d4ff', color: '#0a0c10' }}
        >
          <Plus size={16} />
          Nuevo Proyecto
        </button>
      </div>

      {/* Lista de proyectos */}
      <div className="flex-1 overflow-y-auto px-2">
        <p className="text-xs px-2 pb-2 font-semibold uppercase tracking-wider" style={{ color: '#6b7280' }}>
          Proyectos
        </p>

        {isLoading && (
          <div className="flex justify-center py-4">
            <Loader2 size={20} className="animate-spin" style={{ color: '#00d4ff' }} />
          </div>
        )}

        {proyectos?.map((proyecto) => (
          <Link
            key={proyecto.id}
            to={`/proyecto/${proyecto.id}`}
            className="flex items-center gap-2 px-2 py-2 rounded-lg text-sm mb-1 transition-all hover:opacity-80"
            style={{
              backgroundColor: proyectoActivo?.id === proyecto.id ? '#1e2530' : 'transparent',
              color: '#cbd5e1',
            }}
          >
            <div
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: COLORES_ESTADO[proyecto.estado] }}
            />
            <Folder size={14} style={{ color: '#6b7280' }} />
            <span className="truncate">{proyecto.nombre}</span>
          </Link>
        ))}

        {!isLoading && (!proyectos || proyectos.length === 0) && (
          <p className="text-xs px-2 py-4 text-center" style={{ color: '#6b7280' }}>
            No hay proyectos aún
          </p>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t text-xs" style={{ borderColor: '#1e2530', color: '#6b7280' }}>
        <p>Powered by Claude Sonnet</p>
      </div>
    </aside>
  )
}
