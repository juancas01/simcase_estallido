// ---------------------------------------------------------------------------
// EL ACCESO A LAS VISTAS PERSONALES — desde el tablero, sin estar en el tablero.
//
// EL PROBLEMA. Las ocho vistas privadas solo se alcanzaban desde la portada.
// Quien tenía el tablero delante y quería la suya debía retroceder, buscarla
// entre ocho tarjetas y volver. Con dos horas de ejercicio, ese rodeo se paga
// en minutos de sala.
//
// POR QUÉ NO ES UNA FILA DE PESTAÑAS. **El tablero es la superficie
// PROYECTADA.** Una fila de ocho pestañas encima de él añade tres cosas malas a
// la vez: ocupa el sitio de los datos, invita a la sala a pedir que se proyecte
// una vista personal —y ahí se acaba la asimetría de información que sostiene
// el ejercicio— y convierte un cambio de pantalla en un clic de distancia.
//
// LA SALIDA. Un control con nombre propio —«Vistas privadas»— en la línea de
// la versalita de la cabecera, encima del título y no dentro de él. Ocupa una
// línea que ya existía, no roba altura a los datos y dice exactamente lo que
// hace, de modo que quien nunca ha visto el sistema lo encuentra.
//
//     Una línea que ya estaba. Un clic para quien lo necesita, y ningún
//     panel abierto sobre los datos mientras nadie lo pida.
//
// Y COMO ESTO SE PULSA SOBRE UNA PANTALLA PROYECTADA, el panel lo dice: la vista
// se abre en esta misma pantalla. Es la advertencia que hace falta antes del
// clic, no después.
// ---------------------------------------------------------------------------

import { useEffect, useId, useRef, useState } from 'react'

import { ROLES } from '../comun.jsx'

/** Los frentes, tal como vienen del catálogo. Una lista propia aquí sería un
    catálogo duplicado, y un dato en dos sitios se desincroniza. */
const POR_FRENTE = ROLES.reduce((grupos, r) => {
  const g = grupos.find(x => x.frente === r.frente)
  if (g) g.roles.push(r)
  else grupos.push({ frente: r.frente, roles: [r] })
  return grupos
}, [])

export default function AccesoVistas() {
  const [abierto, setAbierto] = useState(false)
  const caja = useRef(null)
  const id = useId()

  // Se cierra con Escape y pulsando fuera. Un menú que solo cierra con su
  // propio tirador se queda abierto sobre los datos en cuanto alguien se
  // distrae, y esta pantalla está proyectada.
  useEffect(() => {
    if (!abierto) return

    const fuera = (e) => {
      if (!caja.current?.contains(e.target)) setAbierto(false)
    }
    const teclado = (e) => {
      if (e.key === 'Escape') setAbierto(false)
    }

    document.addEventListener('pointerdown', fuera)
    window.addEventListener('keydown', teclado)
    return () => {
      document.removeEventListener('pointerdown', fuera)
      window.removeEventListener('keydown', teclado)
    }
  }, [abierto])

  return (
    <div className="acceso" ref={caja}>
      <button
        type="button"
        className="enlace-superficie acceso-tirador"
        aria-expanded={abierto}
        aria-controls={abierto ? id : undefined}
        onClick={() => setAbierto(a => !a)}
      >
        Vistas privadas
        <span className="acceso-chevron" aria-hidden="true">▾</span>
      </button>

      {abierto && (
        <div className="acceso-panel" id={id}>
          <span className="eyebrow acceso-titulo">Abrir la vista de un rol</span>

          {POR_FRENTE.map(g => (
            <div key={g.frente} className="acceso-grupo">
              <span className="eyebrow acceso-frente">{g.frente}</span>
              {g.roles.map(r => (
                <a key={r.id} className="acceso-rol"
                   href={`/vista/${encodeURIComponent(r.id)}`}>
                  {r.nombre}
                </a>
              ))}
            </div>
          ))}

          <p className="acceso-pie">
            La vista se abre en esta misma pantalla.
          </p>
        </div>
      )}
    </div>
  )
}
