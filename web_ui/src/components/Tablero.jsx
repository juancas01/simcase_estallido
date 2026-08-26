// ---------------------------------------------------------------------------
// SUPERFICIE 1 · EL TABLERO GENERAL — proyectado para toda la sala.
//
// Responde QUÉ ESTÁ PASANDO, en grano grueso. El cuánto, el dónde exactamente y
// el desde cuándo son las ocho vistas privadas.
//
//   · las cuatro reservas, y las cuatro se leen igual: arriba es mejor
//   · el mapa esquemático de los cinco corredores
//   · las cuatro regiones con SEMÁFORO, sin números — los días son de Minas
//   · la fuerza sin comprometer, sin decir dónde está — eso es de la Policía
//
// LA BARRA LATERAL DE LA ESFERA PÚBLICA
// -------------------------------------
// Con dos proyectores, la esfera va en `/esfera` y las dos pantallas se ven a la
// vez. Con uno solo —o con un portátil—, vive aquí como barra que se pliega.
//
// **Barra y no pestaña, y la diferencia importa.** La distancia entre lo que el
// Estado tiene por cierto y lo que se dice es el caso, y solo se percibe
// SIMULTÁNEA. Una barra abierta se ve junto al tablero; una pestaña sustituye
// una cosa por la otra y elimina justamente lo que hay que enseñar.
//
// Cuando está plegada, el contador de denuncias sin verificar sigue visible en
// el botón: es lo que hace que alguien la abra.
//
// LO QUE NUNCA MUESTRA: la mezcla real de un punto, ni si una denuncia es
// cierta. Si eso se filtrara, el dilema central del caso desaparecería.
// ---------------------------------------------------------------------------

import { useEffect, useRef, useState } from 'react'
import MapaEsquematico from './MapaEsquematico'
import EsferaContenido, { ENCUADRE, sinVerificar } from './EsferaContenido'
import {
  Barra, Cargando, nivelPresion, nivelReserva, useDatos,
} from '../comun.jsx'

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

export default function Tablero() {
  const { datos, error } = useDatos('/tablero', 4000)
  const { datos: esfera } = useDatos('/esfera', 4000)
  const [sel, setSel] = useState(null)
  const [abierta, setAbierta] = usarPreferencia(CLAVE_BARRA, true)

  // Cuántas publicaciones había la última vez que la barra estuvo abierta, para
  // avisar de que entró algo nuevo mientras estaba plegada.
  const vistasHasta = useRef(0)
  const totalPubs = esfera?.publicaciones?.length ?? 0
  useEffect(() => {
    if (abierta) vistasHasta.current = totalPubs
  }, [abierta, totalPubs])

  if (!datos) return <Cargando error={error} />

  const r = datos.reservas
  const punto = datos.puntos.find(p => p.nodo_id === sel)
  const abiertas = sinVerificar(esfera).length
  const nuevas = Math.max(0, totalPubs - vistasHasta.current)
  const enc = ENCUADRE[esfera?.encuadre_dominante] || null

  return (
    <div className="pantalla">
      <header className="cabecera">
        <div>
          <span className="eyebrow">Tablero de situación · proyectar</span>
          <h1>Puesto de Mando Unificado</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          <div style={{ textAlign: 'right' }}>
            <div className="num" style={{ fontSize: '1.1rem', fontWeight: 600 }}>
              Turno {datos.turno_decision || 0} · {datos.franja}
            </div>
            {datos.congelado && (
              <div className="congelado">congelado · {datos.fase}</div>
            )}
          </div>
          <button
            onClick={() => setAbierta(a => !a)}
            aria-expanded={abierta}
            aria-controls="esfera-lateral"
            title="La distancia entre el tablero y la esfera pública es el caso"
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
        <div className="rejilla" style={{ gridTemplateColumns: '1fr' }}>
          {/* --- La fila de indicadores ------------------------------------- */}
          <div className="rejilla" style={{
            gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))',
          }}>
            <div className="tarjeta">
              <h2>Presión en la calle</h2>
              <Barra nombre="Movilización" valor={datos.presion_calle}
                     nivel={nivelPresion(datos.presion_calle)} />
              <p style={{ margin: '0.5rem 0 0', fontSize: '0.78rem',
                          color: 'var(--texto-3)' }}>
                La única que va al revés: arriba es peor. Es el adversario.
              </p>
            </div>

            <div className="tarjeta" style={{ gridColumn: 'span 2' }}>
              <h2>Las cuatro reservas · arriba es mejor</h2>
              <div className="rejilla" style={{
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '0.75rem',
              }}>
                <Barra nombre="Legitimidad" valor={r.legitimidad}
                       nivel={nivelReserva(r.legitimidad)} />
                <Barra nombre="Credibilidad de la mesa" valor={r.credibilidad_mesa}
                       nivel={nivelReserva(r.credibilidad_mesa)} />
                <Barra nombre="Respaldo internacional" valor={r.respaldo_internacional}
                       nivel={nivelReserva(r.respaldo_internacional)} />
                <Barra nombre="Cohesión del PMU" valor={r.cohesion_mesa}
                       nivel={nivelReserva(r.cohesion_mesa)} />
              </div>
            </div>

            <div className="tarjeta">
              <h2>Fuerza</h2>
              <div className="num" style={{ fontSize: '2rem', fontWeight: 650, lineHeight: 1 }}>
                {datos.fuerza.esmad_sin_comprometer}
                <span style={{ fontSize: '1rem', color: 'var(--texto-3)' }}>
                  {' '}/ {datos.fuerza.esmad_total}
                </span>
              </div>
              <p style={{ margin: '0.35rem 0 0', fontSize: '0.8rem', color: 'var(--texto-2)' }}>
                escuadrones sin comprometer
              </p>
              {datos.fuerza.frentes_rurales_descubiertos > 0 && (
                <p style={{ margin: '0.4rem 0 0', fontSize: '0.78rem', color: 'var(--medio)' }}>
                  {datos.fuerza.frentes_rurales_descubiertos} frente(s) rural(es) descubierto(s)
                </p>
              )}
            </div>
          </div>

          {/* --- El mapa ---------------------------------------------------- */}
          <MapaEsquematico tablero={datos} seleccionado={sel} onSeleccionar={setSel} />

          {punto && (
            <div className="tarjeta" style={{ borderColor: 'var(--acento)' }}>
              <h2>{punto.nombre} · {punto.nodo_id}</h2>
              <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--texto-2)' }}>
                {datos.regiones.find(x => x.region_id === punto.region_id)?.nombre}
                {punto.corredor_id && ` · ${datos.corredores.find(c => c.corredor_id === punto.corredor_id)?.nombre}`}
                {' · '}
                <span className={`chip chip-${punto.estado === 'abierto' ? 'bien'
                  : punto.estado === 'parcial' ? 'medio'
                  : punto.estado === 'sin_verificar' ? 'neutro' : 'mal'}`}>
                  {punto.estado.replace('_', ' ')}
                </span>
                {punto.modo_apertura !== 'cerrado' && ` · abierto por ${punto.modo_apertura}`}
              </p>
              {punto.estado === 'sin_verificar' && (
                <p style={{ margin: '0.5rem 0 0', fontSize: '0.85rem', color: 'var(--medio)' }}>
                  Nadie ha mirado este punto. La Defensoría puede gastar una dupla aquí
                  — y entonces no la gasta en otro sitio.
                </p>
              )}
            </div>
          )}

          {/* --- Corredores y regiones -------------------------------------- */}
          <div className="rejilla">
            <div className="tarjeta">
              <h2>Corredores · un corredor vale lo que su peor punto</h2>
              <table>
                <thead>
                  <tr><th>Corredor</th><th>Flujo</th><th>Población</th><th>Sirve para</th></tr>
                </thead>
                <tbody>
                  {datos.corredores.map(c => (
                    <tr key={c.corredor_id}>
                      <td style={{ color: 'var(--texto)' }}>{c.nombre}</td>
                      <td className="num" style={{
                        color: c.caudal > 0.6 ? 'var(--bien)'
                          : c.caudal > 0.05 ? 'var(--medio)' : 'var(--mal)',
                      }}>
                        {Math.round(c.caudal * 100)} %
                      </td>
                      <td className="num">{(c.poblacion / 1e6).toFixed(2)} M</td>
                      <td style={{ fontSize: '0.78rem' }}>{c.clases.join(', ')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="tarjeta">
              <h2>Regiones · abastecimiento</h2>
              <table>
                <thead>
                  <tr><th>Región</th><th>Estado</th><th style={{ textAlign: 'right' }}>Muertes evitables</th></tr>
                </thead>
                <tbody>
                  {datos.regiones.map(g => (
                    <tr key={g.region_id}>
                      <td style={{ color: 'var(--texto)' }}>
                        {g.nombre}
                        {g.epicentro && <span className="eyebrow"> · epicentro</span>}
                      </td>
                      <td>
                        <span className={`chip chip-${g.semaforo === 'verde' ? 'bien'
                          : g.semaforo === 'ambar' ? 'medio' : 'mal'}`}>
                          {g.semaforo}
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
              <p style={{ margin: '0.6rem 0 0', fontSize: '0.78rem', color: 'var(--texto-3)' }}>
                Los días exactos los tiene el Ministro de Minas. Hasta que los diga, la
                mesa sabe que hay un problema y no sabe cuánto tiempo tiene.
              </p>
            </div>
          </div>

          {/* --- El pliego -------------------------------------------------- */}
          <div className="tarjeta">
            <h2>Pliego de decisiones · el renglón vacío es más elocuente que una advertencia</h2>
            {datos.registro?.length ? (
              <table>
                <thead>
                  <tr><th>T</th><th>Rol</th><th>Decisión</th><th>Responsable</th></tr>
                </thead>
                <tbody>
                  {datos.registro.slice().reverse().map((d, i) => (
                    <tr key={i}>
                      <td className="num">{d.turno}</td>
                      <td>{d.rol}</td>
                      <td style={{ color: 'var(--texto)' }}>{d.descripcion}</td>
                      <td style={{ color: d.responsable_nominado ? 'var(--texto-2)' : 'var(--mal)' }}>
                        {d.responsable_nominado || '— SIN NOMBRE —'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p style={{ margin: 0, color: 'var(--texto-3)' }}>
                Todavía no se ha registrado ninguna decisión.
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
              <div style={{ fontWeight: 650, fontSize: '0.95rem' }}>Lo que se dice</div>
            </div>
            {enc && <span className={`chip chip-${enc.chip}`}>{enc.texto}</span>}
          </div>
          <div className="lateral-cuerpo">
            <EsferaContenido datos={esfera} compacto />
            <p style={{ fontSize: '0.72rem', color: 'var(--texto-3)',
                        marginTop: '0.75rem' }}>
              La distancia entre esta columna y el tablero es el caso. Con dos
              proyectores, esto va aparte en <code>/esfera</code>.
            </p>
          </div>
        </aside>
      )}
      </div>
    </div>
  )
}
