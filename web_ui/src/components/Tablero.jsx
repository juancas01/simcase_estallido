// ---------------------------------------------------------------------------
// SUPERFICIE 1 · EL TABLERO GENERAL — proyectado para toda la sala.
//
// Responde QUÉ ESTÁ PASANDO, en grano grueso. El cuánto, el dónde exactamente y
// el desde cuándo son las nueve vistas privadas.
//
//
// CÓMO SEÑALA UN PROBLEMA SIN DECIR QUÉ HACER
// ===========================================
// Es la tensión que gobierna todo este archivo. Si el tablero dice «abra el
// corredor hospitalario», el ejercicio se acabó: el tablero pensó por la sala.
// Si el tablero es un muro de números iguales, nadie se entera de nada en trece
// minutos de deliberación.
//
// La salida no es un término medio, es un cambio de mecanismo:
//
//     SALIENCIA, NO INSTRUCCIÓN.
//
// Cuatro palancas, y las cuatro enuncian hechos:
//
//   1 · EL CAMBIO, NO EL NIVEL.  Una métrica que no se movió no lleva marca;
//       una que se movió lleva su flecha. Es la señal más barata del tablero.
//
//   2 · EL PLAZO.  «Jornada 3 de 5, quedan dos» es una presión, y una
//       concertación que tarda dos jornadas en rendir no cabe en la quinta.
//       El reloj dice cuánto queda; qué hacer con eso es de la sala.
//
//   3 · EL ORDEN.  Corredores y regiones van PEOR PRIMERO. El ojo aterriza
//       arriba a la izquierda, y ahí está el problema sin que nadie lo señale.
//
//   4 · LO QUE FALTA, CONTADO.  Puntos que nadie ha mirado, denuncias abiertas,
//       decisiones sin responsable. **La distancia entre «3 puntos sin
//       verificar» y «verifique N003» es la distancia entre un ejercicio y un
//       tutorial.**
//
//
// LAS MÉTRICAS NO LLEVAN CIFRA
// ============================
// Aquí había cuatro barras con su número —«Legitimidad 52»— y esta sección se
// llamaba «Reservas». Ahora son escalas de cinco pasos: muy bajo, bajo, medio,
// alto, muy alto. Y no es una simplificación:
//
//     Un nivel se interpreta. Un número se optimiza.
//
// Con la cifra en la pared, la conversación de la sala se vuelve aritmética
// —«subimos tres, podemos gastar cuatro»— y el ejercicio deja de ser sobre
// conducción para ser sobre puntuación. Ninguna de estas magnitudes es medible
// en la realidad con dos cifras significativas, y fingir que lo es enseña algo
// falso sobre lo que un puesto de mando puede saber de sí mismo.
//
// Lo que SÍ conserva su cifra es lo que se cuenta de verdad: muertes evitables y
// escuadrones sin comprometer. Son personas y son unidades, no índices.
//
//
// LA JERARQUÍA DE LA PANTALLA
// ---------------------------
//   1 · el reloj y los cabos sueltos ....... el plazo y lo que sigue abierto
//   2 · la noche, cuando la hay ............ qué produjo lo que se ordenó
//   3 · lo irreversible y las métricas ..... el marcador, sin marcador
//   4 · el territorio ...................... mapa + corredores
//   5 · el abastecimiento y el pliego ...... la consecuencia y el registro
//
// LA BARRA LATERAL DE LA ESFERA PÚBLICA
// -------------------------------------
// **La esfera pública no tiene ruta propia: vive aquí y solo aquí.** La
// distancia entre lo que el Estado tiene por cierto y lo que se dice solo se
// percibe SIMULTÁNEA, y mientras la esfera tuvo pantalla aparte esa doctrina
// dependía de que quien monta la sala hiciera lo correcto. Una regla que el
// software garantiza vale más que una que el software recomienda.
//
// LO QUE NUNCA MUESTRA: la mezcla real de un punto, ni si una denuncia es
// cierta. Tampoco por la puerta de atrás de una tendencia.
// ---------------------------------------------------------------------------

import { useEffect, useRef, useState } from 'react'
import Mapa from './Mapa'
import EsferaContenido, { ENCUADRE, sinVerificar } from './EsferaContenido'
import Reloj from './Reloj'
import Cronometro from './Cronometro'
import Navegacion from './Navegacion'
import AccesoVistas from './AccesoVistas'
import Ayuda, { Titulo } from './Ayuda'
import { D } from '../definiciones.jsx'
import { COLOR_CORREDOR, EVENTO, SEMAFORO, rotulo } from '../etiquetas.jsx'
import { Cargando, Delta, Medidor, useDatos } from '../comun.jsx'

const CLAVE_BARRA = 'simcase:esfera_abierta'

/** Recuerda si la barra quedó abierta. Si el navegador no deja guardar, da igual. */
function usarPreferencia(clave, inicial) {
  const [valor, setValor] = useState(() => {
    try {
      const guardado = localStorage.getItem(clave)
      return guardado === null ? inicial : guardado === 'true'
    } catch {
      return inicial
    }
  })
  useEffect(() => {
    try { localStorage.setItem(clave, String(valor)) } catch { /* sin persistencia */ }
  }, [clave, valor])
  return [valor, setValor]
}

/** Peor primero. El ojo aterriza arriba y ahí está el problema. */
const ORDEN_SEMAFORO = { rojo: 0, ambar: 1, verde: 2 }

export default function Tablero() {
  const { datos, error } = useDatos('/tablero')
  const { datos: esfera } = useDatos('/esfera')
  const [sel, setSel] = useState(null)
  const [abierta, setAbierta] = usarPreferencia(CLAVE_BARRA, true)

  // Cuántas publicaciones había la última vez que la barra estuvo abierta, para
  // avisar de que entró algo nuevo mientras estaba plegada.
  const vistasHasta = useRef(0)
  const totalPubs = esfera?.publicaciones?.length ?? 0
  useEffect(() => {
    if (abierta) vistasHasta.current = totalPubs
  }, [abierta, totalPubs])

  if (!datos) return <Cargando error={error} ruta="/tablero" />

  const r = datos.reservas
  const d = datos.deltas || {}
  const abiertas = sinVerificar(esfera).length
  const nuevas = Math.max(0, totalPubs - vistasHasta.current)
  const enc = ENCUADRE[esfera?.encuadre_dominante] || null

  const sinVerificarPuntos = datos.puntos.filter(p => p.estado === 'sin_verificar').length
  const sinResponsable = (datos.registro || []).filter(x => !x.responsable_nominado).length

  const corredores = [...datos.corredores].sort((a, b) => a.caudal - b.caudal)
  const regiones = [...datos.regiones].sort((a, b) =>
    (ORDEN_SEMAFORO[a.semaforo] - ORDEN_SEMAFORO[b.semaforo])
    || (b.muertes_evitables - a.muertes_evitables))

  const muertes = datos.muertes_evitables
  const esNoche = datos.fase === 'noche'

  return (
    <div className="pantalla">
      <header className="cabecera">
        <div>
          {/* El acceso a las nueve vistas va en la línea de la versalita:
              una línea que ya existía, encima del título y no dentro de él.
              Una fila de pestañas sobre la pantalla proyectada ocuparía el
              sitio de los datos e invitaría a proyectar una vista privada,
              que es lo único que el ejercicio no puede permitirse. */}
          <div className="cabecera-rotulo">
            <span className="eyebrow">Tablero de situación · para proyectar</span>
            <AccesoVistas />
            <Navegacion destinos={['consola']} />
          </div>
          <h1>Puesto de Mando Unificado</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          {/* El reloj de sala. La misma pieza que ven la consola y las nueve
              vistas, contando sobre el mismo instante. */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <Cronometro cronometro={datos.cronometro} />
            <Ayuda etiqueta="Cómo corre el reloj de la jornada">{D.cronometro}</Ayuda>
          </div>
          <button
            onClick={() => setAbierta(a => !a)}
            aria-expanded={abierta}
            aria-controls="esfera-lateral"
            style={{ position: 'relative', whiteSpace: 'nowrap' }}
          >
            {abierta ? 'Ocultar' : 'Mostrar'} esfera pública
            {!abierta && (abiertas > 0 || nuevas > 0) && (
              <span className="aviso-barra">{abiertas > 0 ? abiertas : nuevas}</span>
            )}
          </button>
        </div>
      </header>

      <div className="con-lateral">
      <div className="cuerpo">

        {/* --- 1 · El plazo y los cabos sueltos --------------------------- */}
        <Reloj
          reloj={datos.reloj}
          pendientes={[
            { nombre: 'Puntos sin verificar',
              n: sinVerificarPuntos, de: datos.puntos.length },
            { nombre: 'Denuncias abiertas',
              n: abiertas, de: esfera?.denuncias?.length ?? 0 },
            { nombre: 'Decisiones sin responsable',
              n: sinResponsable, de: (datos.registro || []).length },
          ]}
        />

        {/* --- 2 · La noche: qué produjo lo que se ordenó ------------------
            Los dos minutos de noche existen para esto, y una sala no puede
            interpretar consecuencias que están repartidas por cinco tarjetas.
            Aquí van juntas, y desaparecen solas al abrir la jornada. */}
        {esNoche && datos.consecuencias && (
          <Consecuencias datos={datos.consecuencias} />
        )}

        {/* --- 3 · Lo irreversible y las métricas ------------------------- */}
        <div className="banda">
          <div className="tarjeta">
            <Titulo ayuda={D.coste_humano}>Coste irreversible</Titulo>
            <div className={`cifra-grave${muertes > 0 ? ' hay' : ''}`}>
              {muertes}
              <Delta valor={d.muertes_evitables} sentido="arriba_peor" />
            </div>
            <p className="pie-cifra">Muertes evitables acumuladas</p>
          </div>

          {/* UNA marca, un globo. Dos marcas pegadas obligan a elegir cuál
              abrir antes de saber qué hay en cada una. */}
          <div className="tarjeta tarjeta-metricas">
            <Titulo ayuda={D.metricas}>Métricas</Titulo>
            <div className="rejilla-metricas">
              <Medidor nombre="Presión en la calle" valor={datos.presion_calle}
                       sentido="arriba_peor" ayuda={D.presion_calle}
                       delta={d.presion_calle} />
              <Medidor nombre="Legitimidad" valor={r.legitimidad}
                       ayuda={D.legitimidad} delta={d.legitimidad} />
              <Medidor nombre="Credibilidad de la mesa" valor={r.credibilidad_mesa}
                       ayuda={D.credibilidad_mesa} delta={d.credibilidad_mesa} />
              <Medidor nombre="Respaldo internacional" valor={r.respaldo_internacional}
                       ayuda={D.respaldo_internacional} delta={d.respaldo_internacional} />
              <Medidor nombre="Cohesión del PMU" valor={r.cohesion_mesa}
                       ayuda={D.cohesion_mesa} delta={d.cohesion_mesa} />
            </div>
          </div>

          <div className="tarjeta">
            <Titulo ayuda={D.fuerza}>Fuerza</Titulo>
            <div className="cifra-recurso">
              {datos.fuerza.esmad_sin_comprometer}
              <span className="cifra-total">/ {datos.fuerza.esmad_total}</span>
              <Delta valor={d.esmad_sin_comprometer} />
            </div>
            <p className="pie-cifra">Escuadrones sin comprometer</p>
            {datos.fuerza.frentes_rurales_descubiertos > 0 && (
              <p className="pie-aviso">
                {datos.fuerza.frentes_rurales_descubiertos === 1
                  ? '1 frente rural descubierto'
                  : `${datos.fuerza.frentes_rurales_descubiertos} frentes `
                    + 'rurales descubiertos'}
              </p>
            )}
          </div>
        </div>

        {/* --- 4 · El territorio: mapa + corredores ----------------------- */}
        <div className="tarjeta" style={{ marginTop: '1rem' }}>
          <Titulo ayuda={D.corredores}>Territorio</Titulo>
          <div className="territorio">
            <div>
              <Mapa tablero={datos} seleccionado={sel} onSeleccionar={setSel} />
            </div>

            <table>
              <thead>
                <tr>
                  <th>Corredor</th>
                  <th>Flujo</th>
                  <th>
                    Población
                    <Ayuda etiqueta="Definición de población aguas abajo">
                      {D.poblacion_corredor}
                    </Ayuda>
                  </th>
                  <th>
                    Prioridad
                    <Ayuda etiqueta="Definición de clases de prioridad">
                      {D.clases_corredor}
                    </Ayuda>
                  </th>
                </tr>
              </thead>
              <tbody>
                {corredores.map(c => (
                  <tr key={c.corredor_id}
                      className={c.caudal <= 0.05 ? 'grave'
                        : c.caudal < 0.6 ? 'aviso' : ''}>
                    {/* La tinta del corredor es la del mapa: la tabla ES la
                        leyenda, y no hay dos listas que desincronizar. */}
                    <td style={{ color: 'var(--texto)' }}>
                      <span className="tinta" style={{
                        background: COLOR_CORREDOR[c.corredor_id] || 'var(--texto-3)',
                      }} />
                      {c.nombre}
                    </td>
                    <td className="num" style={{
                      color: c.caudal > 0.6 ? 'var(--bien)'
                        : c.caudal > 0.05 ? 'var(--medio)' : 'var(--mal)',
                    }}>
                      {Math.round(c.caudal * 100)} %
                      <Delta valor={(d[`caudal:${c.corredor_id}`] ?? 0) * 100} />
                    </td>
                    <td className="num">{(c.poblacion / 1e6).toFixed(2)} M</td>
                    <td style={{ fontSize: '0.78rem' }}>{c.clases.join(', ')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* --- 5 · La consecuencia y el registro -------------------------- */}
        <div className="rejilla" style={{ marginTop: '1rem' }}>
          <div className="tarjeta">
            <Titulo ayuda={D.semaforo}>Abastecimiento · peor primero</Titulo>
            <table>
              <thead>
                <tr>
                  <th>Región</th>
                  <th>Estado</th>
                  <th style={{ textAlign: 'right' }}>
                    Muertes evitables
                    <Ayuda etiqueta="Definición de muertes evitables">
                      {D.muertes_evitables}
                    </Ayuda>
                  </th>
                </tr>
              </thead>
              <tbody>
                {regiones.map(g => (
                  <tr key={g.region_id}
                      className={g.semaforo === 'rojo' ? 'grave'
                        : g.semaforo === 'ambar' ? 'aviso' : ''}>
                    <td style={{ color: 'var(--texto)' }}>
                      {g.nombre}
                      {g.epicentro && <span className="eyebrow"> · epicentro</span>}
                    </td>
                    <td>
                      <span className={`chip chip-${g.semaforo === 'verde' ? 'bien'
                        : g.semaforo === 'ambar' ? 'medio' : 'mal'}`}>
                        {rotulo(SEMAFORO, g.semaforo)}
                      </span>
                    </td>
                    <td className="num" style={{
                      textAlign: 'right',
                      color: g.muertes_evitables ? 'var(--mal)' : 'var(--texto-3)',
                    }}>
                      {g.muertes_evitables}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="tarjeta">
            <Titulo ayuda={D.pliego}>Pliego de decisiones</Titulo>
            {datos.registro?.length ? (
              <table>
                <thead>
                  <tr><th>J</th><th>Rol</th><th>Decisión</th><th>Responsable</th></tr>
                </thead>
                <tbody>
                  {datos.registro.slice().reverse().map((x, i) => (
                    <tr key={i} className={x.responsable_nominado ? '' : 'aviso'}>
                      <td className="num">{x.turno}</td>
                      <td>{x.rol}</td>
                      <td style={{ color: 'var(--texto)' }}>{x.descripcion}</td>
                      <td style={{
                        color: x.responsable_nominado ? 'var(--texto-2)' : 'var(--mal)',
                      }}>
                        {x.responsable_nominado || '— SIN NOMBRE —'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p style={{ margin: 0, color: 'var(--texto-3)' }}>
                Sin decisiones registradas.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* --- La esfera pública, plegable ------------------------------- */}
      {abierta && (
        <aside className="lateral" id="esfera-lateral">
          <div className="lateral-cabecera">
            <div>
              <span className="eyebrow">Esfera pública</span>
              <div style={{ fontWeight: 650, fontSize: '0.95rem' }}>
                Lo que se dice
                <Ayuda etiqueta="Qué es la esfera pública">{D.esfera}</Ayuda>
              </div>
            </div>
            {enc && <span className={`chip chip-${enc.chip}`}>{enc.texto}</span>}
          </div>
          <div className="lateral-cuerpo">
            <EsferaContenido datos={esfera} />
          </div>
        </aside>
      )}
      </div>
    </div>
  )
}

/**
 * QUÉ PRODUJO LO QUE SE ORDENÓ — solo durante los dos minutos de noche.
 *
 * Es el bloque que da contenido a esa mitad de la jornada. Sin él, «mirar las
 * consecuencias» significa recorrer cinco tarjetas buscando cuál se movió, y en
 * dos minutos no da tiempo. Aquí van juntas y en el orden en que ocurrieron.
 *
 * NO INTERPRETA. Enumera lo que el motor devolvió, con sus propias frases: la
 * lectura de qué significa es de la sala, que es justamente lo que esos dos
 * minutos existen para que ocurra.
 */
function Consecuencias({ datos }) {
  const eventos = (datos.eventos || []).filter(e => e.tipo || e.evento)
  return (
    <div className="tarjeta consecuencias">
      <Titulo ayuda={D.consecuencias}>
        Consecuencias de la jornada {datos.jornada}
      </Titulo>

      {datos.resultados?.length ? (
        <div className="consecuencias-lista">
          {datos.resultados.map((x, i) => (
            <p key={i}>
              <span className={`chip chip-${x.ok ? 'bien' : 'mal'}`}>
                {x.ok ? 'Ejecutada' : 'No viable'}
              </span>{' '}
              {x.mensaje}
            </p>
          ))}
        </div>
      ) : (
        <p className="consecuencias-vacio">
          No se ordenó nada en esta jornada. El reloj corrió igual.
        </p>
      )}

      {eventos.length > 0 && (
        <p className="consecuencias-eventos">
          {eventos.slice(0, 12).map((e, i) => (
            <span key={i} className="chip chip-neutro">
              {rotulo(EVENTO, e.tipo || e.evento)}
              {e.nodo ? ` · ${e.nodo}` : ''}
            </span>
          ))}
        </p>
      )}
    </div>
  )
}
