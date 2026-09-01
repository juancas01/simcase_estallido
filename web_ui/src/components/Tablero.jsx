// ---------------------------------------------------------------------------
// EL TABLERO — UNA PANTALLA, SIN DESPLAZAMIENTO, EN PESTAÑAS.
//
// La regla de esta superficie es dura y simple: **nunca hay que hacer scroll
// para ver nada.** Lo que no cabe en la pantalla no se apila debajo — se
// convierte en pestaña o se condensa.
//
//     SALA               la vista general: estado del país, mapa, territorio
//     un rol × 7         su cartera: alerta, detalle y qué se puede pedir hoy
//
// La pestaña activa es una decisión de la sala, no del sistema: se proyecta lo
// que la conversación necesita en cada momento, y volver a la sala entera es
// un clic al lado de donde se está.
//
//
// LA FRANJA DE ESTADO, NO LA BANDA DE TARJETAS
// ============================================
// Las métricas globales vivían en cuatro tarjetas con medidores —dos filas de
// pantalla— y esa altura era justamente la que empujaba el mapa fuera de la
// vista. Ahora es UNA franja de tres líneas que siempre está en pantalla:
//
//   · el PLAZO ....... jornada, fecha, franja y cuántas jornadas quedan
//   · el MARCADOR .... muertes evitables, pérdida diaria por bloqueos y
//                      escuadrones libres — lo que se cuenta de verdad
//   · lo que PIENSA el país y el mundo — encuadre y las cinco magnitudes,
//                      cada una en su palabra de color y sin cifra
//   · lo QUE FALTA ... puntos sin mirar, denuncias abiertas, decisiones
//                      sin responsable
//
// Lo que se fue de la franja no se perdió: la percepción completa con sus
// escalas sigue en los globos de ayuda, y el detalle por cartera está a una
// pestaña. Un nivel se interpreta; un número se optimiza.
//
//
// EL PAPEL Y LA PANTALLA SE REPARTIERON EL TRABAJO
// ================================================
// La guía de acciones —qué hace, qué hace falta antes, cómo se dice— va
// IMPRESA en la mesa. La pantalla no la repite: muestra lo único que el papel
// no puede, el semáforo de HOY, en la pestaña de cada rol.
//
//
// LA NOCHE TIENE SU FRANJA
// ========================
// Los dos minutos de consecuencias son para leer QUÉ PRODUJO lo ordenado, y
// esa lectura no puede competir con scroll. La franja de consecuencias entra
// entre las pestañas y el territorio, con su propio desplazamiento interno si
// la jornada fue larga — y desaparece sola al abrir la jornada siguiente.
//
// LO QUE NUNCA MUESTRA: la mezcla real de un punto, ni si una denuncia es
// cierta. Tampoco por la puerta de atrás de una tendencia.
// ---------------------------------------------------------------------------

import { useEffect, useRef, useState } from 'react'
import Mapa from './Mapa'
import EsferaContenido, { ENCUADRE, sinVerificar } from './EsferaContenido'
import Cronometro from './Cronometro'
import Cabecera from './Cabecera'
import PanelTerritorio from './PanelTerritorio'
import VistaRol from './VistaRol'
import Ayuda, { Titulo } from './Ayuda'
import { D } from '../definiciones.jsx'
import { EVENTO, FRANJA, POSICION_GREMIOS, rotulo } from '../etiquetas.jsx'
import {
  Cargando, Dinero, NIVELES, ROLES, Tendencia, colorPeldano, peldano, useDatos,
} from '../comun.jsx'

const CLAVE_BARRA = 'simcase:esfera_abierta'

/** Recuerda si la barra quedó abierta. Si el navegador no deja guardar, da igual. */
function usePreferencia(clave, inicial) {
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
  const { datos, error } = useDatos('/tablero')
  const { datos: esfera } = useDatos('/esfera')
  // EL ESTADO DEL TERRITORIO VIVE AQUÍ, no dentro del mapa.
  //
  // Eran del mapa —él sabía qué región estaba abierta y qué punto tenía el ratón
  // encima— y mientras la ficha colgaba de él eso bastaba. Ahora la ficha está en
  // el panel de al lado y la tabla necesita las dos cosas: para saber qué
  // detallar, y para que **pasar el ratón por una fila encienda su punto en el
  // mapa**. Un estado que dos hermanos necesitan es del padre.
  //
  // LO FIJADO CON UN CLIC MANDA sobre lo que se está mirando: el ratón resalta,
  // el clic despliega. En una pantalla proyectada quien mueve el ratón no es
  // quien habla, y lo que la mesa discute tiene que quedarse quieto mientras
  // alguien busca otra cosa.
  const [sel, setSel] = useState(null)        // el punto FIJADO con un clic
  const [zoom, setZoom] = useState(null)      // region_id, o null para el país
  const [sobre, setSobre] = useState(null)    // {tipo:'region'|'punto', id}
  // La pestaña de la sala es la vista general; las demás son el id del rol.
  const [pestana, setPestana] = useState('sala')
  const [abierta, setAbierta] = usePreferencia(CLAVE_BARRA, true)

  // Cuántas publicaciones había la última vez que la barra estuvo abierta, para
  // avisar de que entró algo nuevo mientras estaba plegada.
  const vistasHasta = useRef(0)
  const totalPubs = esfera?.publicaciones?.length ?? 0
  useEffect(() => {
    if (abierta) vistasHasta.current = totalPubs
  }, [abierta, totalPubs])

  if (!datos) return <Cargando error={error} ruta="/tablero" />

  const abiertas = sinVerificar(esfera).length
  const nuevas = Math.max(0, totalPubs - vistasHasta.current)
  const enc = ENCUADRE[esfera?.encuadre_dominante] || null

  return (
    <div className="pantalla pantalla-fija">
      <Cabecera
        eyebrow="Tablero de situación · para proyectar"
        titulo="Puesto de Mando Unificado"
        a="consola"
      >
        <div className="cabecera-reloj">
          <Cronometro cronometro={datos.cronometro} />
          <Ayuda etiqueta="Cómo corre el reloj de la jornada">{D.cronometro}</Ayuda>
        </div>
        <button
          className="mando-esfera"
          onClick={() => setAbierta(a => !a)}
          aria-expanded={abierta}
          aria-controls="esfera-lateral"
        >
          {abierta ? 'Ocultar' : 'Mostrar'} esfera pública
          {!abierta && (abiertas > 0 || nuevas > 0) && (
            <span className="aviso-barra">{abiertas > 0 ? abiertas : nuevas}</span>
          )}
        </button>
      </Cabecera>

      {/* --- las pestañas: la sala entera o la cartera de un rol ---------- */}
      <div className="pestanas-rol" role="tablist" aria-label="Vista general o cartera de un rol">
        <button
          role="tab" aria-selected={pestana === 'sala'}
          className={`pestana-rol${pestana === 'sala' ? ' activa' : ''}`}
          onClick={() => setPestana('sala')}
        >
          Sala
        </button>
        {ROLES.map(r => (
          <button
            key={r.id}
            role="tab" aria-selected={pestana === r.id}
            title={r.nombre}
            className={`pestana-rol${pestana === r.id ? ' activa' : ''}`}
            onClick={() => setPestana(r.id)}
          >
            {r.id}
          </button>
        ))}
      </div>

      <div className="con-lateral">
        <main className="cuerpo cuerpo-fijo">
          {pestana === 'sala'
            ? <Sala
                datos={datos}
                sel={sel} onSeleccionar={setSel}
                zoom={zoom} onZoom={setZoom}
                sobre={sobre} onSobre={setSobre}
              />
            : <VistaRol rol={pestana} />}
        </main>

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

// ---------------------------------------------------------------------------
// LA SALA — la vista general: franja de estado y territorio, sin más.
// ---------------------------------------------------------------------------

function Sala({ datos, sel, onSeleccionar, zoom, onZoom, sobre, onSobre }) {
  const r = datos.reservas
  const d = datos.deltas || {}
  const esNoche = datos.fase === 'noche'

  // LA PÉRDIDA POR BLOQUEOS: el costo diario de cada corredor por la parte de
  // su flujo que no circula. Es un hecho público — el costo diario es la mitad
  // del criterio de priorización que Transporte adopta delante de la mesa.
  const perdidaDia = datos.corredores.reduce(
    (s, c) => s + (c.costo_diario || 0) * (1 - c.caudal), 0)
  const dPerdida = -datos.corredores.reduce(
    (s, c) => s + (c.costo_diario || 0) * (d[`caudal:${c.corredor_id}`] ?? 0), 0)
  const cerrados = datos.corredores.filter(c => c.caudal <= 0.05).length

  // EL NÚMERO QUE DICE SI SE VA GANANDO. Es la tarea del ejercicio —abrir el
  // país— y hasta ahora solo se sabía contando filas en la tabla de nodos, que
  // es justo lo que nadie hace desde el fondo de una sala. Un punto cuenta como
  // abierto con el mismo criterio que usa el motor, no con uno propio.
  const abiertos = datos.puntos.filter(p => p.estado === 'abierto').length
  const sinVerificarPuntos = datos.puntos.filter(p => p.estado === 'sin_verificar').length

  // LAS REGIONES EN ROJO VAN BAJO LAS MUERTES, y no en un indicador aparte,
  // porque son su causa: el acumulador de muertes es irreversible y va a la
  // zaga, y el semáforo en rojo dice de dónde van a salir las siguientes.
  const rojas = datos.regiones.filter(g => g.semaforo === 'rojo').length

  // LA MESA: lo que condiciona qué se puede pedir mañana. No mide el país sino
  // la conversación, y por eso va en su propia zona y no en el marcador.
  const sinResponsable = (datos.registro || [])
    .filter(x => !x.responsable_nominado).length

  // Las cinco magnitudes de opinión, cada una en su palabra de color.
  const percepcion = [
    { nombre: 'Presión', valor: datos.presion_calle, sentido: 'arriba_peor',
      ayuda: D.presion_calle, delta: d.presion_calle },
    { nombre: 'Legitimidad', valor: r.legitimidad, ayuda: D.legitimidad,
      delta: d.legitimidad },
    { nombre: 'Credibilidad', valor: r.credibilidad_mesa,
      ayuda: D.credibilidad_mesa, delta: d.credibilidad_mesa },
    { nombre: 'Respaldo', valor: r.respaldo_internacional,
      ayuda: D.respaldo_internacional, delta: d.respaldo_internacional },
    { nombre: 'Cohesión', valor: r.cohesion_mesa, ayuda: D.cohesion_mesa,
      delta: d.cohesion_mesa },
  ]

  const reloj = datos.reloj

  return (
    <>
      {/* --- la noche: qué produjo lo que se ordenó ---------------------- */}
      {esNoche && datos.consecuencias && (
        <Consecuencias datos={datos.consecuencias} />
      )}

      {/* --- la cabecera de estado: tres zonas rotuladas -------------------
          Una sola línea por zona, y cada zona con su nombre encima. Lo que
          estaba antes —cuatro grupos de chips envueltos en cinco renglones—
          decía lo mismo y se leía como datos regados: sin rótulo no hay
          grupo, y sin grupo no hay comprensión, solo información. */}
      <div className="franja-estado">
        {/* EL PLAZO. Lo que de verdad vence: una concertación tarda dos. */}
        <div className="franja-zona">
          <span className="eyebrow">
            El plazo
            <Ayuda etiqueta="Cómo corre el tiempo del ejercicio">{D.reloj}</Ayuda>
          </span>
          {reloj ? (
            <>
              <span className="franja-cifra">
                {reloj.jornada === 0 ? 'Antes de abrir'
                  : <>Jornada {reloj.jornada}
                     <span className="franja-de">/{reloj.jornadas_totales}</span></>}
              </span>
              <span className="franja-linea">
                {reloj.fecha}
                <span className={`chip chip-${reloj.franja === 'noche' ? 'medio' : 'neutro'}`}>
                  {rotulo(FRANJA, reloj.franja)}
                </span>
                {reloj.jornadas_restantes === 0
                  ? <em className="franja-ultima">última jornada</em>
                  : reloj.jornadas_restantes === 1
                    ? <em className="franja-ultima">queda una jornada</em>
                    : null}
              </span>
            </>
          ) : null}
        </div>

        {/* EL MARCADOR. Lo que se cuenta de verdad: personas, pesos, unidades. */}
        <div className="franja-zona franja-zona-marca">
          <span className="eyebrow">El marcador</span>
          <div className="franja-kpis">
            <span className="kpi">
              <span className="kpi-rotulo">
                Puntos abiertos
                <Ayuda etiqueta="Qué cuenta como punto abierto">{D.puntos_abiertos}</Ayuda>
              </span>
              <span className={`kpi-valor${abiertos > 0 ? ' bien' : ''}`}>
                {abiertos}
                <span className="franja-de">/{datos.puntos.length}</span>
              </span>
              {sinVerificarPuntos > 0 && (
                <span className="kpi-sub">{sinVerificarPuntos} sin verificar</span>
              )}
            </span>
            <span className="kpi">
              <span className="kpi-rotulo">
                Muertes evitables
                <Ayuda etiqueta="Definición de muertes evitables">{D.muertes_evitables}</Ayuda>
              </span>
              <span className={`kpi-valor${datos.muertes_evitables > 0 ? ' mal' : ''}`}>
                {datos.muertes_evitables}
                <Tendencia valor={d.muertes_evitables} sentido="arriba_peor" />
              </span>
              {rojas > 0 && (
                <span className="kpi-sub mal">
                  {rojas} regi{rojas === 1 ? 'ón' : 'ones'} en rojo
                </span>
              )}
            </span>
            <span className="kpi">
              <span className="kpi-rotulo">
                Perdido al día
                <Ayuda etiqueta="Qué mide la pérdida por bloqueos">{D.perdida_bloqueos}</Ayuda>
              </span>
              <span className="kpi-valor">
                <Dinero valor={perdidaDia} />
                <Tendencia valor={dPerdida} sentido="arriba_peor" />
              </span>
              <span className="kpi-sub">{cerrados} corredor{cerrados === 1 ? '' : 'es'} cerrado{cerrados === 1 ? '' : 's'}</span>
            </span>
            <span className="kpi">
              <span className="kpi-rotulo">
                Escuadrones libres
                <Ayuda etiqueta="La fuerza disponible">{D.fuerza}</Ayuda>
              </span>
              <span className="kpi-valor">
                {datos.fuerza.esmad_sin_comprometer}
                <span className="franja-de">/{datos.fuerza.esmad_total}</span>
                <Tendencia valor={d.esmad_sin_comprometer} />
              </span>
            </span>
          </div>
        </div>

        {/* LO QUE PIENSA EL PAÍS. Una palabra de color por magnitud. El
            ENCUADRE no va aquí: es narrativa, y la narrativa vive en la esfera
            pública de al lado — cada cosa en su sitio es lo que hace legible
            la cabecera. */}
        <div className="franja-zona">
          <span className="eyebrow">
            Lo que piensa el país
            <Ayuda etiqueta="Las cinco magnitudes de opinión">{D.metricas}</Ayuda>
          </span>
          <div className="franja-kpis">
            {percepcion.map(m => (
              <span key={m.nombre} className="kpi">
                <span className="kpi-rotulo">
                  {m.nombre}
                  <Ayuda etiqueta={`Definición de ${m.nombre}`}>{m.ayuda}</Ayuda>
                </span>
                <span className="kpi-valor kpi-palabra"
                      style={{ color: colorPeldano(peldano(m.valor), m.sentido) }}>
                  {NIVELES[peldano(m.valor)]}
                  <Tendencia valor={m.delta} sentido={m.sentido} />
                </span>
              </span>
            ))}
          </div>
        </div>

        {/* LA MESA. Las tres primeras zonas miden el país; esta mide la
            conversación que lo está conduciendo, que es lo que decide qué se
            puede pedir mañana. Un Comité levantado y unos gremios sumados no
            son malas noticias: son puertas que se cierran, y la sala tiene que
            verlas cerrarse mientras todavía puede hacer algo. */}
        <div className="franja-zona">
          <span className="eyebrow">
            La mesa
            <Ayuda etiqueta="Qué condiciona lo que se puede pedir">{D.estado_mesa}</Ayuda>
          </span>
          <div className="franja-kpis">
            <span className="kpi">
              <span className="kpi-rotulo">Comité del paro</span>
              <span className="kpi-valor kpi-palabra" style={{
                color: datos.comite_disponible ? 'var(--bien)' : 'var(--mal)',
              }}>
                {datos.comite_disponible ? 'Sentado' : 'Levantado'}
              </span>
            </span>
            <span className="kpi">
              <span className="kpi-rotulo">Gremios</span>
              <span className="kpi-valor kpi-palabra" style={{
                color: datos.posicion_gremios === 'sumados' ? 'var(--mal)'
                  : datos.posicion_gremios === 'evaluando' ? 'var(--medio)'
                    : 'var(--bien)',
              }}>
                {rotulo(POSICION_GREMIOS, datos.posicion_gremios)}
              </span>
            </span>
            <span className="kpi">
              <span className="kpi-rotulo">Sin responsable</span>
              <span className={`kpi-valor${sinResponsable > 0 ? ' medio' : ''}`}>
                {sinResponsable}
              </span>
            </span>
            <span className="kpi">
              <span className="kpi-rotulo">En cola</span>
              <span className="kpi-valor">{datos.en_cola ?? 0}</span>
              {(datos.en_cola ?? 0) > 0 && (
                <span className="kpi-sub">se resuelven de noche</span>
              )}
            </span>
          </div>
        </div>
      </div>

      {/* --- el territorio: mapa + panel, el resto de la pantalla --------- */}
      {/* SIN RÓTULO «TERRITORIO». Había tres títulos apilados aquí —el de la
          tarjeta, el del mapa («Colombia», o la región abierta) y el de la
          pestaña del panel— y los tres nombran lo mismo con distinta letra. El
          de la tarjeta era además el único que no decía nada que no se viera:
          debajo hay un mapa. Su globo de ayuda tampoco se pierde, era el mismo
          `D.corredores` que ya cuelga de la pestaña de corredores. Lo que se
          gana es un renglón de alto, y en esta pantalla el alto es del mapa. */}
      <div className="tarjeta tarjeta-territorio">
        <div className="territorio">
          {/* Sin caja intermedia: `.mapa` ES la columna, y reparte su alto
              entre el título, el lienzo —que se queda con lo que sobre— la
              ficha y la leyenda. La caja de antes era el bloque relativo que
              dejaba al lienzo cubrir a los otros tres. */}
          <Mapa
            tablero={datos}
            seleccionado={sel} onSeleccionar={onSeleccionar}
            zoom={zoom} onZoom={onZoom}
            sobre={sobre} onSobre={onSobre}
          />
          <PanelTerritorio
            datos={datos} deltas={d} registro={datos.registro}
            seleccionado={sel} onSeleccionar={onSeleccionar}
            sobre={sobre} onSobre={onSobre}
            zoom={zoom} onZoom={onZoom}
          />
        </div>
      </div>
    </>
  )
}

/**
 * QUÉ PRODUJO LO QUE SE ORDENÓ — solo durante los dos minutos de noche.
 *
 * Es una FRANJA y no una tarjeta alta: la noche no retira el mapa, y leer las
 * consecuencias no puede costar el desplazamiento que la regla de esta
 * superficie prohíbe. Si la jornada fue larga, la franja desplaza por dentro.
 *
 * NO INTERPRETA. Enumera lo que el motor devolvió, con sus propias frases: la
 * lectura de qué significa es de la sala.
 */
function Consecuencias({ datos }) {
  const eventos = (datos.eventos || []).filter(e => e.tipo || e.evento)
  return (
    <div className="tarjeta consecuencias consecuencias-franja">
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
