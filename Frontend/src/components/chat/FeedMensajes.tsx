import { useEffect, useRef } from 'react'
import { Loader2 } from 'lucide-react'
import { useMensajes } from '../../hooks/useMensajes'
import { useProyectoStore } from '../../store/proyectoStore'
import BurbujaMensaje from './BurbujaMensaje'
import IndicadorTyping from './IndicadorTyping'

interface FeedMensajesProps {
  proyectoId: string
}

export default function FeedMensajes({ proyectoId }: FeedMensajesProps) {
  const { canalActivo } = useProyectoStore()
  const { data: mensajes, isLoading } = useMensajes(proyectoId, canalActivo)
  const finRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    finRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [mensajes?.length])

  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <Loader2 size={24} className="animate-spin" style={{ color: '#00d4ff' }} />
      </div>
    )
  }

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="flex-1 overflow-y-auto p-4">
        {(!mensajes || mensajes.length === 0) && (
          <div className="flex flex-col items-center justify-center h-full" style={{ color: '#6b7280' }}>
            <p className="text-sm">No hay mensajes en #{canalActivo}</p>
            <p className="text-xs mt-1">Los mensajes aparecerán aquí en tiempo real</p>
          </div>
        )}

        {mensajes?.map((mensaje) => (
          <BurbujaMensaje key={mensaje.id} mensaje={mensaje} />
        ))}

        <div ref={finRef} />
      </div>

      <IndicadorTyping />
    </div>
  )
}
