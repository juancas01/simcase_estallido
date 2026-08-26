// ---------------------------------------------------------------------------
// SUPERFICIE 1 · EL TABLERO GENERAL — proyectado para toda la sala.
//
// Responde QUÉ ESTÁ PASANDO, en grano grueso. El cuánto, el dónde exactamente y
// el desde cuándo son las ocho vistas privadas.
//
//
// CÓMO SEÑALA UN PROBLEMA SIN DECIR QUÉ HACER
// ===========================================
// Es la tensión que gobierna todo este archivo. Si el tablero dice «abra el
// corredor hospitalario», el ejercicio se acabó: el tablero pensó por la sala.
// Si el tablero es un muro de números iguales, nadie se entera de nada en seis
// minutos de deliberación.
//
// La salida no es un término medio, es un cambio de mecanismo:
//
//     SALIENCIA, NO INSTRUCCIÓN.
//
// Cuatro palancas, y las cuatro enuncian hechos:
//
//   1 · EL CAMBIO, NO EL NIVEL.  `Legitimidad 41` no le dice nada a quien no
//       memorizó el punto de partida. `41 ▼9` le dice que algo de anoche costó
//       nueve puntos. Es la señal más barata del tablero y la que más apunta.
//
//   2 · EL PLAZO.  «Turno 3» es neutro. «Jornada 3 de 5» es una presión, y una
//       concertación que tarda dos turnos en rendir no cabe en la jornada 5.
//       El reloj dice cuánto queda; qué hacer con eso es de la sala.
//
//   3 · EL ORDEN.  Corredores y regiones van PEOR PRIMERO. El ojo aterriza
//       arriba a la izquierda, y ahí está el problema sin que nadie lo señale.
//       Con cuatro regiones y cinco corredores, la memoria espacial que se
//       pierde la devuelve el mapa.
//
//   4 · LO QUE FALTA, CONTADO.  Tres puntos que nadie ha mirado, dos denuncias
//       abiertas, una decisión sin responsable. **La distancia entre «3 puntos
//       sin verificar» y «verifique P7» es la distancia entre un ejercicio y un
//       tutorial.**
//
// Ninguna de las cuatro nombra un remedio. Todas hacen que el problema sea lo
// primero que se ve.
//
//
// LA JERARQUÍA DE LA PANTALLA
// ---------------------------
//   1 · el reloj y los cabos sueltos ....... el plazo y lo que sigue abierto
//   2 · lo irreversible y las reservas ..... el marcador, con sus deltas
//   3 · el territorio ...................... mapa PEQUEÑO + corredores
//   4 · el abastecimiento y el pliego ...... la consecuencia y el registro
//
// El mapa dejó de ocupar el ancho entero. Era la pieza más grande de la pantalla
// y no es la más importante: ahora vive junto a la tabla de corredores, que con
// su tinta hace además de leyenda. Dos leyendas de lo mismo eran una de más.
//
// LA BARRA LATERAL DE LA ESFERA PÚBLICA
// -------------------------------------
// **La esfera pública ya no tiene ruta propia: vive aquí y solo aquí.**
//
// La tenía, para montajes de dos proyectores. Pero la doctrina siempre fue que
// la distancia entre lo que el Estado tiene por cierto y lo que se dice solo se
// percibe SIMULTÁNEA — y mientras la esfera tuvo pantalla aparte, esa doctrina
// dependía de que quien monta la sala hiciera lo correcto. Bastaba proyectar una
// de las dos sola para perder justamente lo que hay que enseñar.
//
// Al vivir dentro del tablero, el montaje incorrecto deja de ser posible. **Una
// regla que el software garantiza vale más que una que el software recomienda.**
//
// Sigue siendo barra y no pestaña: una pestaña sustituye una cosa por la otra y
// vuelve a eliminar lo que hay que enseñar.
//
// LO QUE NUNCA MUESTRA: la mezcla real de un punto, ni si una denuncia es
// cierta. Tampoco por la puerta de atrás de un delta. Si eso se filtrara, el
// dilema central del caso desaparecería.
// ---------------------------------------------------------------------------

import { useEffect, useRef, useState } from 'react'
import MapaEsquematico, { COLOR_CORREDOR } from './MapaEsquematico'
import EsferaContenido, { ENCUADRE, sinVerificar } from './EsferaContenido'
import Reloj from './Reloj'
import Ayuda, { Titulo } from './Ayuda'
import { D } from '../definiciones.jsx'
import { ESTADO_PUNTO, FASE, MODO_APERTURA, SEMAFORO, rotulo } from '../etiquetas.jsx'
import {
  Barra, Cargando, Delta, nivelPresion, nivelReserva, useDatos,
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

/** Peor primero. El ojo aterriza arriba y ahí está el problema. */
const ORDEN_SEMAFORO = { rojo: 0, ambar: 1, verde: 2 }

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
  const d = datos.deltas || {}
  const punto = datos.puntos.find(p => p.nodo_id === sel)
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

  return (
    <div className="pantalla">
      <header className="cabecera">
        <div>
          <span className="eyebrow">Tablero de situación · proyectar</span>
          <h1>Puesto de Mando Unificado</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
          {datos.congelado && (
            <div className="congelado">
              Congelado · {rotulo(FASE, datos.fase)}
              <Ayuda etiqueta="Qué significa congelado">{D.congelado}</Ayuda>
            </div>
          )}
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

        {/* --- 2 · Lo irreversible, la presión y las reservas ------------- */}
        <div className="banda">
          <div className="tarjeta">
            <Titulo ayuda={D.coste_humano}>Coste irreversible</Titulo>
            <div className={`cifra-grave${muertes > 0 ? ' hay' : ''}`}>
              {muertes}
              <Delta valor={d.muertes_evitables} sentido="arriba_peor" />
            </div>
            <p className="pie-cifra">Muertes evitables acumuladas</p>
            <div style={{ marginTop: '0.9rem' }}>
              <Barra nombre="Presión en la calle" valor={datos.presion_calle}
                     nivel={nivelPresion(datos.presion_calle)}
                     ayuda={D.presion_calle}
                     delta={d.presion_calle} sentido="arriba_peor" />
            </div>
          </div>

          <div className="tarjeta">
            {/* UNA marca, un globo. Dos marcas pegadas obligan a elegir cuál
                abrir antes de saber qué hay en cada una: la notación ▲▼ va
                dentro de este mismo globo. */}
            <Titulo ayuda={D.reservas}>Reservas</Titulo>
            <div className="rejilla" style={{
              gridTemplateColumns: 'repeat(auto-fit, minmax(148px, 1fr))', gap: '0.75rem',
            }}>
              <Barra nombre="Legitimidad" valor={r.legitimidad}
                     nivel={nivelReserva(r.legitimidad)} ayuda={D.legitimidad}
                     delta={d.legitimidad} />
              <Barra nombre="Credibilidad de la mesa" valor={r.credibilidad_mesa}
                     nivel={nivelReserva(r.credibilidad_mesa)} ayuda={D.credibilidad_mesa}
                     delta={d.credibilidad_mesa} />
              <Barra nombre="Respaldo internacional" valor={r.respaldo_internacional}
                     nivel={nivelReserva(r.respaldo_internacional)}
                     ayuda={D.respaldo_internacional} delta={d.respaldo_internacional} />
              <Barra nombre="Cohesión del PMU" valor={r.cohesion_mesa}
                     nivel={nivelReserva(r.cohesion_mesa)} ayuda={D.cohesion_mesa}
                     delta={d.cohesion_mesa} />
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
                {datos.fuerza.frentes_rurales_descubiertos} frente(s) rural(es)
                descubierto(s)
              </p>
            )}
          </div>
        </div>

        {/* --- 3 · El territorio: mapa pequeño + corredores --------------- */}
        <div className="tarjeta" style={{ marginTop: '1rem' }}>
          <Titulo ayuda={D.corredores}>Corredores · peor primero</Titulo>
          <div className="territorio">
            <div>
              <MapaEsquematico tablero={datos} seleccionado={sel} onSeleccionar={setSel} />
              {punto && (
                <div className="punto-detalle">
                  <div className="punto-nombre">{punto.nombre} · {punto.nodo_id}</div>
                  <div className="punto-sub">
                    {datos.regiones.find(x => x.region_id === punto.region_id)?.nombre}
                    {' · '}
                    <span className={`chip chip-${punto.estado === 'abierto' ? 'bien'
                      : punto.estado === 'parcial' ? 'medio'
                      : punto.estado === 'sin_verificar' ? 'neutro' : 'mal'}`}>
                      {rotulo(ESTADO_PUNTO, punto.estado)}
                    </span>
                    {punto.estado === 'sin_verificar' && (
                      <Ayuda etiqueta="Qué significa sin verificar">
                        {D.punto_sin_verificar}
                      </Ayuda>
                    )}
                    {punto.modo_apertura !== 'cerrado'
                      && ` · por ${rotulo(MODO_APERTURA, punto.modo_apertura).toLowerCase()}`}
                  </div>
                </div>
              )}
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

        {/* --- 4 · La consecuencia y el registro -------------------------- */}
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
                  <tr><th>T</th><th>Rol</th><th>Decisión</th><th>Responsable</th></tr>
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
