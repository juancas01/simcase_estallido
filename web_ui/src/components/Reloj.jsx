// ---------------------------------------------------------------------------
// LA FRANJA DE RELOJ — qué hora es, cuánto queda, qué sigue sin cerrar.
//
// Es la espina del tablero y va arriba del todo, porque **las tres cosas que
// deciden una jugada no son magnitudes: son el plazo y los cabos sueltos.**
//
//   IZQUIERDA   la fecha y la franja · 12 de mayo, 06:00–18:00, día
//   CENTRO      las nueve ventanas del ejercicio, cumplidas y pendientes
//   DERECHA     lo que sigue sin cerrar, contado
//
// POR QUÉ EL PLAZO IMPORTA TANTO COMO EL DATO
// -------------------------------------------
// Una concertación tarda dos turnos en rendir. Abrirla en la jornada 5 es no
// abrirla. Con cinco jornadas, **saber cuántas quedan cambia qué se decide**, y
// hasta ahora el tablero decía «Turno 3» sin decir de cuántos.
//
// «Turno 3» es neutro. «Jornada 3 de 5, quedan dos» es una presión — y no le
// dice a nadie qué hacer con ella.
//
// LA NOCHE SE VE DISTINTA, y no es decoración: de noche no se delibera, se
// sufre. Lo abierto por la fuerza vuelve a cerrarse, el riesgo se multiplica por
// 1,6 y la sala no puede intervenir. Si la franja cambia de color, nadie tiene
// que explicarlo dos veces.
//
// LOS CONTADORES DE «SIN CERRAR» son la pieza más delicada de todo el tablero.
// Enuncian un hecho —hay tres puntos que nadie ha mirado— y **jamás un remedio**.
// La distancia entre «3 puntos sin verificar» y «verifique P7» es la distancia
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
      {/* --- la fecha --------------------------------------------------- */}
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
        <div className="reloj-horas">
          {reloj.hora_inicio} – {reloj.hora_fin}
          {reloj.cruza_medianoche && ` del ${reloj.fecha_fin}`}
          <span className="reloj-transcurrido">
            +{reloj.horas_transcurridas} h
          </span>
        </div>
      </div>

      {/* --- las nueve ventanas ----------------------------------------- */}
      <div>
        <div className="eyebrow" style={{ marginBottom: '0.4rem' }}>
          Mayo
          <Ayuda etiqueta="Qué representa esta línea">{D.linea_jornadas}</Ayuda>
        </div>
        <div className="jornadas">
          {reloj.linea.map(j => (
            <div key={j.jornada}
                 className={`jornada${j.dia === 'actual' || j.noche === 'actual'
                   ? ' es-actual' : ''}`}>
              <div className="jornada-barras">
                <span className={`ventana ${j.dia}`} />
                <span className={`ventana ${j.noche || 'vacia'}`} />
              </div>
              <div className="jornada-fecha">{j.fecha}</div>
            </div>
          ))}
        </div>
      </div>

      {/* --- lo que sigue sin cerrar ------------------------------------ */}
      <div>
        <div className="eyebrow" style={{ marginBottom: '0.35rem' }}>
          Sin cerrar
          <Ayuda etiqueta="Qué cuentan estos números">{D.sin_cerrar}</Ayuda>
        </div>
        <div className="pendientes">
          {/* Fracción y no número suelto. `24` no dice si la sala avanza; `24/24`
              sí, y `9/24` tres turnos después se lee sin explicar nada. */}
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
