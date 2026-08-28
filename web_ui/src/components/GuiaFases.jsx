// ---------------------------------------------------------------------------
// LA GUÍA DE LA JORNADA — en qué mitad va la sala y qué debería estar pasando.
//
// Va SOLO en la consola. El tablero enuncia hechos y no da instrucciones —esa es
// la regla de la que cuelga todo el diseño de esa pantalla—, pero la consola es
// otra cosa: la opera una persona que no montó el sistema, y que necesita saber
// si el minuto que corre es para transcribir o para callarse.
//
// Dos tramos, no siete. El texto de cada uno llega del motor dentro de la tabla
// de fases: si mañana el día pasa de trece a diez minutos, hay un solo sitio que
// corregir.
//
// SOLO SE DESPLIEGA LA GUÍA DEL TRAMO EN CURSO. El otro queda como recorrido: de
// dónde viene la sala y cuánto le falta.
// ---------------------------------------------------------------------------

/** Coma decimal, como en el resto de la aplicación: «2,5 min» y no «2.5 min». */
const minutos = (m) => String(m).replace('.', ',')

export default function GuiaFases({ cronometro }) {
  const fases = cronometro?.fases || []
  if (!fases.length) return null

  // Sin reloj no hay tramo en curso: la jornada entera queda por delante.
  const actual = cronometro?.corriendo
    ? fases.findIndex(f => f.id === cronometro.fase)
    : -1

  return (
    <ol className="guia-fases">
      {fases.map((f, i) => (
        <li key={f.id}
            className={i === actual ? 'es-actual' : i < actual ? 'cumplida' : ''}
            aria-current={i === actual ? 'step' : undefined}>
          <span className="guia-marca" aria-hidden="true">
            {i < actual ? '·' : i + 1}
          </span>
          <div className="guia-cuerpo">
            <div className="guia-titulo">
              <span>{f.nombre}</span>
              <span className="guia-min num">{minutos(f.minutos)} min</span>
            </div>
            {i === actual && <p className="guia-texto">{f.guia}</p>}
          </div>
        </li>
      ))}
    </ol>
  )
}
