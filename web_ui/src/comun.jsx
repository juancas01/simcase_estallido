// ---------------------------------------------------------------------------
// Lo que comparten las cuatro superficies.
//
// UNA REGLA: la interfaz lee de las MISMAS fuentes que el motor. Una lista
// propia en el frontend es un catálogo duplicado con otro nombre, y un dato en
// dos sitios se desincroniza. Siempre.
// ---------------------------------------------------------------------------

import { useCallback, useEffect, useRef, useState } from 'react'

import Ayuda from './components/Ayuda'

export const ROLES = [
  { id: 'Presidente', nombre: 'Presidente de la República', frente: 'Estrategia' },
  { id: 'Interior', nombre: 'Ministro del Interior', frente: 'Estrategia' },
  { id: 'Alcalde', nombre: 'Alcalde de la ciudad epicentro', frente: 'Estrategia' },
  { id: 'Defensa', nombre: 'Ministro de Defensa', frente: 'Seguridad' },
  { id: 'Policía', nombre: 'Director General de la Policía', frente: 'Seguridad' },
  { id: 'Transporte', nombre: 'Ministro de Transporte', frente: 'Logística' },
  { id: 'Agricultura', nombre: 'Ministro de Agricultura y Desarrollo Rural', frente: 'Logística' },
]

// LA TABLA DE FASES NO ESTÁ AQUÍ. Vivía duplicada —una copia en este archivo y
// otra en `api/main.py`— y desde que el reloj corre solo, esa copia decidía la
// duración de los tramos en la pantalla mientras la otra los decidía en el
// servidor. El motor la sirve dentro de `cronometro` en cada respuesta, y
// `Cronometro.jsx` dibuja lo que llega.

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
 * privadas también, porque nadie va a estar recargando en mitad de una jornada.
 *
 * DOS SEGUNDOS Y NO CUATRO. Con el reloj de sala llevando el ritmo, el paso de
 * día a noche es el instante en que la consola se apaga y aparecen las
 * consecuencias: cuatro segundos de retraso ahí se ven desde la última fila.
 */
export function useDatos(ruta, ms = 2000) {
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

/** Umbrales de color. Arriba es mejor en las cuatro métricas. */
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

/**
 * La pantalla mientras no hay datos. **No puede parecerse a una pantalla en
 * blanco**, porque es exactamente lo que ve alguien cuyo dispositivo no alcanza
 * al servidor — y en una sala con nueve tabletas eso pasa.
 *
 * Antes era una línea gris claro sobre fondo oscuro que decía «Leyendo del
 * motor…». A dos metros y en un móvil, indistinguible de una pantalla muerta.
 * Ahora dice qué se está pidiendo, desde dónde, y qué hacer si no llega.
 */
export function Cargando({ error, ruta }) {
  return (
    <div className="pantalla">
      <div className="cuerpo cargando">
        <div className={`cargando-caja${error ? ' con-error' : ''}`}>
          <div className="eyebrow">
            {error ? 'Sin conexión con el motor' : 'Conectando con el motor'}
          </div>
          <p className="cargando-titulo">
            {error ? 'Esta pantalla no está recibiendo datos' : 'Leyendo…'}
          </p>
          {error && (
            <>
              <p className="cargando-detalle">{error}</p>
              <p className="cargando-detalle">
                El servidor del ejercicio corre en el equipo de la consola. Si
                esta pantalla está en otro dispositivo, tiene que alcanzarlo por
                la misma red.
              </p>
            </>
          )}
          {ruta && <code className="cargando-ruta">/api{ruta}</code>}
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// LA TENDENCIA — la dirección, sin la cifra.
//
// En el tablero de métricas no sale ni un número, y eso incluye el delta: `▼9`
// es tan numérico como `41`. Lo que queda es la flecha, que dice lo único que
// hace falta saber sin abrir una discusión sobre magnitudes: **esto se movió, y
// en esta dirección.**
//
// Si no se movió, NO se dibuja nada. Una fila de guiones en una pared es ruido,
// y la ausencia de marca ya significa «esto sigue igual».
// ---------------------------------------------------------------------------

export function Tendencia({ valor, sentido = 'arriba_mejor', umbral = 1 }) {
  if (valor === undefined || valor === null) return null
  const v = Number(valor)
  if (!Number.isFinite(v) || Math.abs(v) < umbral) return null

  const sube = v > 0
  const bueno = sentido === 'arriba_mejor' ? sube : !sube
  return (
    <span className={`tendencia tendencia-${bueno ? 'bien' : 'mal'}`}
          aria-label={sube ? 'subió' : 'bajó'}>
      {sube ? '▲' : '▼'}
    </span>
  )
}

/**
 * Cuánto se movió la magnitud, con su cifra. **Solo para las vistas privadas**,
 * que son el sitio del grano fino. En el tablero manda `Tendencia`.
 */
export function Delta({ valor, sentido = 'arriba_mejor', decimales = 0 }) {
  if (valor === undefined || valor === null) return null
  const v = Number(valor)
  if (!Number.isFinite(v) || Math.abs(v) < 0.05) return null

  const sube = v > 0
  const bueno = sentido === 'arriba_mejor' ? sube : !sube
  return (
    <span className={`delta delta-${bueno ? 'bien' : 'mal'}`}>
      {sube ? '▲' : '▼'}{Math.abs(v).toFixed(decimales)}
    </span>
  )
}

// ---------------------------------------------------------------------------
// EL MEDIDOR — una escala de cinco pasos, y ni un número.
//
// LAS MÉTRICAS DEL TABLERO NO LLEVAN CIFRA, y no es una simplificación: es lo
// que impide que la sala juegue contra el marcador. Con `Legitimidad 52` en la
// pared, la conversación se vuelve aritmética —«subimos tres, podemos gastar
// cuatro»— y el ejercicio deja de ser sobre conducción para ser sobre
// puntuación. Ninguna de estas cuatro magnitudes es medible en la realidad con
// dos cifras significativas, y fingir que lo es enseña algo falso.
//
//     Un nivel se interpreta. Un número se optimiza.
//
// Cinco pasos y no tres: con tres, la mitad del tablero vive siempre en
// «medio» y el movimiento deja de verse. Con siete, la sala vuelve a contar.
// ---------------------------------------------------------------------------

export const NIVELES = ['muy bajo', 'bajo', 'medio', 'alto', 'muy alto']

/** De 0–100 al peldaño que le toca. Los cortes son los cinco quintos. */
export function peldano(valor) {
  const v = Math.max(0, Math.min(100, Number(valor) || 0))
  return Math.min(NIVELES.length - 1, Math.floor(v / 20))
}

/** El color del peldaño, según qué extremo sea el bueno. */
export function colorPeldano(i, sentido = 'arriba_mejor') {
  const orden = sentido === 'arriba_mejor'
    ? ['mal', 'mal', 'medio', 'bien', 'bien']
    : ['bien', 'bien', 'medio', 'mal', 'mal']
  return COLOR_NIVEL[orden[i]]
}

export function Medidor({ nombre, valor, sentido = 'arriba_mejor', ayuda, delta }) {
  const i = peldano(valor)
  const color = colorPeldano(i, sentido)

  return (
    <div className="medidor">
      <div className="medidor-fila">
        <span className="medidor-nombre">
          {nombre}
          {ayuda && <Ayuda etiqueta={`Definición de ${nombre}`}>{ayuda}</Ayuda>}
        </span>
        <span className="medidor-nivel" style={{ color }}>
          {NIVELES[i]}
          <Tendencia valor={delta} sentido={sentido} />
        </span>
      </div>
      <div className="medidor-escala" role="img"
           aria-label={`${nombre}: ${NIVELES[i]} de ${NIVELES.length} niveles`}>
        {NIVELES.map((_, k) => (
          <span key={k} className={k <= i ? 'peldano lleno' : 'peldano'}
                style={k <= i ? { background: color } : undefined} />
        ))}
      </div>
    </div>
  )
}

/** La barra con cifra. Sigue viva en las vistas privadas y en la esfera. */
export function Barra({ nombre, valor, nivel, ayuda, delta, sentido }) {
  return (
    <div className="reserva">
      <div className="reserva-fila">
        <span className="reserva-nombre">
          {nombre}
          {ayuda && <Ayuda etiqueta={`Definición de ${nombre}`}>{ayuda}</Ayuda>}
        </span>
        <span className="reserva-valor" style={{ color: COLOR_NIVEL[nivel] }}>
          {Math.round(valor)}
          <Delta valor={delta} sentido={sentido} />
        </span>
      </div>
      <div className="barra">
        <div style={{ width: `${Math.max(0, Math.min(100, valor))}%`,
                      background: COLOR_NIVEL[nivel] }} />
      </div>
    </div>
  )
}
