// ---------------------------------------------------------------------------
// LA AYUDA CONTEXTUAL — un signo de interrogación y nada más.
//
// El principio: **la pantalla muestra el dato; la explicación se pide.** Una
// glosa impresa bajo cada cifra la lee todo el mundo la primera vez y nadie la
// segunda, pero sigue ocupando el sitio del dato en todas las demás. En una
// pantalla proyectada a una sala eso es caro: el ojo tiene que atravesar texto
// que ya conoce para llegar al número que cambió.
//
// De modo que la glosa se retira a un globo y deja una marca de 14 píxeles.
// Quien la necesita la pide; quien no, lee el tablero limpio.
//
// TRES DECISIONES DE CONSTRUCCIÓN
//   1 · No es el atributo `title` del navegador. Ese tarda medio segundo en
//       aparecer, no se puede dar formato y no llega por teclado.
//   2 · Se monta en `document.body` mediante un portal, con posición fija. Sin
//       eso lo recortan el desplazamiento de la barra lateral y el de las
//       tablas anchas, que es justo donde más falta hace.
//   3 · Abre con el puntero, con el foco del teclado y con un toque; cierra
//       también con Escape.
// ---------------------------------------------------------------------------

import { useCallback, useId, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

const MARGEN = 10        // respiro mínimo contra el borde de la ventana
const SEPARACION = 9     // hueco entre la marca y el globo

export default function Ayuda({ children, etiqueta = 'Ver la definición' }) {
  const [visible, setVisible] = useState(false)
  const [pos, setPos] = useState(null)
  const marca = useRef(null)
  const globo = useRef(null)
  const id = useId()

  // Encima de la marca si cabe; debajo si no. Y siempre dentro de la ventana:
  // un globo medio salido de la pantalla no explica nada.
  const colocar = useCallback(() => {
    const m = marca.current?.getBoundingClientRect()
    const g = globo.current?.getBoundingClientRect()
    if (!m || !g) return

    const centro = m.left + m.width / 2
    const izq = Math.max(
      MARGEN,
      Math.min(centro - g.width / 2, window.innerWidth - g.width - MARGEN),
    )

    let arriba = m.top - g.height - SEPARACION
    let debajo = false
    if (arriba < MARGEN) {
      arriba = m.bottom + SEPARACION
      debajo = true
    }

    setPos({
      izq, arriba, debajo,
      flecha: Math.max(12, Math.min(centro - izq, g.width - 12)),
    })
  }, [])

  useLayoutEffect(() => {
    if (!visible) { setPos(null); return }
    colocar()

    const teclado = (e) => { if (e.key === 'Escape') setVisible(false) }
    // `true` en el scroll: hace falta la fase de captura para enterarse del
    // desplazamiento de la barra lateral, que no burbujea hasta la ventana.
    window.addEventListener('scroll', colocar, true)
    window.addEventListener('resize', colocar)
    window.addEventListener('keydown', teclado)
    return () => {
      window.removeEventListener('scroll', colocar, true)
      window.removeEventListener('resize', colocar)
      window.removeEventListener('keydown', teclado)
    }
  }, [visible, colocar])

  return (
    <>
      <button
        ref={marca}
        type="button"
        className="ayuda"
        aria-label={etiqueta}
        aria-describedby={visible ? id : undefined}
        onPointerEnter={(e) => { if (e.pointerType === 'mouse') setVisible(true) }}
        onPointerLeave={(e) => { if (e.pointerType === 'mouse') setVisible(false) }}
        onFocus={() => setVisible(true)}
        onBlur={() => setVisible(false)}
        onClick={() => setVisible(v => !v)}
      >
        ?
      </button>

      {visible && createPortal(
        <div
          ref={globo}
          id={id}
          role="tooltip"
          className={`ayuda-globo${pos?.debajo ? ' debajo' : ''}`}
          style={{
            left: pos?.izq ?? 0,
            top: pos?.arriba ?? 0,
            opacity: pos ? 1 : 0,
            '--flecha': `${pos?.flecha ?? 0}px`,
          }}
        >
          {children}
        </div>,
        document.body,
      )}
    </>
  )
}

/** Un encabezado de tarjeta con su marca de ayuda. El título queda desnudo: la
    explicación que antes iba en el propio título vive ahora en el globo. */
export function Titulo({ children, ayuda, etiqueta }) {
  return (
    <h2>
      {children}
      {ayuda && <Ayuda etiqueta={etiqueta || `Definición de ${children}`}>{ayuda}</Ayuda>}
    </h2>
  )
}
