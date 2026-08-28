// ---------------------------------------------------------------------------
// LA FRANJA DE RELOJ — qué jornada es, y qué sigue sin cerrar.
//
// Es la espina del tablero y va arriba del todo, porque **las dos cosas que
// deciden una jugada no son magnitudes: son el plazo y los cabos sueltos.**
//
//   IZQUIERDA   jornada 3 de 5 · 13 de mayo · día
//   CENTRO      las cinco jornadas, cumplidas y pendientes
//   DERECHA     lo que sigue sin cerrar, contado
//
// SE HA QUEDADO EN LA MITAD, Y ESO ES LO QUE SE ARREGLÓ
// ----------------------------------------------------
// Aquí había además la hora de la ventana —«06:00 – 18:00 del 13 de mayo»—,
// las horas transcurridas —«+48 h»— y dos marcas por jornada, una de día y otra
// de noche. Diez marcas y tres líneas de cifras para decir algo que se dice con
// cinco marcas y una línea.
//
// Y ninguna de las cifras que se fueron cambiaba una decisión. Nadie ordena
// distinto por saber que la ventana termina a las 18:00: la fecha ficticia es
// un ancla —sitúa el episodio y le pone nombre a la jornada— y con eso cumple.
//
//     La fecha es un indicador, no un calendario.
//
// LO QUE NO SE FUE es lo único del reloj que sí cambia lo que se decide:
// **cuántas jornadas quedan.** Una concertación tarda dos en rendir; abrirla en
// la jornada 5 es no abrirla. «Jornada 3 de 5» es una presión, y no le dice a
// nadie qué hacer con ella.
//
// LA NOCHE SE VE DISTINTA, y no es decoración: de noche no se delibera, se
// sufre. Lo abierto por la fuerza vuelve a cerrarse y la consola no recibe
// órdenes. Si la franja cambia de color, nadie tiene que explicarlo dos veces.
//
// LOS CONTADORES DE «SIN CERRAR» son la pieza más delicada de todo el tablero.
// Enuncian un hecho —hay tres puntos que nadie ha mirado— y **jamás un remedio**.
// La distancia entre «3 puntos sin verificar» y «verifique N003» es la distancia
// entre un ejercicio y un tutorial.
// ---------------------------------------------------------------------------

import Ayuda from './Ayuda'
import { D } from '../definiciones.jsx'
import { FRANJA, rotulo } from '../etiquetas.jsx'

export default function Reloj({ reloj, pendientes }) {
  if (!reloj) return null
  const noche = reloj.franja === 'noche'
  const sinEmpezar = reloj.jornada === 0

  return (
    <div className={`reloj${noche ? ' es-noche' : ''}`}>
      {/* --- la jornada -------------------------------------------------- */}
      <div>
        <div className="eyebrow">
          {sinEmpezar
            ? 'Antes de la apertura'
            : `Jornada ${reloj.jornada} de ${reloj.jornadas_totales}`}
          <Ayuda etiqueta="Cómo corre el tiempo del ejercicio">{D.reloj}</Ayuda>
        </div>
        <div className="reloj-fecha">
          {reloj.fecha}
          <span className={`chip chip-${noche ? 'medio' : 'neutro'} reloj-franja`}>
            {rotulo(FRANJA, reloj.franja)}
          </span>
        </div>
        {!sinEmpezar && (
          <div className="reloj-restantes">
            {reloj.jornadas_restantes === 0
              ? 'última jornada'
              : reloj.jornadas_restantes === 1
                ? 'queda una jornada más'
                : `quedan ${reloj.jornadas_restantes} jornadas más`}
          </div>
        )}
      </div>

      {/* --- las cinco jornadas ------------------------------------------ */}
      <div>
        <div className="eyebrow" style={{ marginBottom: '0.4rem' }}>
          Mayo
          <Ayuda etiqueta="Qué representa esta línea">{D.linea_jornadas}</Ayuda>
        </div>
        <div className="jornadas">
          {reloj.linea.map(j => (
            <div key={j.jornada}
                 className={`jornada${j.estado === 'actual' ? ' es-actual' : ''}`}>
              <div className={`ventana ${j.estado}`} />
              <div className="jornada-fecha">{j.fecha}</div>
            </div>
          ))}
        </div>
      </div>

      {/* --- lo que sigue sin cerrar ------------------------------------- */}
      <div>
        <div className="eyebrow" style={{ marginBottom: '0.35rem' }}>
          Sin cerrar
          <Ayuda etiqueta="Qué cuentan estos números">{D.sin_cerrar}</Ayuda>
        </div>
        <div className="pendientes">
          {/* Fracción y no número suelto. `11` no dice si la sala avanza;
              `11/11` sí, y `4/11` dos jornadas después se lee sin explicar. */}
          {pendientes.map(p => (
            <div key={p.nombre} className={`pendiente${p.n ? ' hay' : ''}`}>
              <span>{p.nombre}</span>
              <span className="pendiente-n">
                {p.n}<span className="pendiente-de">/{p.de}</span>
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
