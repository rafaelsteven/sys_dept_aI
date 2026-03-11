import { useState, useRef } from 'react'
import { X, Upload, FileText, Image, Loader2 } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useCrearProyecto } from '../../hooks/useProyectos'

interface ModalNuevoProyectoProps {
  abierto: boolean
  onCerrar: () => void
}

export default function ModalNuevoProyecto({ abierto, onCerrar }: ModalNuevoProyectoProps) {
  const [nombre, setNombre] = useState('')
  const [descripcion, setDescripcion] = useState('')
  const [promptInicial, setPromptInicial] = useState('')
  const [pdfs, setPdfs] = useState<File[]>([])
  const [imagenes, setImagenes] = useState<File[]>([])
  const inputPdfRef = useRef<HTMLInputElement>(null)
  const inputImgRef = useRef<HTMLInputElement>(null)

  const navigate = useNavigate()
  const { mutate: crearProyecto, isPending, error } = useCrearProyecto()

  const manejarSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!nombre.trim() || !descripcion.trim() || !promptInicial.trim()) return

    const formData = new FormData()
    formData.append('nombre', nombre.trim())
    formData.append('descripcion', descripcion.trim())
    formData.append('prompt_inicial', promptInicial.trim())
    pdfs.forEach((pdf) => formData.append('pdfs', pdf))
    imagenes.forEach((img) => formData.append('imagenes', img))

    crearProyecto(formData, {
      onSuccess: (datos: { proyecto: { id: string } }) => {
        onCerrar()
        navigate(`/proyecto/${datos.proyecto.id}`)
        resetear()
      },
    })
  }

  const resetear = () => {
    setNombre('')
    setDescripcion('')
    setPromptInicial('')
    setPdfs([])
    setImagenes([])
  }

  if (!abierto) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ backgroundColor: 'rgba(0,0,0,0.8)' }}>
      <div
        className="w-full max-w-2xl rounded-xl border flex flex-col"
        style={{ backgroundColor: '#0f1318', borderColor: '#1e2530', maxHeight: '90vh' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b flex-shrink-0" style={{ borderColor: '#1e2530' }}>
          <h2 className="text-xl font-bold font-ui" style={{ color: '#e2e8f0' }}>
            Nuevo Proyecto
          </h2>
          <button onClick={onCerrar} style={{ color: '#6b7280' }}>
            <X size={22} />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={manejarSubmit} className="flex flex-col flex-1 overflow-y-auto">
          <div className="p-6 space-y-4 flex-1">
            {/* Nombre */}
            <div>
              <label className="block text-sm mb-1.5 font-medium" style={{ color: '#9ca3af' }}>
                Nombre del proyecto *
              </label>
              <input
                type="text"
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
                required
                placeholder="ej: Sistema de gestión de inventario"
                className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none"
                style={{ backgroundColor: '#1e2530', borderColor: '#2a3545', color: '#e2e8f0' }}
              />
            </div>

            {/* Descripción */}
            <div>
              <label className="block text-sm mb-1.5 font-medium" style={{ color: '#9ca3af' }}>
                Descripción breve *
              </label>
              <textarea
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
                required
                placeholder="¿Qué problema resuelve este proyecto?"
                rows={2}
                className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none resize-none"
                style={{ backgroundColor: '#1e2530', borderColor: '#2a3545', color: '#e2e8f0' }}
              />
            </div>

            {/* Prompt inicial */}
            <div>
              <label className="block text-sm mb-1.5 font-medium" style={{ color: '#9ca3af' }}>
                Prompt inicial del proyecto *
              </label>
              <p className="text-xs mb-2" style={{ color: '#6b7280' }}>
                Describe con todo el detalle posible qué quieres construir: tecnologías, alcance, restricciones, usuarios objetivo...
              </p>
              <textarea
                value={promptInicial}
                onChange={(e) => setPromptInicial(e.target.value)}
                required
                placeholder="Quiero construir una aplicación que..."
                rows={5}
                className="w-full px-3 py-2.5 rounded-lg text-sm border outline-none resize-none"
                style={{ backgroundColor: '#1e2530', borderColor: '#2a3545', color: '#e2e8f0' }}
              />
            </div>

            {/* PDFs */}
            <div>
              <label className="block text-sm mb-1.5 font-medium" style={{ color: '#9ca3af' }}>
                Documentos PDF (opcional)
              </label>
              <button
                type="button"
                onClick={() => inputPdfRef.current?.click()}
                className="w-full py-3 rounded-lg border-2 border-dashed text-sm transition-all hover:opacity-80"
                style={{ borderColor: '#1e2530', color: '#6b7280' }}
              >
                <Upload size={16} className="inline mr-2" />
                Arrastra o haz clic para subir PDFs
              </button>
              <input
                ref={inputPdfRef}
                type="file"
                accept=".pdf"
                multiple
                hidden
                onChange={(e) => setPdfs(Array.from(e.target.files ?? []))}
              />
              {pdfs.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {pdfs.map((f, i) => (
                    <span
                      key={i}
                      className="flex items-center gap-1 text-xs px-2 py-1 rounded"
                      style={{ backgroundColor: '#1e2530', color: '#9ca3af' }}
                    >
                      <FileText size={12} />
                      {f.name}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Imágenes */}
            <div>
              <label className="block text-sm mb-1.5 font-medium" style={{ color: '#9ca3af' }}>
                Imágenes / Mockups (opcional)
              </label>
              <button
                type="button"
                onClick={() => inputImgRef.current?.click()}
                className="w-full py-3 rounded-lg border-2 border-dashed text-sm transition-all hover:opacity-80"
                style={{ borderColor: '#1e2530', color: '#6b7280' }}
              >
                <Upload size={16} className="inline mr-2" />
                Arrastra o haz clic para subir imágenes
              </button>
              <input
                ref={inputImgRef}
                type="file"
                accept=".png,.jpg,.jpeg,.webp,.gif"
                multiple
                hidden
                onChange={(e) => setImagenes(Array.from(e.target.files ?? []))}
              />
              {imagenes.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {imagenes.map((f, i) => (
                    <span
                      key={i}
                      className="flex items-center gap-1 text-xs px-2 py-1 rounded"
                      style={{ backgroundColor: '#1e2530', color: '#9ca3af' }}
                    >
                      <Image size={12} />
                      {f.name}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {error && (
              <p className="text-sm" style={{ color: '#ff4466' }}>
                {error instanceof Error ? error.message : 'Error creando proyecto'}
              </p>
            )}
          </div>

          {/* Footer */}
          <div className="flex gap-3 p-6 border-t flex-shrink-0" style={{ borderColor: '#1e2530' }}>
            <button
              type="button"
              onClick={onCerrar}
              className="flex-1 py-2.5 rounded-lg text-sm border transition-all hover:opacity-80"
              style={{ borderColor: '#1e2530', color: '#9ca3af' }}
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isPending || !nombre.trim() || !descripcion.trim() || !promptInicial.trim()}
              className="flex-1 py-2.5 rounded-lg text-sm font-semibold transition-all hover:opacity-90 disabled:opacity-40 flex items-center justify-center gap-2"
              style={{ backgroundColor: '#00d4ff', color: '#0a0c10' }}
            >
              {isPending ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Creando...
                </>
              ) : (
                'Crear Proyecto'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
