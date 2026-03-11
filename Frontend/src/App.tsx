import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import VistaProyecto from './pages/VistaProyecto'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/proyecto/:proyectoId" element={<VistaProyecto />} />
    </Routes>
  )
}
