export const CONFIG = {
  urlApi: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  urlWebSocket: import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000',
  timeoutPeticion: Number(import.meta.env.VITE_TIMEOUT_MS ?? 10000),
  maxArchivosMb: Number(import.meta.env.VITE_MAX_ARCHIVO_MB ?? 50),
} as const
