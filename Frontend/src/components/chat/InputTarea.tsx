import { useState } from 'react'
import { Send } from 'lucide-react'
import { useEnviarTarea } from '../../hooks/useMensajes'

interface InputTareaProps {
  proyectoId: string
}

export default function InputTarea({ proyectoId }: InputTareaProps) {
  const [texto, setTexto] = useState('')
  const { mutate: enviarTarea, isPending } = useEnviarTarea(proyectoId)

  const manejarEnvio = (e: React.FormEvent) => {
    e.preventDefault()
    if (!texto.trim() || isPending) return
    enviarTarea({ tarea: texto.trim() })
    setTexto('')
  }

  const manejarKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      manejarEnvio(e as unknown as React.FormEvent)
    }
  }

  return (
    <form
      onSubmit={manejarEnvio}
      className="flex items-end gap-2 p-4 border-t"
      style={{ borderColor: '#1e2530' }}
    >
      <div className="flex-1">
        <textarea
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          onKeyDown={manejarKeyDown}
          placeholder="Escribe una tarea para el equipo... (Enter para enviar)"
          rows={2}
          className="w-full px-3 py-2 rounded-lg text-sm border outline-none resize-none"
          style={{
            backgroundColor: '#1e2530',
            borderColor: '#2a3545',
            color: '#e2e8f0',
            fontFamily: 'inherit',
          }}
        />
      </div>
      <button
        type="submit"
        disabled={isPending || !texto.trim()}
        className="p-2.5 rounded-lg transition-all hover:opacity-90 disabled:opacity-40 flex-shrink-0"
        style={{ backgroundColor: '#00d4ff', color: '#0a0c10' }}
      >
        <Send size={18} />
      </button>
    </form>
  )
}
