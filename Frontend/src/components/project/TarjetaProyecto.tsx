import { Link } from 'react-router-dom'
import { Trash2, ArrowRight } from 'lucide-react'
import { useEliminarProyecto } from '../../hooks/useProyectos'
import type { Proyecto } from '../../types/Proyecto'

const ETIQUETA_ESTADO: Record<Proyecto['estado'], string> = {
  creando: 'Creando',
  analizando: 'Analizando...',
  activo: 'Activo',
  pausado: 'Pausado',
  completado: 'Completado',
}

const COLOR_ESTADO: Record<Proyecto['estado'], string> = {
  creando: '#6b7280',
  analizando: '#ffd700',
  activo: '#00ff88',
  pausado: '#ff8c42',
  completado: '#00d4ff',
}

interface TarjetaProyectoProps {
  proyecto: Proyecto
}

export default function TarjetaProyecto({ proyecto }: TarjetaProyectoProps) {
  const { mutate: eliminar } = useEliminarProyecto()

  return (
    <div
      className="p-4 rounded-xl border transition-all hover:border-opacity-80 group"
      style={{ backgroundColor: '#0f1318', borderColor: '#1e2530' }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold font-ui truncate" style={{ color: '#e2e8f0' }}>
            {proyecto.nombre}
          </h3>
          <p className="text-xs mt-0.5 line-clamp-2" style={{ color: '#9ca3af' }}>
            {proyecto.descripcion}
          </p>
        </div>
        <div className="flex items-center gap-2 ml-3 flex-shrink-0">
          <span
            className="text-xs px-2 py-0.5 rounded-full font-mono font-semibold"
            style={{
              backgroundColor: COLOR_ESTADO[proyecto.estado] + '22',
              color: COLOR_ESTADO[proyecto.estado],
            }}
          >
            {ETIQUETA_ESTADO[proyecto.estado]}
          </span>
        </div>
      </div>

      <div className="flex items-center justify-between mt-3">
        <span className="text-xs" style={{ color: '#6b7280' }}>
          {new Date(proyecto.fechaCreacion).toLocaleDateString('es')}
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => eliminar(proyecto.id)}
            className="p-1.5 rounded opacity-0 group-hover:opacity-100 transition-all"
            style={{ color: '#ff4466' }}
          >
            <Trash2 size={14} />
          </button>
          <Link
            to={`/proyecto/${proyecto.id}`}
            className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-lg transition-all hover:opacity-80"
            style={{ backgroundColor: '#1e2530', color: '#00d4ff' }}
          >
            Abrir
            <ArrowRight size={12} />
          </Link>
        </div>
      </div>
    </div>
  )
}
