# SysDept AI — Instrucciones para Claude Code

## Stack obligatorio
- Frontend: React 18 + TypeScript + Vite + TailwindCSS + shadcn/ui + Zustand + React Query
- Backend: Python 3.11 + FastAPI + asyncio + SQLite (aiosqlite)
- Agentes: Anthropic SDK, modelo `claude-sonnet-4-6`
- WebSockets nativos de FastAPI para tiempo real

---

## 🚫 REGLA NÚMERO 1 — NUNCA QUEMAR VALORES EN EL CÓDIGO

**Prohibido absolutamente:**
```python
# ❌ MAL — valores quemados
modelo = "claude-sonnet-4-6"
max_tokens = 2000
tiempo_expiracion = 3600
url_base = "http://localhost:8000"
carpeta_uploads = "./uploads"
turnos_conversacion = 6
```

**Siempre así:**
```python
# ✅ BIEN — todo desde configuración
from core.configuracion import configuracion

modelo = configuracion.modelo_agente
max_tokens = configuracion.max_tokens_agente
tiempo_expiracion = configuracion.tiempo_expiracion_jwt
```

**Toda configuración va en `backend/core/configuracion.py` usando Pydantic Settings:**
```python
from pydantic_settings import BaseSettings

class Configuracion(BaseSettings):
    # Anthropic
    anthropic_api_key: str
    modelo_agente: str = "claude-sonnet-4-6"
    max_tokens_agente: int = 2000
    
    # Conversación
    turnos_analisis_inicial: int = 6
    turnos_max_conversacion: int = 8
    ventana_historial_mensajes: int = 20
    
    # Archivos
    directorio_uploads: str = "./uploads"
    tamano_max_archivo_mb: int = 50
    extensiones_pdf_permitidas: list[str] = [".pdf"]
    extensiones_imagen_permitidas: list[str] = [".png", ".jpg", ".jpeg", ".webp", ".gif"]
    
    # Servidor
    puerto_api: int = 8000
    origenes_permitidos: list[str] = ["http://localhost:5173"]
    
    # Base de datos
    url_base_datos: str = "sqlite:///./sysdept.db"
    
    # Agentes — reintentos
    max_reintentos_agente: int = 2
    segundos_espera_reintento: int = 3

    class Config:
        env_file = ".env"

configuracion = Configuracion()
```

**En el frontend, todo en `src/configuracion/` o variables de entorno Vite:**
```typescript
// src/configuracion/api.ts
export const CONFIG = {
  urlApi: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  urlWebSocket: import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000',
  timeoutPeticion: Number(import.meta.env.VITE_TIMEOUT_MS ?? 10000),
  maxArchivosMb: Number(import.meta.env.VITE_MAX_ARCHIVO_MB ?? 50),
} as const;
```

---

## 🌐 IDIOMA — Español en funciones y variables de dominio

**Regla:** Todo lo que pertenece al **dominio del negocio** va en español.
La infraestructura técnica puede quedar en inglés si la librería lo requiere.

### Python — Backend:
```python
# ✅ Nombres de dominio en español
async def crear_proyecto(datos: DatosProyecto) -> Proyecto: ...
async def agregar_agente(proyecto_id: str, rol: RolAgente) -> Agente: ...
async def obtener_historial_mensajes(proyecto_id: str) -> list[Mensaje]: ...
async def analizar_documento_pdf(ruta_archivo: str) -> str: ...
async def iniciar_analisis_proyecto(proyecto: Proyecto) -> None: ...
async def asignar_tarea_a_agente(tarea: Tarea, agente: Agente) -> None: ...
async def transmitir_mensaje_websocket(mensaje: Mensaje) -> None: ...
async def resumir_historial(mensajes: list[Mensaje]) -> str: ...

# Variables de dominio en español
proyecto_activo = await repositorio.obtener_proyecto(proyecto_id)
agentes_disponibles = [a for a in equipo if a.estado == EstadoAgente.DISPONIBLE]
turno_actual = 0
mensaje_entrante = MessageBus.recibir()
texto_extraido = await extraer_texto_pdf(ruta)

# Modelos Pydantic en español
class Proyecto(BaseModel):
    id: str
    nombre: str
    descripcion: str
    prompt_inicial: str
    fecha_creacion: datetime
    estado: EstadoProyecto

class Mensaje(BaseModel):
    id: str
    proyecto_id: str
    canal: CanalComunicacion
    agente_origen: RolAgente
    agente_destino: RolAgente | Literal["todos"]
    etiqueta: EtiquetaMensaje
    contenido: str
    marca_tiempo: datetime
```

### TypeScript — Frontend:
```typescript
// ✅ Nombres de dominio en español
const obtenerProyectos = async (): Promise<Proyecto[]> => { ... }
const crearProyecto = async (datos: DatosNuevoProyecto) => { ... }
const agregarMiembro = async (proyectoId: string, miembro: NuevoMiembro) => { ... }
const manejarMensajeWebSocket = (evento: MessageEvent) => { ... }

// Tipos en español
interface Proyecto {
  id: string
  nombre: string
  descripcion: string
  promptInicial: string
  fechaCreacion: string
  estado: EstadoProyecto
}

interface Agente {
  id: string
  nombre: string
  rol: RolAgente
  estado: EstadoAgente
  especialidad?: string
}

// Hooks en español
const useConexionWebSocket = (proyectoId: string) => { ... }
const useGestionAgentes = () => { ... }
const useHistorialMensajes = (proyectoId: string) => { ... }
```

**Excepciones permitidas en inglés:** nombres de librerías, hooks de React (`useState`, `useEffect`), parámetros internos de librerías externas, variables de iteración cortas (`i`, `j`), clases CSS de Tailwind.

---

## 🏗️ PRINCIPIOS SOLID — Obligatorios en todo el código

### S — Responsabilidad Única
Cada clase/función hace UNA sola cosa. Si una función hace más de una cosa, se divide.

```python
# ❌ MAL — hace demasiado
async def procesar_proyecto(datos, archivo_pdf, imagenes):
    # guarda en DB
    # extrae texto del PDF
    # sube imágenes
    # inicia los agentes
    # envía WebSocket

# ✅ BIEN — responsabilidades separadas
async def guardar_proyecto(datos: DatosProyecto) -> Proyecto: ...
async def extraer_texto_pdf(ruta: str) -> str: ...
async def guardar_imagenes(archivos: list, proyecto_id: str) -> list[str]: ...
async def iniciar_equipo(proyecto: Proyecto) -> None: ...
async def notificar_creacion(proyecto_id: str) -> None: ...
```

### O — Abierto/Cerrado
Los agentes se extienden, no se modifican. Usar herencia desde `AgenteBase`.

```python
# ✅ BIEN — extender, no modificar
class AgenteBase:
    async def pensar(self, contexto: ContextoAgente) -> str: ...
    async def responder(self, mensaje: str) -> Mensaje: ...

class AgenteBackend(AgenteBase):
    # Extiende, no sobreescribe la lógica base
    async def notificar_contrato_api(self, endpoint: str) -> None: ...
    async def consultar_dba(self, esquema: str) -> None: ...
```

### L — Sustitución de Liskov
Cualquier agente puede sustituir a `AgenteBase` sin romper el sistema.
El Orquestador trabaja siempre con `AgenteBase`, nunca con tipos concretos.

```python
# ✅ BIEN — el orquestador no sabe qué tipo de agente es
class Orquestador:
    def __init__(self, agentes: list[AgenteBase]):
        self.agentes = agentes  # No importa si son Backend, QA, DBA...
```

### I — Segregación de Interfaces
Interfaces pequeñas y específicas, no una interfaz gigante.

```python
# ✅ BIEN — interfaces específicas
class PuedeConsultarDB(Protocol):
    async def consultar_esquema(self, tabla: str) -> str: ...

class PuedeRevisarSeguridad(Protocol):
    async def auditar_endpoint(self, ruta: str) -> list[str]: ...

class PuedeNotificarFrontend(Protocol):
    async def publicar_contrato_api(self, contrato: ContratoAPI) -> None: ...
```

### D — Inversión de Dependencias
Depender de abstracciones, nunca de implementaciones concretas.

```python
# ❌ MAL — depende de implementación concreta
class Orquestador:
    def __init__(self):
        self.repositorio = RepositorioSQLite()  # acoplado

# ✅ BIEN — depende de abstracción
class Orquestador:
    def __init__(self, repositorio: RepositorioBase, bus: BusMensajesBase):
        self.repositorio = repositorio
        self.bus = bus
```

---

## ✅ BUENAS PRÁCTICAS GENERALES

### Funciones cortas y descriptivas
```python
# ❌ MAL
async def handle(x, y, z): ...

# ✅ BIEN
async def asignar_tarea_segun_carga(
    tarea: Tarea,
    agentes_disponibles: list[AgenteBase],
    criterio: CriterioAsignacion = CriterioAsignacion.MENOR_CARGA
) -> AgenteBase: ...
```

### Enums para valores fijos, nunca strings sueltos
```python
# ❌ MAL
agente.estado = "thinking"
mensaje.canal = "general"

# ✅ BIEN
class EstadoAgente(str, Enum):
    ACTIVO = "activo"
    PENSANDO = "pensando"
    INACTIVO = "inactivo"
    ERROR = "error"

class CanalComunicacion(str, Enum):
    GENERAL = "general"
    ARQUITECTURA = "arquitectura"
    BACKEND = "backend"
    FRONTEND = "frontend"
    QA = "qa"
    DIRECTO = "directo"

class EtiquetaMensaje(str, Enum):
    PREGUNTA = "PREGUNTA"
    APROBACION = "APROBACIÓN"
    SEGURIDAD = "SEGURIDAD"
    ACTUALIZACION = "ACTUALIZACIÓN"
    BUG = "BUG"
    OK = "OK"
    TAREA = "TAREA"
```

### Constantes agrupadas, nunca sueltas
```python
# ❌ MAL — constantes flotando en el código
TURNOS = 6
MAX = 2000
ESPERA = 3

# ✅ BIEN — agrupadas por dominio en configuracion.py o en un archivo constantes.py
class ConstantesAgente:
    ROLES_SIEMPRE_PRESENTES = [RolAgente.LIDER, RolAgente.ARQUITECTO]
    MENSAJES_SYSTEM_POR_ROL = {
        RolAgente.LIDER: "Eres Carlos López, Líder de Proyecto...",
        RolAgente.ARQUITECTO: "Eres Ana Reyes, Arquitecta Senior...",
    }
```

### Manejo de errores explícito con excepciones propias
```python
# ✅ BIEN — excepciones de dominio
class SysDeptError(Exception): pass
class ProyectoNoEncontrado(SysDeptError): pass
class AgenteNoDisponible(SysDeptError): pass
class ErrorExtraccionPDF(SysDeptError): pass
class LimiteArchivoExcedido(SysDeptError): pass
```

### TypeScript — tipos estrictos, sin `any`
```typescript
// ❌ MAL
const manejarRespuesta = (datos: any) => { ... }

// ✅ BIEN
const manejarRespuesta = (datos: RespuestaAgente): void => { ... }

// Usar tipos discriminados para estados
type EstadoMensaje =
  | { tipo: 'enviando' }
  | { tipo: 'entregado'; marcaTiempo: string }
  | { tipo: 'error'; mensaje: string }
```

### Comentarios solo cuando el porqué no es obvio
```python
# ❌ MAL — comenta el qué (ya se ve en el código)
# Incrementa el turno
turno_actual += 1

# ✅ BIEN — comenta el porqué
# Limitamos a ventana_historial_mensajes para no exceder el contexto
# máximo del modelo. El resto se resume antes de pasar al agente.
historial_reciente = mensajes[-configuracion.ventana_historial_mensajes:]
```

### Async en todo el backend
```python
# ❌ MAL — bloquea el event loop
def obtener_proyecto(id: str) -> Proyecto:
    return db.query(...)

# ✅ BIEN
async def obtener_proyecto(id: str) -> Proyecto:
    return await db.fetch_one(...)
```

---

## 📁 ESTRUCTURA DE ARCHIVOS — Convenciones de nombres

```
backend/
├── agents/          # snake_case: lider_agent.py, backend_agent.py
├── core/            # snake_case: orquestador.py, configuracion.py
├── models/          # snake_case: proyecto.py, mensaje.py
├── routes/          # snake_case: proyectos.py, agentes.py
└── db/              # snake_case: base_datos.py, repositorio.py

frontend/src/
├── types/           # PascalCase interfaces: Proyecto.ts, Agente.ts
├── store/           # camelCase: proyectoStore.ts, agenteStore.ts
├── hooks/           # camelCase con use: useConexionWS.ts, useProyecto.ts
├── components/      # PascalCase: AgentCard.tsx, MensajeBurbuja.tsx
└── configuracion/   # camelCase: api.ts, websocket.ts
```

---

## 🔒 SEGURIDAD — Reglas del Arquitecto aplicadas al código

- Nunca loggear la `ANTHROPIC_API_KEY` ni ningún secreto
- Validar tamaño y extensión de archivos antes de guardarlos
- Sanitizar el texto extraído de PDFs antes de pasarlo al modelo
- Los IDs de proyecto son UUID, nunca auto-incrementales expuestos
- El endpoint de archivos estáticos valida que el `project_id` existe en DB

---

## 🚀 FLUJO DE DESARROLLO

Cuando Claude Code agregue nueva funcionalidad, debe seguir este orden:
1. Modelo/tipo (Pydantic o TypeScript interface)
2. Repositorio/servicio (lógica de negocio)
3. Ruta/endpoint (FastAPI o React component)
4. Integración WebSocket si aplica
5. Actualizar README si cambia algo importante

**Nunca saltarse el paso 1.** Los tipos primero, siempre.