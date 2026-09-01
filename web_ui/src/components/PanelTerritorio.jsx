// ---------------------------------------------------------------------------
// EL PANEL DEL TERRITORIO — a la derecha del mapa, en pestañas.
//
// Las métricas que la mesa necesita para decidir sobre el territorio son de
// tres clases distintas — puntos, corredores y regiones — y hasta ahora vivían
// repartidas: los corredores junto al mapa, las regiones en una tarjeta de
// abajo, y los puntos solo en el mapa, que es donde peor se comparan.
//
// TRES PESTAÑAS Y NO TRES TABLAS APILADAS. La mesa no llega a este panel a
// «ver el territorio»: llega con una pregunta —¿qué está cerrado?, ¿por dónde
// pasa la carga?, ¿dónde se está quedando sin comida?— y cada pestaña es una
// de esas preguntas. Tres tablas apiladas obligarían a recorrerlas todas para
// contestar cualquiera.
//
// LA TABLA ES LA LEYENDA DEL MAPA, y la fila está conectada con él en los DOS
// sentidos: pasar el ratón por una fila enciende su punto en el mapa, pasarlo
// por el punto enciende la fila, y el clic fija lo que la mesa discute. Dos
// representaciones del mismo hecho que no se hablan serían dos tableros.
//
// Y CADA FILA LLEVA DIBUJADO SU PUNTO. Al nivel de país el mapa no rotula: doce
// nombres largos sobre un racimo de seis puntos en la misma ciudad no se leen.
// Sin la marca, la fila decía «Portería de la refinería» y el mapa devolvía una
// constelación de formas sin una palabra que las casara. La dibuja `Mapa.jsx`
// —no este archivo— para que forma y color no puedan desincronizarse.
//
// AQUÍ ABAJO ESTÁ LA FICHA. Colgaba del mapa, en la otra columna, y eso partía
// la lectura de un punto en dos mitades separadas por media pantalla: la fila
// aquí, las seis lecturas allá. Ahora se recorre la lista arriba y se lee el
// detalle abajo, en la misma columna y sin cruzar la vista. Va FUERA de las
// pestañas porque no es de ninguna.
//
// PEOR PRIMERO, en las tres pestañas: el ojo aterriza arriba y ahí está el
// problema, sin que el tablero diga qué hacer con él — eso sigue siendo de la
// sala.
// ---------------------------------------------------------------------------

import { Fragment, useState } from 'react'

import Ayuda from './Ayuda'
import { ClaveDelMapa, DetallePunto, DetalleRegion, MarcaPunto } from './Mapa'
import { D } from '../definiciones.jsx'
import {
  COLOR_CORREDOR, ESTADO_PUNTO, INTERVENCION_CORTA, SEMAFORO, banda, rotulo,
} from '../etiquetas.jsx'
import { Delta, Dinero, millones } from '../comun.jsx'

/** Peor primero. Sin verificar va detrás de cerrado: es una duda, no un hecho. */
const RANGO_ESTADO = { cerrado: 0, sin_verificar: 1, parcial: 2, abierto: 3 }

const CHIP_ESTADO = {
  abierto: 'bien', parcial: 'medio', cerrado: 'mal', sin_verificar: 'neutro',
}

const PESTANAS = [
  { id: 'nodos', texto: 'Nodos' },
  { id: 'corredores', texto: 'Corredores' },
  { id: 'regiones', texto: 'Regiones' },
  { id: 'pliego', texto: 'Pliego' },
]

export default function PanelTerritorio({
  datos, deltas, registro, seleccionado, onSeleccionar, sobre, onSobre,
  zoom, onZoom,
}) {
  const [pestana, setPestana] = useState('nodos')

  return (
    <div className="panel-territorio">
      <div className="pestanas" role="tablist" aria-label="Métricas del territorio">
        {PESTANAS.map(p => (
          <button
            key={p.id}
            role="tab"
            aria-selected={pestana === p.id}
            className={`pestana${pestana === p.id ? ' activa' : ''}`}
            onClick={() => setPestana(p.id)}
          >
            {p.texto}
          </button>
        ))}
      </div>

      <div className="panel-pestana">
        {pestana === 'nodos' && (
          <TablaNodos datos={datos} seleccionado={seleccionado}
                      onSeleccionar={onSeleccionar}
                      sobre={sobre} onSobre={onSobre} />
        )}
        {pestana === 'corredores' && <TablaCorredores datos={datos} deltas={deltas} />}
        {pestana === 'regiones' && (
          <TablaRegiones datos={datos} zoom={zoom} onZoom={onZoom}
                         sobre={sobre} onSobre={onSobre} />
        )}
        {pestana === 'pliego' && <TablaPliego registro={registro} />}
      </div>
    </div>
  )
}

/**
 * EL DESPLIEGUE DE UNA FILA — el detalle, DENTRO de la tabla.
 *
 * Las seis lecturas fueron una tarjeta aparte: debajo del mapa primero, al pie
 * del panel después. En los dos sitios cometía el mismo error —sacar la lectura
 * de un punto fuera de la lista donde está el punto—, y el coste lo pagaba
 * quien comparaba dos filas: ir al bloque, cargar seis palabras en la cabeza,
 * volver, repetir.
 *
 * Aquí el detalle ocupa el ancho entero JUSTO DEBAJO de su fila. No está cerca
 * de ella: es ella. Y por eso lo abre un CLIC y no el ratón — con el ratón, la
 * tabla se abriría y cerraría sola mientras alguien busca, y en una pantalla
 * proyectada quien mueve el ratón no es quien habla.
 */
function FilaDetalle({ columnas, children }) {
  return (
    <tr className="fila-detalle">
      <td colSpan={columnas}>{children}</td>
    </tr>
  )
}

/** Una banda de la lectura de un punto, en palabra: el color lo dice todo. */
function Banda({ lectura }) {
  if (!lectura) return <span className="num">—</span>
  const color = peldanoColor(lectura)
  return (
    <span className="num" style={{ color }}>
      {banda(lectura.banda)}
    </span>
  )
}

/** El peldaño traducido a tinta. 0 es el extremo bueno o el malo según el
    sentido que el motor declaró para esa lectura. */
function peldanoColor(lectura) {
  const i = lectura.peldano ?? 0
  const arribaMejor = lectura.sentido !== 'arriba_peor'
  const orden = arribaMejor
    ? ['var(--mal)', 'var(--mal)', 'var(--medio)', 'var(--bien)', 'var(--bien)']
    : ['var(--bien)', 'var(--bien)', 'var(--medio)', 'var(--mal)', 'var(--mal)']
  return orden[Math.min(i, orden.length - 1)]
}

function TablaNodos({ datos, seleccionado, onSeleccionar, sobre, onSobre }) {
  const puntos = [...datos.puntos].sort((a, b) =>
    (RANGO_ESTADO[a.estado] - RANGO_ESTADO[b.estado])
    || ((b.lectura?.dias_sostenido?.dias ?? 0) - (a.lectura?.dias_sostenido?.dias ?? 0)))
  const sinVerificar = puntos.filter(p => p.estado === 'sin_verificar').length
  const hechos = datos.hechos || {}
  const regiones = Object.fromEntries(datos.regiones.map(r => [r.region_id, r]))

  return (
    <>
      <div className="panel-titulo">
        <span className="eyebrow">
          Puntos de cierre
          <Ayuda etiqueta="Qué dice esta tabla">{D.panel_nodos}</Ayuda>
        </span>
        {/* LO QUE FALTA, CONTADO — y contado DONDE SE CONSULTA. Este número
            vivía en la franja de arriba, lejos de la tabla donde están sus
            filas; aquí es un hecho con su contexto. El hecho, jamás el
            remedio. */}
        <span className={`panel-sub${sinVerificar ? ' hay' : ''}`}>
          {sinVerificar
            ? `${sinVerificar} de ${puntos.length} sin verificar`
            : `${puntos.length} puntos`}
        </span>
      </div>
      <div className="panel-tabla pulsable">
        <table>
          <thead>
            <tr>
              {/* La columna de la marca no lleva rótulo: lo que dice cada
                  forma está en la clave, al pie de esta misma tabla. Un
                  encabezado ahí solo podría decir «marca», que no informa. */}
              <th className="col-marca" aria-label="Marca en el mapa" />
              <th>Punto</th>
              <th>Estado</th>
              <th>Se hace</th>
              <th>Mesa</th>
              <th className="num">Días</th>
              <th>Vocería</th>
            </tr>
          </thead>
          <tbody>
            {puntos.map(p => {
              // EL RATÓN SEÑALA EN LOS DOS SENTIDOS. Pasarlo por la fila
              // enciende el punto en el mapa, y pasarlo por el punto enciende
              // la fila. Es la conexión que hace innecesario buscar: quien
              // pregunta «¿y ese cuál es?» lo tiene contestado antes de acabar
              // la frase, y desde el fondo de la sala.
              const mirado = sobre?.tipo === 'punto' && sobre.id === p.nodo_id
              const abierto = seleccionado === p.nodo_id
              return (
              <Fragment key={p.nodo_id}>
              <tr
                className={[
                  p.estado === 'cerrado' ? 'grave'
                    : p.estado === 'sin_verificar' ? 'aviso' : '',
                  seleccionado === p.nodo_id ? 'sel' : '',
                  mirado ? 'mirado' : '',
                ].filter(Boolean).join(' ')}
                onMouseEnter={() => onSobre?.({ tipo: 'punto', id: p.nodo_id })}
                onMouseLeave={() => onSobre?.(null)}
                onClick={() => onSeleccionar?.(
                  seleccionado === p.nodo_id ? null : p.nodo_id)}
              >
                <td className="col-marca">
                  <MarcaPunto punto={p} hechos={hechos[p.nodo_id]} />
                </td>
                <td style={{ color: 'var(--texto)' }}>
                  {p.nombre}
                  {/* EL CÓDIGO, debajo y en monoespacio. No se dice en voz alta
                      —para eso está el nombre— pero es lo que casa esta fila
                      con el globo del mapa y con la ficha de abajo, que son los
                      dos únicos sitios donde el punto se identifica por él. */}
                  <span className="celda-sub">
                    <span className="punto-id">{p.nodo_id}</span> · {p.region_id}
                  </span>
                </td>
                <td>
                  <span className={`chip chip-${CHIP_ESTADO[p.estado] || 'neutro'}`}>
                    {rotulo(ESTADO_PUNTO, p.estado)}
                  </span>
                </td>
                <td style={{ fontSize: '0.78rem' }}>
                  {rotulo(INTERVENCION_CORTA, p.intervencion)}
                </td>
                <td style={{ fontSize: '0.78rem' }}>
                  {p.mesa ? (
                    p.mesa.sesionada_hoy
                      ? <span className="chip chip-bien">sesionó hoy</span>
                      : p.mesa.congelada
                        ? <span className="chip chip-mal">congelada</span>
                        : <span className="chip chip-medio">instalada</span>
                  ) : '—'}
                </td>
                <td className="num">{p.lectura?.dias_sostenido?.dias ?? '—'}</td>
                <td><Banda lectura={p.lectura?.control_voceria} /></td>
              </tr>
              {abierto && (
                <FilaDetalle columnas={7}>
                  <DetallePunto
                    punto={p}
                    region={regiones[p.region_id]}
                    corredor={datos.corredores.find(
                      c => c.corredor_id === p.corredor_id)}
                  />
                </FilaDetalle>
              )}
              </Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* LA CLAVE, AL PIE DE LAS MARCAS QUE EXPLICA. Estaba debajo del mapa,
          a una columna de distancia de las formas que nombra. */}
      <ClaveDelMapa />
    </>
  )
}

function TablaCorredores({ datos, deltas }) {
  const corredores = [...datos.corredores].sort((a, b) => a.caudal - b.caudal)

  return (
    <>
      <div className="panel-titulo">
        <span className="eyebrow">
          Corredores
          <Ayuda etiqueta="Definiciones de las columnas">{D.corredores}</Ayuda>
        </span>
        <span className="panel-sub">menos flujo primero</span>
      </div>
      <div className="panel-tabla">
        <table>
          <thead>
            <tr>
              <th>Corredor</th>
              <th className="num">Flujo</th>
              <th className="num">
                Costo al día
                <Ayuda etiqueta="Qué mide el costo diario">{D.perdida_bloqueos}</Ayuda>
              </th>
              <th className="num">Población</th>
              <th>Prioridad</th>
            </tr>
          </thead>
          <tbody>
            {corredores.map(c => (
              <tr key={c.corredor_id}
                  className={c.caudal <= 0.05 ? 'grave' : c.caudal < 0.6 ? 'aviso' : ''}>
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
                  {Math.round(c.caudal * 100)}&nbsp;%
                  <Delta valor={(deltas?.[`caudal:${c.corredor_id}`] ?? 0) * 100} />
                </td>
                <td className="num"><Dinero valor={c.costo_diario} /></td>
                {/* «2.40 M» era un error de lectura esperando a ocurrir: en
                    español el punto separa los MILLARES, de modo que esa cifra
                    se lee «doscientos cuarenta millones» y no «dos millones y
                    medio». Va con coma decimal, como se escribe aquí. */}
                <td className="num">{millones(c.poblacion)}</td>
                <td style={{ fontSize: '0.78rem' }}>{c.clases.join(', ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="panel-pie">
        El costo es lo que se pierde con el corredor totalmente cerrado. La
        unidad va pegada a cada cifra.
      </p>
    </>
  )
}

function TablaRegiones({ datos, zoom, onZoom, sobre, onSobre }) {
  const regiones = [...datos.regiones].sort((a, b) =>
    ({ rojo: 0, ambar: 1, verde: 2 })[a.semaforo]
      - ({ rojo: 0, ambar: 1, verde: 2 })[b.semaforo]
    || (b.muertes_evitables - a.muertes_evitables))

  return (
    <>
      <div className="panel-titulo">
        <span className="eyebrow">
          Regiones · abastecimiento
          <Ayuda etiqueta="Definición del semáforo">{D.semaforo}</Ayuda>
        </span>
        <span className="panel-sub">toque para acercar el mapa</span>
      </div>
      <div className="panel-tabla pulsable">
        <table>
          <thead>
            <tr>
              <th>Región</th>
              <th>Estado</th>
              <th className="num">Muertes</th>
              <th>Flujo</th>
              <th>Bloqueo</th>
              <th>Apoyo</th>
            </tr>
          </thead>
          <tbody>
            {regiones.map(g => {
              // LA FILA ABRE EL MAPA. Tocar una región aquí es lo mismo que
              // tocarla en el lienzo: se acerca allá y se despliega aquí. Dos
              // maneras de hacer una sola cosa, y no dos cosas parecidas.
              const mirado = sobre?.tipo === 'region' && sobre.id === g.region_id
              const abierto = zoom === g.region_id
              return (
              <Fragment key={g.region_id}>
              <tr
                  className={[
                    g.semaforo === 'rojo' ? 'grave'
                      : g.semaforo === 'ambar' ? 'aviso' : '',
                    abierto ? 'sel' : '',
                    mirado ? 'mirado' : '',
                  ].filter(Boolean).join(' ')}
                  onMouseEnter={() => onSobre?.({ tipo: 'region', id: g.region_id })}
                  onMouseLeave={() => onSobre?.(null)}
                  onClick={() => onZoom?.(abierto ? null : g.region_id)}>
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
                  color: g.muertes_evitables ? 'var(--mal)' : 'var(--texto-3)',
                }}>
                  {g.muertes_evitables}
                </td>
                <td><Banda lectura={g.lectura?.caudal} /></td>
                <td><Banda lectura={g.lectura?.dias_sostenido} /></td>
                <td><Banda lectura={g.lectura?.apoyo_local} /></td>
              </tr>
              {abierto && (
                <FilaDetalle columnas={6}>
                  <DetalleRegion region={g} />
                </FilaDetalle>
              )}
              </Fragment>
              )
            })}
          </tbody>
        </table>
      </div>
    </>
  )
}

/** EL PLIEGO — el registro de lo decidido, con su responsable. Lo más nuevo
    arriba: durante la deliberación la sala vuelve a lo de esta jornada, no a lo
    del comienzo. */
function TablaPliego({ registro }) {
  const sinResponsable = (registro || []).filter(x => !x.responsable_nominado).length
  return (
    <>
      <div className="panel-titulo">
        <span className="eyebrow">
          Pliego de decisiones
          <Ayuda etiqueta="Qué es el pliego">{D.pliego}</Ayuda>
        </span>
        <span className={`panel-sub${sinResponsable ? ' hay' : ''}`}>
          {sinResponsable
            ? `${sinResponsable} sin responsable`
            : 'lo más nuevo arriba'}
        </span>
      </div>
      <div className="panel-tabla">
        {registro?.length ? (
          <table>
            <thead>
              <tr><th className="num">J</th><th>Rol</th><th>Decisión</th><th>Responsable</th></tr>
            </thead>
            <tbody>
              {registro.slice().reverse().map((x, i) => (
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
            Sin decisiones registradas todavía.
          </p>
        )}
      </div>
    </>
  )
}
