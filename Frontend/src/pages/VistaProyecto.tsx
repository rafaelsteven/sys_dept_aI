import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Loader2 } from 'lucide-react'
import { useProyecto } from '../hooks/useProyectos'
import { useProyectoStore } from '../store/proyectoStore'
import { useConexionWebSocket } from '../hooks/useConexionWebSocket'
import Sidebar from '../components/layout/Sidebar'
import SelectorCanal from '../components/chat/SelectorCanal'
import FeedMensajes from '../components/chat/FeedMensajes'
import InputTarea from '../components/chat/InputTarea'
import ListaAgentes from '../components/agents/ListaAgentes'
import ModalNuevoProyecto from '../components/project/ModalNuevoProyecto'

const COLOR_ESTADO_TEXTO: Record<string, string> = {
  activo: '#00ff88',
  analizando: '#ffd700',
  creando: '#6b7280',
  pausado: '#ff8c42',
  completado: '#00d4ff',
}

export default function VistaProyecto() {
  const { proyectoId } = useParams<{ proyectoId: string }>()
  const { data: proyecto, isLoading } = useProyecto(proyectoId)
  const { establecerProyectoActivo } = useProyectoStore()
  const [modalNuevoAbierto, setModalNuevoAbierto] = useState(false)

  // Conectar WebSocket para mensajes en tiempo real
  useConexionWebSocket(proyectoId)

  useEffect(() => {
    if (proyecto) establecerProyectoActivo(proyecto)
    return () => establecerProyectoActivo(null)
  }, [proyecto, establecerProyectoActivo])

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center" style={{ backgroundColor: '#0a0c10' }}>
        <Loader2 size={32} className="animate-spin" style={{ color: '#00d4ff' }} />
      </div>
    )
  }

  if (!proyecto || !proyectoId) {
    return (
      <div className="h-screen flex flex-col items-center justify-center" style={{ backgroundColor: '#0a0c10' }}>
        <p style={{ color: '#ff4466' }}>Proyecto no encontrado</p>
        <Link to="/" className="mt-4 text-sm" style={{ color: '#00d4ff' }}>
          Volver al inicio
        </Link>
      </div>
    )
  }

  return (
    <div className="h-screen flex overflow-hidden" style={{ backgroundColor: '#0a0c10' }}>
      {/* Sidebar */}
      <Sidebar onNuevoProyecto={() => setModalNuevoAbierto(true)} />

      {/* Area principal */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header del proyecto */}
        <div
          className="flex items-center gap-3 px-4 py-3 border-b flex-shrink-0"
          style={{ backgroundColor: '#0f1318', borderColor: '#1e2530' }}
        >
          <Link to="/" style={{ color: '#6b7280' }}>
            <ArrowLeft size={18} />
          </Link>
          <div>
            <h2 className="text-sm font-semibold font-ui" style={{ color: '#e2e8f0' }}>
              {proyecto.nombre}
            </h2>
            <p className="text-xs" style={{ color: '#6b7280' }}>{proyecto.descripcion}</p>
          </div>
          <div className="ml-auto">
            <span
              className="text-xs px-2 py-0.5 rounded-full font-mono"
              style={{
                backgroundColor: '#1e2530',
                color: COLOR_ESTADO_TEXTO[proyecto.estado] ?? '#e2e8f0',
              }}
            >
              {proyecto.estado}
            </span>
          </div>
        </div>

        {/* Selector de canal */}
        <SelectorCanal />

        {/* Feed de mensajes */}
        <FeedMensajes proyectoId={proyectoId} />

        {/* Input de tarea */}
        <InputTarea proyectoId={proyectoId} />
      </div>

      {/* Panel de actividad / equipo */}
      <div
        className="flex flex-col border-l overflow-y-auto"
        style={{
          width: 280,
          minWidth: 280,
          borderColor: '#1e2530',
          backgroundColor: '#0f1318',
          padding: '16px',
        }}
      >
        <ListaAgentes proyectoId={proyectoId} />

        {/* Info del proyecto */}
        <div className="mt-6">
          <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: '#6b7280' }}>
            Info del Proyecto
          </p>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span style={{ color: '#6b7280' }}>Estado</span>
              <span style={{ color: '#e2e8f0' }}>{proyecto.estado}</span>
            </div>
            {proyecto.archivosPdf.length > 0 && (
              <div className="flex justify-between text-xs">
                <span style={{ color: '#6b7280' }}>PDFs</span>
                <span style={{ color: '#e2e8f0' }}>{proyecto.archivosPdf.length}</span>
              </div>
            )}
            {proyecto.archivosImagen.length > 0 && (
              <div className="flex justify-between text-xs">
                <span style={{ color: '#6b7280' }}>Imagenes</span>
                <span style={{ color: '#e2e8f0' }}>{proyecto.archivosImagen.length}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      <ModalNuevoProyecto
        abierto={modalNuevoAbierto}
        onCerrar={() => setModalNuevoAbierto(false)}
      />
    </div>
  )
}
