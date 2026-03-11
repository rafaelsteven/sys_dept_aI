import { COLOR_POR_ROL, NOMBRE_ROL, type RolAgente } from '../../types/Agente'
import { COLOR_ETIQUETA, type Mensaje } from '../../types/Mensaje'

const formatearHora = (marcaTiempo: string): string => {
  try {
    return new Date(marcaTiempo).toLocaleTimeString('es', {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
}

interface BurbujaMensajeProps {
  mensaje: Mensaje
}

export default function BurbujaMensaje({ mensaje }: BurbujaMensajeProps) {
  const esSistema = mensaje.agenteOrigen === 'sistema'
  const colorAgente = esSistema
    ? '#6b7280'
    : (COLOR_POR_ROL[mensaje.agenteOrigen as RolAgente] ?? '#e2e8f0')

  const nombreAgente = esSistema
    ? 'Sistema'
    : (NOMBRE_ROL[mensaje.agenteOrigen as RolAgente] ?? mensaje.agenteOrigen)

  if (esSistema) {
    return (
      <div className="flex justify-center my-2 animate-fade-in">
        <span
          className="text-xs px-3 py-1 rounded-full border font-mono"
          style={{ color: '#6b7280', borderColor: '#1e2530', backgroundColor: '#0f1318' }}
        >
          {mensaje.contenido}
        </span>
      </div>
    )
  }

  return (
    <div className="flex gap-3 mb-4 animate-fade-in">
      {/* Avatar */}
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold font-mono flex-shrink-0 mt-0.5"
        style={{
          backgroundColor: colorAgente + '22',
          color: colorAgente,
          border: `1px solid ${colorAgente}44`,
        }}
      >
        {nombreAgente.charAt(0)}
      </div>

      {/* Contenido */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1 flex-wrap">
          <span className="text-sm font-semibold font-ui" style={{ color: colorAgente }}>
            {nombreAgente}
          </span>
          {mensaje.agenteDestino !== 'todos' && (
            <span className="text-xs" style={{ color: '#6b7280' }}>
              → {NOMBRE_ROL[mensaje.agenteDestino as RolAgente] ?? mensaje.agenteDestino}
            </span>
          )}
          <span
            className="text-xs px-1.5 py-0.5 rounded font-mono font-semibold"
            style={{
              backgroundColor: COLOR_ETIQUETA[mensaje.etiqueta] + '22',
              color: COLOR_ETIQUETA[mensaje.etiqueta],
              border: `1px solid ${COLOR_ETIQUETA[mensaje.etiqueta]}44`,
            }}
          >
            {mensaje.etiqueta}
          </span>
          <span className="text-xs ml-auto" style={{ color: '#4b5563' }}>
            {formatearHora(mensaje.marcaTiempo)}
          </span>
        </div>

        <div
          className="text-sm leading-relaxed rounded-lg p-3 border whitespace-pre-wrap"
          style={{
            backgroundColor: '#0f1318',
            borderColor: '#1e2530',
            color: '#cbd5e1',
            fontFamily: 'inherit',
          }}
        >
          {mensaje.contenido}
        </div>
      </div>
    </div>
  )
}
