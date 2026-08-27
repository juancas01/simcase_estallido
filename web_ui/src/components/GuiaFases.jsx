// ---------------------------------------------------------------------------
// LA GUÍA DEL TURNO — en qué paso va la sala y qué debería estar pasando ahí.
//
// Va SOLO en la consola. El tablero enuncia hechos y no da instrucciones —esa es
// la regla de la que cuelga todo el diseño de esa pantalla—, pero la consola es
// otra cosa: la opera una persona que no montó el sistema, y que necesita saber
// si el minuto que corre es para leer en silencio o para transcribir.
//
// El texto de cada paso es la coreografía de §6.2 de `docs/propuesta.md`, y
// llega del motor dentro de la tabla de fases. No está escrito aquí: si mañana
// una fase cambia de duración o de sentido, hay un solo sitio que corregir.
//
// SOLO SE DESPLIEGA LA GUÍA DE LA FASE EN CURSO. Los siete textos a la vez son
// un documento, y un documento en pantalla durante un ejercicio de dos horas no
// lo lee nadie. Los demás pasos quedan como recorrido: de dónde viene la sala y
// cuánto le falta.
// ---------------------------------------------------------------------------

/** Coma decimal, como en el resto de la aplicación: «2,5 min» y no «2.5 min». */
const minutos = (m) => String(m).replace('.', ',')

export default function GuiaFases({ cronometro }) {
  const fases = cronometro?.fases || []
  if (!fases.length) return null

  // Sin reloj no hay fase en curso: la lista entera queda por delante.
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
