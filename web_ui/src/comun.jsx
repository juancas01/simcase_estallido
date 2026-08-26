// ---------------------------------------------------------------------------
// Lo que comparten las cuatro superficies.
//
// UNA REGLA: la interfaz lee de las MISMAS fuentes que el motor. Una lista
// propia en el frontend es un catálogo duplicado con otro nombre, y un dato en
// dos sitios se desincroniza. Siempre.
// ---------------------------------------------------------------------------

import { useCallback, useEffect, useRef, useState } from 'react'

export const ROLES = [
  { id: 'Presidente', nombre: 'Presidente de la República', frente: 'Estrategia' },
  { id: 'Interior', nombre: 'Ministro del Interior', frente: 'Estrategia' },
  { id: 'Alcalde', nombre: 'Alcalde de la ciudad epicentro', frente: 'Estrategia' },
  { id: 'Defensa', nombre: 'Ministro de Defensa', frente: 'Seguridad' },
  { id: 'Policía', nombre: 'Director General de la Policía', frente: 'Seguridad' },
  { id: 'Defensoría', nombre: 'Delegado de la Defensoría del Pueblo', frente: 'Seguridad' },
  { id: 'Transporte', nombre: 'Ministro de Transporte', frente: 'Logística' },
  { id: 'Minas', nombre: 'Ministro de Minas y Energía', frente: 'Logística' },
]

export const FASES = [
  { id: 'parte_privado', nombre: 'Parte privado', min: 1, congela: true },
  { id: 'apertura', nombre: 'Apertura', min: 1, congela: true },
  { id: 'deliberacion', nombre: 'Deliberación', min: 6, congela: true },
  { id: 'ordenes', nombre: 'Órdenes', min: 2.5, congela: false },
  { id: 'resolucion', nombre: 'Resolución', min: 1, congela: false },
  { id: 'consecuencias', nombre: 'Consecuencias', min: 1, congela: false },
  { id: 'registro', nombre: 'Registro', min: 0.5, congela: false },
]

export async function api(ruta, opciones) {
  const r = await fetch(`/api${ruta}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opciones,
  })
  if (!r.ok) {
    const detalle = await r.json().catch(() => ({}))
    throw new Error(detalle.detail || `Error ${r.status} en ${ruta}`)
  }
  return r.json()
}

/**
 * Refresca cada `ms`. Las pantallas proyectadas se refrescan solas; las
 * privadas también, porque nadie va a estar recargando en mitad de un turno.
 *
 * Que el dato cambie durante la DELIBERACIÓN es otro asunto: eso lo impide el
 * motor con `congelado`, no el frontend.
 */
export function useDatos(ruta, ms = 4000) {
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState(null)
  const vivo = useRef(true)

  const cargar = useCallback(async () => {
    try {
      const d = await api(ruta)
      if (vivo.current) { setDatos(d); setError(null) }
    } catch (e) {
      if (vivo.current) setError(e.message)
    }
  }, [ruta])

  useEffect(() => {
    vivo.current = true
    cargar()
    if (!ms) return () => { vivo.current = false }
    const t = setInterval(cargar, ms)
    return () => { vivo.current = false; clearInterval(t) }
  }, [cargar, ms])

  return { datos, error, recargar: cargar }
}

/** Arriba es mejor en las cuatro reservas. La presión en la calle va al revés. */
export function nivelReserva(v) {
  if (v >= 55) return 'bien'
  if (v >= 35) return 'medio'
  return 'mal'
}

export function nivelPresion(v) {
  if (v >= 75) return 'mal'
  if (v >= 55) return 'medio'
  return 'bien'
}

export const COLOR_NIVEL = {
  bien: 'var(--bien)',
  medio: 'var(--medio)',
  mal: 'var(--mal)',
}

export const COLOR_SEMAFORO = {
  verde: 'var(--bien)',
  ambar: 'var(--medio)',
  rojo: 'var(--mal)',
}

export function Cargando({ error }) {
  return (
    <div className="pantalla">
      <div className="cuerpo" style={{ display: 'grid', placeItems: 'center' }}>
        <p style={{ color: error ? 'var(--mal)' : 'var(--texto-3)' }}>
          {error
            ? `No se pudo leer del motor: ${error}`
            : 'Leyendo del motor…'}
        </p>
      </div>
    </div>
  )
}

export function Barra({ nombre, valor, nivel }) {
  return (
    <div className="reserva">
      <div className="reserva-fila">
        <span className="reserva-nombre">{nombre}</span>
        <span className="reserva-valor" style={{ color: COLOR_NIVEL[nivel] }}>
          {Math.round(valor)}
        </span>
      </div>
      <div className="barra">
        <div style={{ width: `${Math.max(0, Math.min(100, valor))}%`,
                      background: COLOR_NIVEL[nivel] }} />
      </div>
    </div>
  )
}
