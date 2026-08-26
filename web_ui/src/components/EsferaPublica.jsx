// ---------------------------------------------------------------------------
// SUPERFICIE 3 · LA ESFERA PÚBLICA — como página propia.
//
// El tablero muestra lo que el Estado tiene por cierto; esta muestra lo que se
// dice. **La distancia entre las dos es el caso**, y solo se percibe si se ven a
// la vez.
//
// Esta ruta es para el montaje de DOS PROYECTORES. Con uno solo, la misma
// información vive como barra lateral del tablero — ver `Tablero.jsx`. Las dos
// presentaciones comparten `EsferaContenido`, así que no hay dos versiones que
// se puedan desincronizar.
//
// Lo que NO se hace nunca es ponerla en una pestaña del tablero: la divergencia
// solo se percibe simultánea, y una pestaña la elimina.
// ---------------------------------------------------------------------------

import EsferaContenido, { ENCUADRE } from './EsferaContenido'
import { Cargando, useDatos } from '../comun.jsx'

export default function EsferaPublica() {
  const { datos, error } = useDatos('/esfera', 4000)
  if (!datos) return <Cargando error={error} />

  const enc = ENCUADRE[datos.encuadre_dominante] || ENCUADRE.desorden

  return (
    <div className="pantalla">
      <header className="cabecera">
        <div>
          <span className="eyebrow">Esfera pública · proyectar</span>
          <h1>Lo que se dice</h1>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <span className="eyebrow">Encuadre dominante</span>
          <span className={`chip chip-${enc.chip}`}>{enc.texto}</span>
        </div>
      </header>

      <div className="cuerpo">
        <div className="rejilla" style={{ gridTemplateColumns: '1.4fr 1fr' }}>
          <EsferaContenido datos={datos} />
        </div>
      </div>
    </div>
  )
}
