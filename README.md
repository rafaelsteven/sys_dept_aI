# SysDept AI

Sistema de departamento de sistemas virtual donde cada miembro del equipo es un agente de IA (Claude) con personalidad, rol y responsabilidades definidas. Los agentes se comunican en tiempo real, revisan código, aprueban commits y hacen push al repositorio del proyecto.

---

## Requisitos previos

| Herramienta | Versión mínima | Verificar |
|---|---|---|
| Python | 3.11+ | `python --version` |
| Node.js | 18+ | `node --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | 2.x | `git --version` |

---

## Configuración inicial (una sola vez)

### 1. Clonar el proyecto

```bash
git clone <url-de-este-repo>
cd equipoSitema
```

### 2. Crear la base de datos en PostgreSQL

```bash
# Opción A — desde la terminal
createdb sysdept

# Opción B — desde psql
psql -U postgres
CREATE DATABASE sysdept;
\q
```

### 3. Configurar el Backend

```bash
cd Backend

# Crear entorno virtual
python -m venv venv

# instalar
sudo apt install python3
sudo apt install python3.12-venv
sudo apt install python3-pip

# Activar entorno virtual
# Linux / macOS:
source venv/bin/activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo de configuración
cp .env.example .env
```

Edita `Backend/.env` con tus valores reales:

```env
# REQUERIDO — tu API Key de Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# PostgreSQL — ajusta usuario, contraseña y nombre de la base
DATABASE_URL=postgresql+asyncpg://postgres:tu_password@localhost:5432/sysdept

# Opcionales (tienen valores por defecto)
MODELO_AGENTE=claude-sonnet-4-6
MAX_TOKENS_AGENTE=2000
TURNOS_ANALISIS_INICIAL=6
RAMA_DESARROLLO_DEFAULT=dev
GIT_AUTOR_NOMBRE=SysDept AI
GIT_AUTOR_EMAIL=sysdept@ai.local
```

### 4. Aplicar migraciones de la base de datos

```bash
# Desde la carpeta Backend, con el venv activado
alembic upgrade head
```

Esto crea las tablas: `proyectos`, `agentes`, `mensajes`, `commits_pendientes`.

### 5. Configurar el Frontend

```bash
cd ../Frontend
npm install
```

---

## Arrancar el sistema

Necesitas **dos terminales** abiertas simultáneamente.

### Terminal 1 — Backend

```bash
cd Backend
source venv/bin/activate   # o venv\Scripts\activate en Windows

uvicorn main:app --reload --port 8000
```

Verás:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

Comprueba que está vivo: [http://localhost:8000/health](http://localhost:8000/health)

Documentación interactiva: [http://localhost:8000/docs](http://localhost:8000/docs)

### Terminal 2 — Frontend

```bash
cd Frontend
npm run dev
```

Verás:
```
  VITE v5.x  ready in 300ms
  ➜  Local:   http://localhost:5173/
```

Abre [http://localhost:5173](http://localhost:5173) en tu navegador.

---

## Flujo de uso

### Crear un proyecto

1. Haz clic en **"+ Nuevo Proyecto"**
2. Rellena el formulario:
   - **Nombre** y **descripción** del proyecto
   - **Prompt inicial** — describe con el máximo detalle qué quieres construir
   - **URL del repositorio** *(opcional)* — el equipo clonará el repo y trabajará sobre la rama `dev`
   - **PDFs** *(opcional)* — documentos de requerimientos (el texto se extrae automáticamente)
   - **Imágenes** *(opcional)* — mockups, wireframes

3. Al crear el proyecto:
   - El **Líder** (Carlos) y la **Arquitecta** (Ana) inician una sesión de análisis en `#arquitectura`
   - Tienen N turnos de conversación real (configurable con `TURNOS_ANALISIS_INICIAL`)
   - Al terminar, el Líder presenta el plan al canal `#general`
   - Si se proporcionó repo: se clona en background y se crea la rama `dev`

### Enviar tareas al equipo

Escribe en el input inferior de la vista de proyecto. El mensaje va al Líder, quien lo distribuye al equipo según los roles.

Para enviar directamente a un agente específico, usa el selector de destino (próximamente en UI).

### Agregar miembros al equipo

Haz clic en **"Agregar"** en el panel de equipo. Selecciona el rol, nombre y especialidad. El Líder hará un **briefing automático** al nuevo miembro.

### Flujo de código y commits

Cuando los agentes producen código, puedes enviarlo a revisión via API:

```bash
curl -X POST http://localhost:8000/api/proyectos/{proyecto_id}/codigo \
  -H "Content-Type: application/json" \
  -d '{
    "descripcion": "Implementa el endpoint de autenticación JWT",
    "archivos": [
      {
        "ruta": "src/api/auth.py",
        "contenido": "# código aquí..."
      }
    ]
  }'
```

El flujo automático es:

```
Código enviado
     ↓
  QA revisa (Diego)
  ¿APROBADO?
  ├── NO  → Rechazado, notificación por WebSocket
  └── SÍ  ↓
     Líder aprueba (Carlos)
     ¿APROBADO?
     ├── NO  → Rechazado, notificación por WebSocket
     └── SÍ  ↓
        commit + push → rama dev
        hash del commit por WebSocket
```

Ver todos los commits de un proyecto:

```bash
GET http://localhost:8000/api/proyectos/{proyecto_id}/commits
```

---

## Canales de comunicación

| Canal | Quién participa |
|---|---|
| `#general` | Todo el equipo |
| `#arquitectura` | Líder + Arquitecto (análisis inicial aquí) |
| `#backend` | Backend Devs + DBA |
| `#frontend` | Frontend Devs |
| `#qa` | QA Engineer |
| `#directo` | Conversaciones 1:1 entre agentes |

---

## Agentes disponibles

| Agente | Nombre | Rol |
|---|---|---|
| Líder | Carlos López | Coordina, distribuye tareas, aprueba commits |
| Arquitecto | Ana Reyes | Seguridad, escalabilidad, arquitectura |
| Backend Dev | Miguel Torres | APIs, lógica de negocio |
| Frontend Dev | Sofía Vargas | UI/UX, React |
| QA Engineer | Diego Méndez | Testing, revisión de código |
| DBA | Elena Castro | Esquemas PostgreSQL, queries, índices |

> El Líder y el Arquitecto están siempre presentes. El resto se agregan según el proyecto.

---

## Migraciones de base de datos

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head

# Ver estado actual
alembic current

# Ver historial
alembic history --verbose

# Generar nueva migración (al cambiar modelos)
alembic revision --autogenerate -m "descripcion del cambio"

# Rollback de una migración
alembic downgrade -1

# Rollback total (¡elimina todas las tablas!)
alembic downgrade base
```

---

## Variables de entorno — referencia completa

| Variable | Descripción | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | **Requerida.** Tu API Key de Anthropic | — |
| `DATABASE_URL` | URL de conexión a PostgreSQL (asyncpg) | `postgresql+asyncpg://postgres:password@localhost:5432/sysdept` |
| `MODELO_AGENTE` | Modelo Claude a usar | `claude-sonnet-4-6` |
| `MAX_TOKENS_AGENTE` | Tokens máximos por respuesta de agente | `2000` |
| `TURNOS_ANALISIS_INICIAL` | Turnos de conversación Líder↔Arquitecto al crear proyecto | `6` |
| `TURNOS_MAX_CONVERSACION` | Máximo de turnos en cualquier conversación | `8` |
| `VENTANA_HISTORIAL_MENSAJES` | Mensajes del historial que ve cada agente | `20` |
| `MAX_REINTENTOS_AGENTE` | Reintentos si falla la API de Anthropic | `2` |
| `SEGUNDOS_ESPERA_REINTENTO` | Espera entre reintentos (segundos) | `3` |
| `DIRECTORIO_UPLOADS` | Carpeta de archivos subidos y repos clonados | `./uploads` |
| `TAMANO_MAX_ARCHIVO_MB` | Tamaño máximo por archivo subido | `50` |
| `PUERTO_API` | Puerto del servidor FastAPI | `8000` |
| `ORIGENES_PERMITIDOS` | CORS origins permitidos (JSON list) | `["http://localhost:5173"]` |
| `RAMA_DESARROLLO_DEFAULT` | Rama que se crea al clonar un repo | `dev` |
| `GIT_AUTOR_NOMBRE` | Nombre del autor en los commits | `SysDept AI` |
| `GIT_AUTOR_EMAIL` | Email del autor en los commits | `sysdept@ai.local` |

---

## Estructura del proyecto

```
equipoSitema/
├── Backend/
│   ├── main.py                  Entrada FastAPI
│   ├── requirements.txt
│   ├── alembic.ini              Configuración de migraciones
│   ├── .env.example
│   ├── agents/                  Agentes de IA (uno por rol)
│   ├── core/
│   │   ├── configuracion.py     Toda la config (sin valores quemados)
│   │   ├── orquestador.py       Flujo de agentes + flujo de commits
│   │   └── bus_mensajes.py      WebSocket broadcaster
│   ├── db/
│   │   ├── base_datos.py        Modelos ORM + engine async
│   │   └── repositorio.py       Acceso a datos
│   ├── migrations/
│   │   └── versions/
│   │       ├── 0001_inicial_tablas.py
│   │       └── 0002_repositorio_y_commits.py
│   ├── models/                  Modelos Pydantic de dominio
│   ├── routes/                  Endpoints FastAPI
│   ├── servicios/
│   │   └── gestor_repositorio.py  Operaciones Git (clone, commit, push)
│   └── uploads/                 Archivos subidos + repos clonados
└── Frontend/
    └── src/
        ├── components/          Componentes React
        ├── hooks/               React Query + lógica de datos
        ├── pages/               Dashboard y VistaProyecto
        ├── store/               Zustand (estado UI)
        └── types/               Tipos TypeScript del dominio
```

---

## Solución de problemas frecuentes

**`connection refused` al iniciar el backend**
→ Verifica que PostgreSQL está corriendo: `pg_ctl status` o `sudo service postgresql status`

**`ANTHROPIC_API_KEY is missing`**
→ Asegúrate de que el archivo `.env` existe en `Backend/` y tiene la key correcta

**Error al clonar el repositorio**
→ Para repos privados, incluye el token en la URL: `https://token@github.com/usuario/repo.git`
→ O configura SSH key en el sistema antes de arrancar el backend

**El WebSocket no conecta**
→ Verifica que `VITE_WS_URL` apunta a `ws://localhost:8000` (no `http://`)

**`alembic: command not found`**
→ Activa el entorno virtual: `source venv/bin/activate`

---

## Licencia

MIT
