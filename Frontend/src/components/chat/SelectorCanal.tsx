import { useProyectoStore } from '../../store/proyectoStore'
import type { CanalComunicacion } from '../../types/Mensaje'

const CANALES: { id: CanalComunicacion; etiqueta: string }[] = [
  { id: 'general', etiqueta: '#general' },
  { id: 'arquitectura', etiqueta: '#arquitectura' },
  { id: 'backend', etiqueta: '#backend' },
  { id: 'frontend', etiqueta: '#frontend' },
  { id: 'qa', etiqueta: '#qa' },
  { id: 'directo', etiqueta: '#directo' },
]

export default function SelectorCanal() {
  const { canalActivo, establecerCanalActivo } = useProyectoStore()

  return (
    <div
      className="flex items-center gap-1 px-4 py-2 border-b overflow-x-auto"
      style={{ borderColor: '#1e2530', backgroundColor: '#0f1318' }}
    >
      {CANALES.map((canal) => (
        <button
          key={canal.id}
          onClick={() => establecerCanalActivo(canal.id)}
          className="flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-mono transition-all"
          style={{
            backgroundColor: canalActivo === canal.id ? '#1e2530' : 'transparent',
            color: canalActivo === canal.id ? '#00d4ff' : '#6b7280',
            border: canalActivo === canal.id ? '1px solid #1e2530' : '1px solid transparent',
          }}
        >
          {canal.etiqueta}
        </button>
      ))}
    </div>
  )
}
