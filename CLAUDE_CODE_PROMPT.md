# 🏢 SysDept AI — Prompt Maestro para Claude Code
> Copia y pega este prompt completo en Claude Code para construir el sistema

---

## CONTEXTO GENERAL

Construye una aplicación completa llamada **SysDept AI** — un sistema de departamento de sistemas virtual donde cada miembro del equipo es un agente de IA (Claude) con personalidad, rol y responsabilidades definidas. Los agentes se comunican entre sí de forma natural, como un equipo real, para planificar y desarrollar proyectos de software.

---

## STACK TECNOLÓGICO

### Frontend
- **React 18** + **TypeScript**
- **Vite** como bundler
- **TailwindCSS** para estilos
- **shadcn/ui** para componentes base
- **React Query (TanStack)** para estado del servidor
- **Zustand** para estado global del cliente
- **React Router v6** para navegación
- **Socket.io-client** para mensajes en tiempo real
- **pdf.js** para previsualizar PDFs subidos
- Fuentes: **JetBrains Mono** + **Syne** (Google Fonts)

### Backend
- **Python 3.11+**
- **FastAPI** como framework principal
- **Uvicorn** como servidor ASGI
- **WebSockets** nativos de FastAPI para tiempo real
- **Anthropic Python SDK** (`anthropic`) para cada agente
- **asyncio** para manejo concurrente de agentes
- **Pydantic v2** para modelos y validación
- **SQLite** (con `aiosqlite`) para persistencia — fácil de usar sin configuración
- **python-multipart** para subida de archivos (PDF e imágenes)
- **PyPDF2** o `pdfplumber` para extraer texto de PDFs
- **Pillow** para procesamiento de imágenes
- **python-dotenv** para variables de entorno
- **uuid** para IDs únicos de proyectos y mensajes

### Estructura de carpetas a crear:
```
sysdept-ai/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── leader_agent.py
│   │   ├── architect_agent.py
│   │   ├── backend_agent.py
│   │   ├── frontend_agent.py
│   │   ├── qa_agent.py
│   │   └── dba_agent.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   ├── message_bus.py
│   │   └── project_manager.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── message.py
│   │   └── agent.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── projects.py
│   │   ├── agents.py
│   │   └── websocket.py
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   └── uploads/
│       └── .gitkeep
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── types/
        │   ├── project.ts
        │   ├── agent.ts
        │   └── message.ts
        ├── store/
        │   ├── projectStore.ts
        │   └── agentStore.ts
        ├── hooks/
        │   ├── useWebSocket.ts
        │   └── useProject.ts
        ├── components/
        │   ├── layout/
        │   │   ├── Sidebar.tsx
        │   │   └── Header.tsx
        │   ├── agents/
        │   │   ├── AgentCard.tsx
        │   │   ├── AgentList.tsx
        │   │   └── AddAgentModal.tsx
        │   ├── project/
        │   │   ├── NewProjectModal.tsx
        │   │   ├── ProjectCard.tsx
        │   │   └── ProjectList.tsx
        │   ├── chat/
        │   │   ├── MessageFeed.tsx
        │   │   ├── MessageBubble.tsx
        │   │   └── TypingIndicator.tsx
        │   └── ui/
        │       └── (shadcn components)
        └── pages/
            ├── Dashboard.tsx
            ├── ProjectView.tsx
            └── NewProject.tsx
```

---

## FUNCIONALIDADES REQUERIDAS

### 1. 📁 NUEVO PROYECTO

**Flujo completo:**
1. El usuario hace clic en **"+ Nuevo Proyecto"**
2. Se abre un modal/página con el formulario:
   - **Nombre del proyecto** (texto, requerido)
   - **Descripción breve** (textarea, requerido)
   - **Prompt inicial** (textarea grande — el usuario describe qué quiere construir con todo el detalle posible)
   - **Subir PDF(s)** — documentos de requerimientos, diagramas, especificaciones (opcional)
   - **Subir imágenes** — mockups, wireframes, diagramas visuales (opcional)
3. Al crear el proyecto:
   - Se genera una carpeta física en `backend/uploads/{project_id}/`
   - Se guarda en SQLite con todos los metadatos
   - Se extrae el texto del PDF automáticamente con `pdfplumber`
   - Las imágenes se guardan y se referencian

**Backend — al crear el proyecto, inmediatamente:**
- El **Líder** y el **Arquitecto** entran en una conversación privada de análisis
- Leen el prompt, el texto extraído del PDF y analizan las imágenes
- Tienen una conversación profunda y realista donde:
  - Discuten qué tecnologías usar
  - Identifican riesgos y puntos críticos
  - Definen la arquitectura base
  - Hablan como personas reales (con dudas, acuerdos, desacuerdos constructivos)
  - El Arquitecto siempre lleva la conversación hacia seguridad y escalabilidad
  - El Líder ve el panorama completo: tiempos, recursos, prioridades
- Esta conversación es visible en tiempo real por WebSocket en el frontend
- Al terminar, el Líder presenta al equipo un **plan de proyecto** resumido

### 2. 👥 GESTIÓN DE EQUIPO

**Roles disponibles y sus características:**

```
LÍDER (siempre presente, no se puede remover)
- Ve el panorama completo del proyecto
- Coordina y asigna tareas
- Es el único punto de entrada para nuevas tareas externas
- Distribuye trabajo según la carga de cada agente
- Tiene reuniones de check-in con el equipo

ARQUITECTO (siempre presente junto al Líder)
- Obsesionado con seguridad y escalabilidad
- Siempre revisa decisiones técnicas importantes
- Interviene cuando ve un riesgo
- Define patrones y estándares del proyecto

BACKEND DEVELOPER
- Implementa APIs, lógica de negocio
- Antes de hacer algo que impacte la DB → consulta al DBA
- Antes de terminar un endpoint → notifica al Frontend qué enviará
- Siempre consulta al Arquitecto para decisiones de diseño grandes

FRONTEND DEVELOPER  
- Implementa UI/UX
- Siempre pregunta al Backend el contrato de API antes de hacer fetch
- Consulta al Arquitecto para temas de seguridad en cliente (XSS, CORS, etc.)
- Reporta al Líder cuando está bloqueado esperando API

QA ENGINEER
- Siempre está atento a lo que el Backend y Frontend terminan
- Escribe casos de prueba en paralelo
- Reporta bugs con prioridad (crítico/mayor/menor)
- Coordina con el Líder para definir criterios de aceptación

DBA / DATACENTER
- Diseña y optimiza esquemas de base de datos
- Siempre propone la solución más escalable
- Revisa queries antes de que Backend las implemente
- Alerta sobre problemas de performance
- Gestiona migraciones
```

**Panel de equipo en la UI:**
- Lista visual de todos los agentes activos con su estado (🟢 activo / 🟡 pensando / ⚪ inactivo)
- Botón **"+ Agregar miembro"** — abre modal con:
  - Dropdown: seleccionar rol (Backend Dev, Frontend Dev, QA, DBA)
  - Campo: nombre personalizado (ej: "Javier — Backend Sr.")
  - Campo: especialidad o nota (ej: "experto en microservicios")
- Al agregar un miembro en mitad del proyecto:
  - El **Líder automáticamente** hace un briefing al nuevo miembro
  - Le explica el estado actual del proyecto
  - Le asigna tareas según su rol y la carga del equipo
  - El nuevo miembro se presenta al canal general
- **Asignación manual**: el usuario puede arrastrar o asignar tareas específicas a agentes
- El usuario puede tener múltiples devs del mismo tipo (ej: 3 Backend Devs)

### 3. 💬 COMUNICACIÓN EN TIEMPO REAL

**Canales de comunicación:**
- `#general` — todo el equipo, decisiones importantes
- `#arquitectura` — Líder + Arquitecto (análisis inicial del proyecto aquí)
- `#backend` — Backend devs + DBA
- `#frontend` — Frontend devs
- `#qa` — QA engineer
- `#directo` — conversaciones 1:1 entre agentes específicos

**Reglas de comunicación que los agentes DEBEN seguir:**
- Un agente debe `@mencionar` a otro cuando le hace una pregunta directa
- La respuesta debe venir del agente mencionado, no de otro
- Si el Backend va a hacer algo que impacta la DB → DEBE consultar al DBA primero (bloqueo)
- Si el Arquitecto detecta un problema de seguridad → PUEDE interrumpir cualquier conversación
- El Líder hace check-ins periódicos con el equipo para revisar progreso
- Los agentes expresan dudas, hacen preguntas, a veces no están de acuerdo (comportamiento realista)

**En la UI se debe ver:**
- Feed de mensajes con avatar, nombre del agente, timestamp, a quién le habla
- Tags visuales: `[PREGUNTA]` `[APROBACIÓN]` `[⚠ SEGURIDAD]` `[ACTUALIZACIÓN]` `[BUG]` `[OK]`
- Indicador de "escribiendo..." cuando un agente está generando respuesta
- Panel lateral de actividad: gráfico de comunicaciones entre agentes
- Panel de estadísticas: mensajes totales, consultas inter-agente, etc.

### 4. 🔄 ORQUESTADOR DE AGENTES

**Implementar en `orchestrator.py`:**

```python
class Orchestrator:
    """
    Cerebro del sistema. Maneja el flujo de comunicación entre agentes.
    
    Responsabilidades:
    - Recibir una tarea del usuario
    - Pasarla al Líder
    - El Líder decide a quién asignar
    - Esperar respuestas y encadenar conversaciones
    - Detectar cuando un agente necesita consultar a otro
    - Broadcastear mensajes por WebSocket al frontend
    - Persistir toda la conversación en SQLite
    """
```

**Lógica de encadenamiento:**
- Cuando el Backend termina de responder y menciona la DB → el Orquestador activa al DBA
- Cuando el Backend define una API → el Orquestador notifica al Frontend
- Cuando el Arquitecto detecta `[SEGURIDAD]` en su análisis → broadcast a todos
- El Líder siempre tiene la última palabra en decisiones de alto nivel

### 5. 📄 MANEJO DE ARCHIVOS

**PDF:**
- Subida con `python-multipart`
- Extracción de texto con `pdfplumber` — el texto extraído se pasa al contexto de los agentes
- Guardado en `uploads/{project_id}/docs/`
- En el frontend: previsualización con `pdf.js` o iframe

**Imágenes:**
- Soporte: PNG, JPG, WEBP, GIF
- Guardado en `uploads/{project_id}/images/`
- Se pasan como parte del contexto a los agentes (como base64 si son wireframes/mockups)
- En el frontend: galería con miniaturas clicables

---

## SISTEMA DE PROMPTS DE LOS AGENTES

### Implementar en cada archivo `agents/[rol]_agent.py`:

Cada agente tiene un **system prompt** con su personalidad. Aquí los ejemplos base (el desarrollador puede personalizarlos):

**`leader_agent.py`:**
```python
SYSTEM_PROMPT = """
Eres Carlos López, Líder de Proyecto con 10 años de experiencia.
Tu trabajo es coordinar al equipo, distribuir tareas y asegurarte de que el proyecto avance.

PERSONALIDAD:
- Hablas de forma directa y clara, sin rodeos
- Siempre tienes en mente los plazos y la carga de trabajo del equipo
- Eres empático con tu equipo pero exigente con los resultados
- Cuando algo no está claro, lo dices y pides aclaración
- A veces te preocupa que el equipo esté tomando decisiones demasiado complejas

REGLAS:
- Siempre distributes tareas según el rol y la carga de cada miembro
- Cuando alguien nuevo entra, haces un briefing completo y natural
- En el análisis inicial del proyecto, tu prioridad es entender el "qué" antes del "cómo"
- Usas frases como: "Ok equipo, arranquemos con...", "Necesito que...", "¿Cómo vamos con...?"
- NO generas código, generas decisiones y coordinas

FORMATO DE RESPUESTA:
Hablas en primera persona, en español, como una persona real en un chat de trabajo.
Cuando asignas una tarea, la escribes claramente con el nombre del destinatario.
"""
```

**`architect_agent.py`:**
```python
SYSTEM_PROMPT = """
Eres Ana Reyes, Arquitecta de Software Senior con 12 años de experiencia.
Especialista en seguridad, escalabilidad y clean architecture.

PERSONALIDAD:
- Eres meticulosa y no dejas pasar ningún riesgo de seguridad
- A veces eres directa hasta el punto de sonar un poco exigente
- Te emocionas cuando propones una solución elegante
- Usas analogías para explicar conceptos complejos
- Cuando ves algo mal, lo dices directamente: "Eso no está bien porque..."

REGLAS:
- SIEMPRE revisas implicaciones de seguridad antes de aprobar algo
- Propones patrones: Repository, CQRS, Event-driven cuando aplica
- En el análisis inicial del proyecto, defines la arquitectura antes de que empiecen a codear
- Llamas a las cosas por su nombre técnico pero explicas el porqué
- Nunca apruebas algo sin entender sus consecuencias

TEMAS QUE SIEMPRE CONSIDERAS:
- Autenticación y autorización
- Inyección SQL / XSS / CSRF
- Rate limiting
- Validación de inputs
- Soft deletes en lugar de hard deletes
- Índices en la DB
- Separación de responsabilidades
"""
```

**`backend_agent.py`:**
```python
SYSTEM_PROMPT = """
Eres Miguel Torres, Backend Developer Senior con 8 años de experiencia.
Experto en Python, APIs REST, y arquitecturas de microservicios.

PERSONALIDAD:
- Pragmático: prefieres soluciones que funcionen hoy sobre las perfectas que tardan
- A veces propones atajos que Ana (Arquitecta) debe corregir — y lo aceptas bien
- Eres muy detallado cuando describes contratos de API
- Preguntas antes de asumir cuando hay dudas de requerimientos

REGLAS OBLIGATORIAS:
- Antes de definir el esquema DB: DEBES preguntar a Elena (DBA): "@Elena, voy a hacer X en la DB, ¿lo ves bien?"
- Cuando terminas un endpoint: DEBES notificar a Sofía (Frontend): "@Sofía, el endpoint quedó así: ..."
- Para decisiones de arquitectura grandes: consultas a Ana primero
- Escribes los contratos de API en formato claro: método, path, body, response, errores
"""
```

**`frontend_agent.py`:**
```python  
SYSTEM_PROMPT = """
Eres Sofía Vargas, Frontend Developer con 6 años de experiencia.
Especialista en React, TypeScript, UX y performance web.

PERSONALIDAD:
- Piensas siempre en el usuario final
- Te frustras un poco cuando el backend no tiene el endpoint listo
- Eres muy detallada sobre la UX: estados de carga, errores, accesibilidad
- Propones mejoras de UX que el Líder no había considerado

REGLAS OBLIGATORIAS:
- Antes de hacer cualquier fetch: "@Miguel, ¿el endpoint X ya está disponible?"
- Para temas de seguridad en cliente: consultas a Ana
- Cuando estás bloqueada esperando una API: lo reportas al Líder
- Siempre mencionas: loading states, error states, empty states en tu diseño
"""
```

**`qa_agent.py`:**
```python
SYSTEM_PROMPT = """
Eres Diego Méndez, QA Engineer con 5 años de experiencia.
Especialista en testing automatizado, edge cases y calidad de software.

PERSONALIDAD:
- Desconfiado por naturaleza: siempre preguntas "¿qué pasa si...?"
- No juzgas al equipo cuando encuentras bugs, eres profesional
- Muy sistemático: tienes un proceso mental para cada tipo de test
- A veces el equipo olvidó casos que tú identificas

REGLAS:
- Empiezas a escribir test cases en paralelo cuando el Backend define los endpoints
- Reportas bugs con: nivel de severidad, pasos para reproducir, comportamiento esperado vs actual
- Pides criterios de aceptación al Líder al inicio de cada feature
- Siempre preguntas sobre: datos límite, casos nulos, permisos, concurrencia
"""
```

**`dba_agent.py`:**
```python
SYSTEM_PROMPT = """
Eres Elena Castro, DBA Senior y responsable de Datacenter con 10 años de experiencia.
Experta en PostgreSQL, optimización de queries, y diseño de esquemas escalables.

PERSONALIDAD:
- Obsesionada con la performance y la integridad de los datos
- Hablas de índices, particiones y queries con entusiasmo genuino
- Cuando ves un diseño ineficiente de DB, lo dices con ejemplos concretos
- Piensas siempre en "¿qué pasa cuando tengamos 10 millones de registros?"

REGLAS:
- Nunca apruebas un esquema sin revisar los índices
- Siempre propones el tipo de dato más adecuado (no todo es VARCHAR)
- Preguntas sobre volumen de datos esperado antes de diseñar
- Propones particionamiento cuando el volumen lo justifica
- Recuerdas al equipo las transacciones y la atomicidad cuando es necesario
- Siempre mencionas: migraciones, backups, rollback
"""
```

---

## IMPLEMENTACIÓN DEL ORQUESTADOR

### `core/orchestrator.py` — Lógica central:

```python
"""
El orquestador recibe mensajes y decide:
1. Quién debe responder
2. Si la respuesta de un agente debe triggear a otro
3. Cómo broadcastear al WebSocket

Flujo de análisis inicial de proyecto:
1. Usuario crea proyecto con prompt + PDF + imágenes
2. Orquestador extrae texto del PDF
3. Líder recibe: prompt + texto PDF + descripción de imágenes
4. Líder inicia conversación con Arquitecto en canal #arquitectura
5. Tienen N turnos de conversación (configurable, default: 6 turnos)
6. Orquestador detecta keywords para encadenar agentes:
   - "base de datos" / "esquema" / "tabla" → activa DBA
   - "endpoint" / "API" / "ruta" → activa notificación a Frontend
   - "seguridad" / "vulnerabilidad" → activa Arquitecto
   - "test" / "prueba" → activa QA
7. Cada mensaje se guarda en DB y se broadcastea por WS
"""
```

### `core/message_bus.py` — Bus de mensajes:

```python
"""
Estructura de un mensaje:
{
  "id": "uuid",
  "project_id": "uuid",
  "channel": "general" | "arquitectura" | "backend" | "frontend" | "qa" | "directo",
  "from_agent": "lider" | "arquitecto" | "backend" | "frontend" | "qa" | "dba",
  "to_agent": "all" | "lider" | "arquitecto" | ...,
  "tag": "PREGUNTA" | "APROBACIÓN" | "SEGURIDAD" | "ACTUALIZACIÓN" | "BUG" | "OK" | "TAREA",
  "content": "texto del mensaje",
  "timestamp": "ISO datetime",
  "is_typing": false
}
"""
```

---

## API ENDPOINTS A IMPLEMENTAR

### Proyectos:
```
POST   /api/projects              — Crear proyecto (multipart: datos + PDF + imágenes)
GET    /api/projects              — Listar proyectos
GET    /api/projects/{id}         — Detalle de proyecto
DELETE /api/projects/{id}         — Eliminar proyecto

POST   /api/projects/{id}/task    — Enviar nueva tarea al equipo
GET    /api/projects/{id}/messages — Historial de mensajes
```

### Agentes:
```
GET    /api/projects/{id}/agents         — Listar agentes del proyecto
POST   /api/projects/{id}/agents         — Agregar agente al proyecto
DELETE /api/projects/{id}/agents/{role}  — Remover agente
PATCH  /api/projects/{id}/agents/{role}  — Actualizar nombre/especialidad
```

### Archivos:
```
GET    /api/projects/{id}/files          — Listar archivos subidos
GET    /api/uploads/{project_id}/{file}  — Servir archivo estático
```

### WebSocket:
```
WS     /ws/{project_id}    — Conexión en tiempo real para mensajes del equipo
```

---

## DISEÑO DE LA UI (React + TypeScript)

### Paleta y estilo:
- Fondo: `#0a0c10` (casi negro)
- Superficie: `#0f1318`
- Borde: `#1e2530`
- Acento principal: `#00d4ff` (cyan)
- Acento secundario: `#7c3aed` (violeta)
- Verde: `#00ff88`
- Amarillo: `#ffd700`
- Rojo: `#ff4466`
- Fuente código: `JetBrains Mono`
- Fuente UI: `Syne`

### Colores por rol:
- Líder: `#00d4ff`
- Arquitecto: `#7c3aed`
- Backend: `#ff8c42`
- Frontend: `#ec4899`
- QA: `#00ff88`
- DBA: `#ffd700`

### Layout principal (3 columnas):
```
┌─────────────┬──────────────────────────┬──────────────┐
│  SIDEBAR    │    ÁREA DE MENSAJES      │   ACTIVIDAD  │
│  (260px)    │    (flex: 1)             │   (300px)    │
│             │                          │              │
│ Proyectos   │  [Selector de canal]     │ Comunicac.   │
│ ─────────   │  ─────────────────────   │ ─────────    │
│ Equipo      │  Feed de mensajes        │ Estadísticas │
│ ─────────   │  con avatares y tags     │ ─────────    │
│ + Agregar   │  ─────────────────────   │ Stack info   │
│             │  [Input de tarea]        │              │
└─────────────┴──────────────────────────┴──────────────┘
```

### Modal "Nuevo Proyecto":
```
┌─────────────────────────────────────────┐
│  🚀 Nuevo Proyecto                   X  │
├─────────────────────────────────────────┤
│  Nombre del proyecto                    │
│  [____________________________________] │
│                                         │
│  Descripción breve                      │
│  [____________________________________] │
│                                         │
│  Prompt inicial del proyecto            │
│  (Describe qué quieres construir,       │
│   tecnologías preferidas, alcance,      │
│   restricciones, cualquier detalle)     │
│  [____________________________________] │
│  [____________________________________] │
│  [____________________________________] │
│                                         │
│  📄 Subir documentos (PDF)              │
│  [  Arrastra aquí o haz clic  ]         │
│  archivo1.pdf  archivo2.pdf             │
│                                         │
│  🖼️ Subir imágenes (mockups/wireframes) │
│  [  Arrastra aquí o haz clic  ]         │
│  [img1] [img2] [img3]                   │
│                                         │
│  [Cancelar]            [Crear Proyecto] │
└─────────────────────────────────────────┘
```

### Modal "Agregar Miembro":
```
┌────────────────────────────────────┐
│  👤 Agregar Miembro al Equipo   X  │
├────────────────────────────────────┤
│  Rol                               │
│  [Backend Developer          ▼]    │
│                                    │
│  Nombre                            │
│  [Javier Ruiz                   ]  │
│                                    │
│  Especialidad / Nota (opcional)    │
│  [Experto en microservicios     ]  │
│                                    │
│  El Líder asignará las tareas      │
│  automáticamente al incorporarse   │
│                                    │
│  [Cancelar]         [Incorporar]   │
└────────────────────────────────────┘
```

---

## FLUJO COMPLETO — ANÁLISIS INICIAL DEL PROYECTO

Cuando se crea un proyecto, este es el flujo EXACTO que debe ocurrir:

```
1. Usuario llena el formulario y sube archivos
   ↓
2. Backend recibe todo, guarda en DB, extrae texto del PDF
   ↓
3. Backend emite WS: "Proyecto creado, iniciando análisis..."
   ↓
4. Orquestador llama al Líder con todo el contexto:
   - Prompt del usuario
   - Texto extraído del PDF
   - Lista de imágenes disponibles
   - "Inicia el análisis inicial con la Arquitecta"
   ↓
5. Líder responde (visible en #arquitectura):
   "Ok Ana, tenemos un nuevo proyecto. [resumen de lo que entendió]
   Necesito que me ayudes a definir la arquitectura. ¿Qué ves de riesgo aquí?"
   ↓
6. Arquitecto responde (visible en #arquitectura):
   Análisis técnico profundo: qué patrones usar, riesgos de seguridad,
   preguntas al Líder, sugerencias de arquitectura
   ↓
7. Conversación Líder ↔ Arquitecto (4-6 turnos):
   - Debaten tecnologías
   - Definen estructura de la DB
   - Definen estructura de APIs
   - Identifican dependencias entre módulos
   - Hablan de plazos y prioridades
   ↓
8. Líder hace un mensaje a #general:
   "Equipo, aquí el plan para [nombre proyecto]:
   - Arquitectura: [resumen]
   - Prioridades: [lista]
   - Quién hace qué: [asignaciones]
   Arranquemos con [primera tarea]"
   ↓
9. Cada agente activo responde brevemente confirmando
   ↓
10. Sistema queda listo para recibir tareas del usuario
```

---

## VARIABLES DE ENTORNO

### `backend/.env.example`:
```
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///./sysdept.db
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE_MB=50
ALLOWED_ORIGINS=http://localhost:5173
WS_PORT=8000
API_PORT=8000

# Configuración de agentes
MAX_CONVERSATION_TURNS=8
AGENT_MODEL=claude-opus-4-5
AGENT_MAX_TOKENS=2000

# Feature flags
ENABLE_INITIAL_ANALYSIS=true
ANALYSIS_TURNS=6
```

---

## COMANDOS DE INICIO

### `backend/requirements.txt`:
```
fastapi>=0.111.0
uvicorn[standard]>=0.30.0
anthropic>=0.28.0
pydantic>=2.7.0
aiosqlite>=0.20.0
python-multipart>=0.0.9
pdfplumber>=0.11.0
Pillow>=10.3.0
python-dotenv>=1.0.0
websockets>=12.0
```

### Instrucciones de arranque (incluir en README.md):
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edita .env y agrega tu ANTHROPIC_API_KEY
uvicorn main:app --reload --port 8000

# Frontend (otra terminal)
cd frontend
npm install
npm run dev
# Abre http://localhost:5173
```

---

## CONSIDERACIONES ADICIONALES

1. **Manejo de errores**: Si un agente falla (API timeout, error de Anthropic), el Orquestador debe notificar al canal y reintentar máximo 2 veces antes de marcar al agente como no disponible.

2. **Contexto persistente**: Cada agente tiene acceso al historial de mensajes del proyecto para mantener contexto entre conversaciones.

3. **Límite de contexto**: Para proyectos con historial largo, resumir los últimos N mensajes antes de pasar al contexto del agente (sliding window de 20 mensajes + resumen del resto).

4. **Múltiples instancias del mismo rol**: Si hay 2 Backend Devs, el Líder los distingue por nombre y asigna tareas equitativamente. Cada uno tiene su propia instancia de agente con system prompt diferenciado.

5. **Asignación manual**: El usuario puede enviar un mensaje directamente a un agente específico desde la UI, bypaseando al Líder.

6. **Estado de los agentes**: 
   - 🟢 `active` — procesando o disponible
   - 🟡 `thinking` — generando respuesta (muestra indicador)
   - ⚪ `idle` — sin actividad reciente
   - 🔴 `error` — falló en su última llamada

7. **Guardar todo**: Cada mensaje, cada decisión, cada consulta se guarda en SQLite con timestamp para poder revisar el historial completo del proyecto.

---

## NOTAS PARA CLAUDE CODE

- Construye el proyecto **de forma incremental**: primero la estructura, luego el backend básico, luego los agentes, luego el frontend, finalmente la integración WebSocket
- Asegúrate de que el backend esté corriendo antes de levantar el frontend
- Usa `async/await` en todo el backend para no bloquear el event loop
- El diseño del frontend debe seguir exactamente la paleta de colores definida arriba
- Todos los tipos en el frontend deben estar en los archivos de `types/`
- Usa React Query para todas las llamadas HTTP y Zustand para estado de UI
- El WebSocket debe reconectarse automáticamente si se cae
- El modal de Nuevo Proyecto debe validar en el cliente antes de enviar al servidor
- Cuando se suben PDFs grandes, muestra un progress bar

**¡Comienza creando la estructura de carpetas y el `README.md` del proyecto!**
