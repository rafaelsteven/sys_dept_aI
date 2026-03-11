import { useState } from 'react'
import { X } from 'lucide-react'
import { useAgregarAgente } from '../../hooks/useAgentes'
import { NOMBRE_ROL, type RolAgente } from '../../types/Agente'

const ROLES_OPCIONALES: RolAgente[] = ['backend', 'frontend', 'qa', 'dba']

interface ModalAgregarAgenteProps {
  proyectoId: string
  abierto: boolean
  onCerrar: () => void
}

export default function ModalAgregarAgente({
  proyectoId,
  abierto,
  onCerrar,
}: ModalAgregarAgenteProps) {
  const [rol, setRol] = useState<RolAgente>('backend')
  const [nombre, setNombre] = useState('')
  const [especialidad, setEspecialidad] = useState('')

  const { mutate: agregarAgente, isPending } = useAgregarAgente(proyectoId)

  const manejarSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!nombre.trim()) return

    agregarAgente(
      { rol, nombre: nombre.trim(), especialidad: especialidad.trim() || undefined },
      {
        onSuccess: () => {
          onCerrar()
          setNombre('')
          setEspecialidad('')
          setRol('backend')
        },
      }
    )
  }

  if (!abierto) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ backgroundColor: 'rgba(0,0,0,0.8)' }}>
      <div className="w-full max-w-md rounded-xl border p-6" style={{ backgroundColor: '#0f1318', borderColor: '#1e2530' }}>
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-bold font-ui" style={{ color: '#e2e8f0' }}>
            Agregar Miembro
          </h2>
          <button onClick={onCerrar} style={{ color: '#6b7280' }}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={manejarSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1.5" style={{ color: '#9ca3af' }}>Rol</label>
            <select
              value={rol}
              onChange={(e) => setRol(e.target.value as RolAgente)}
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ backgroundColor: '#1e2530', borderColor: '#2a3545', color: '#e2e8f0' }}
            >
              {ROLES_OPCIONALES.map((r) => (
                <option key={r} value={r}>{NOMBRE_ROL[r]}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: '#9ca3af' }}>Nombre</label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="ej: Javier Ruiz"
              required
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ backgroundColor: '#1e2530', borderColor: '#2a3545', color: '#e2e8f0' }}
            />
          </div>

          <div>
            <label className="block text-sm mb-1.5" style={{ color: '#9ca3af' }}>Especialidad (opcional)</label>
            <input
              type="text"
              value={especialidad}
              onChange={(e) => setEspecialidad(e.target.value)}
              placeholder="ej: Experto en microservicios"
              className="w-full px-3 py-2 rounded-lg text-sm border outline-none"
              style={{ backgroundColor: '#1e2530', borderColor: '#2a3545', color: '#e2e8f0' }}
            />
          </div>

          <p className="text-xs" style={{ color: '#6b7280' }}>
            El Líder asignará tareas automáticamente al incorporarse.
          </p>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onCerrar}
              className="flex-1 py-2 rounded-lg text-sm border transition-all hover:opacity-80"
              style={{ borderColor: '#1e2530', color: '#9ca3af' }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isPending || !nombre.trim()}
              className="flex-1 py-2 rounded-lg text-sm font-semibold transition-all hover:opacity-90 disabled:opacity-50"
              style={{ backgroundColor: '#00d4ff', color: '#0a0c10' }}
            >
              {isPending ? 'Incorporando...' : 'Incorporar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
