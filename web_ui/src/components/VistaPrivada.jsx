// ---------------------------------------------------------------------------
// SUPERFICIE 2 · LA VISTA PRIVADA — en el dispositivo de cada uno.
//
//     El tablero responde QUÉ ESTÁ PASANDO.
//     Esta responde CUÁNTO, DÓNDE EXACTAMENTE Y DESDE CUÁNDO.
//
// Es PERSONAL, NO CONFIDENCIAL: el sistema solo se la muestra a su titular, pero
// nadie está obligado a callársela y el ejercicio quiere que se comparta. Lo que
// la hace valiosa no es que esté oculta — es que hay una sola persona que la
// tiene actualizada.
//
// LAS CINCO REGLAS QUE IMPIDEN QUE LA SALA MIRE PANTALLAS
//   1 · cabe en una pantalla y NO tiene desplazamiento — tres bloques
//   2 · nadie ordena desde aquí: es de solo lectura
//   3 · la ficha de rol y la agenda reservada van en papel
//   4 · no repite lo que ya está en el tablero
//   5 · dice qué se puede pedir HOY, para no gastar deliberación en lo que no
//
//
// LA GUÍA DE ACCIONES ES UNA TABLA, Y ESO ES EL DISEÑO
// ====================================================
// Era una lista. Cada acción traía lo que hace y si hoy se puede pedir, y con
// eso su titular seguía sin poder contestar las dos preguntas que de verdad se
// hace mirando su repertorio: **¿qué hace falta antes?** y **¿cómo se dice
// esto en voz alta?**
//
// Cuatro columnas, y cada una contesta una cosa distinta:
//
//     TIPO        constituye · toca el mundo · informa
//     ACCIÓN      qué hace y qué cambia, y debajo el nombre del acto
//     REQUISITOS  qué hace falta antes — EN CUALITATIVO, NUNCA UNA CIFRA
//     EN CONSOLA  una frase que funciona, tal cual
//
// EL REQUISITO NO LLEVA CIFRA, y es la misma regla que gobierna el tablero: un
// nivel se interpreta, un número se optimiza. «Escuadrones sin comprometer»
// obliga a preguntarle al Director de la Policía si los hay; «dos escuadrones»
// invita a contar hasta dos y pedirla ahí. Lo primero empuja la conversación a
// la mesa, que es donde el ejercicio la quiere. Hay una prueba en el motor que
// vigila que en esa columna no entre ningún dígito.
//
// EL EJEMPLO FUNCIONA DE VERDAD. No es una paráfrasis: es la frase que produce
// la acción, y hay una prueba que las pasa todas por el intérprete. Un ejemplo
// que no funciona se dicta delante de la mesa y la consola contesta que no lo
// entiende — peor que no dar ninguno.
//
//
// EL REPERTORIO LLEVA SEMÁFORO
// ============================
// Cada acción dice ahora si se puede pedir **ahora mismo** y, si no, qué falta.
// Antes era una lista plana de cuatro o cinco líneas, y de ellas dos podían
// llevar tres jornadas bloqueadas sin que su titular tuviera forma de saberlo:
// lo descubría dictándola en voz alta y recibiendo el rechazo delante de la
// mesa. Eso no es información incompleta —que es el objeto del ejercicio—, es
// una interfaz que esconde una regla que ya conoce.
//
//     Se puede pedir     verde    hoy sale
//     Con reparos        ámbar    sale, y hay algo que conviene saber antes
//     Aún no             rojo     falta algo que otro tiene que hacer primero
//     Ya vigente         gris     está puesta; volver a pedirla no cambia nada
//
// EL REQUISITO SE ENUNCIA EN GENERAL, y esa restricción es la que sostiene la
// pieza. «Requiere que el Presidente firme la asistencia militar» es un hecho
// sobre el mundo. «Pida al Presidente que firme y opere el Puente Amarillo»
// sería la pantalla decidiendo por la sala — y en cuanto la pantalla decide,
// deja de haber ejercicio.
//
// Y ES LO QUE EMPUJA LA CONVERSACIÓN A LA MESA: quien lee «falta escolta ·
// Director General de la Policía» sabe a quién tiene que pedírselo, y eso pasa
// en voz alta y no en un menú.
//
//
// EL REPERTORIO SE LEE EN CLARO, NO EN NOMBRE DE ACTO
// ---------------------------------------------------
// Cada acción se muestra por lo que HACE —«autoriza que el Ejército apoye a la
// Policía»— y no por cómo se llama —«acto administrativo de asistencia
// militar». El nombre formal sigue debajo, en pequeño, porque es el que va al
// pliego; pero deja de ser lo primero que se lee.
// ---------------------------------------------------------------------------

import Ayuda, { Titulo } from './Ayuda'
import Navegacion from './Navegacion'
import Cronometro from './Cronometro'
import { D } from '../definiciones.jsx'
import {
  CHIP_CLASE, CHIP_DISPONIBILIDAD, CLASE_ACCION, DISPONIBILIDAD, FRANJA, rotulo,
} from '../etiquetas.jsx'
import { Cargando, ROLES, useDatos } from '../comun.jsx'

/** Bloqueadas al final: lo que hoy no se puede pedir no compite por el ojo. */
const ORDEN_DISPONIBILIDAD = {
  disponible: 0, condicionada: 1, hecha: 2, bloqueada: 3,
}

export default function VistaPrivada({ rol }) {
  const ruta = `/vista/${encodeURIComponent(rol)}`
  const { datos, error } = useDatos(ruta)
  if (!datos) return <Cargando error={error} ruta={ruta} />

  const ficha = ROLES.find(r => r.id === rol)
  const acciones = [...(datos.acciones || [])].sort((a, b) =>
    (ORDEN_DISPONIBILIDAD[a.disponibilidad?.estado ?? 'disponible'] ?? 0)
    - (ORDEN_DISPONIBILIDAD[b.disponibilidad?.estado ?? 'disponible'] ?? 0))

  const jornada = datos.cronometro?.jornada ?? datos.turno

  return (
    <div className="pantalla">
      <header className="cabecera">
        <div>
          <div className="cabecera-rotulo">
            <span className="eyebrow">{ficha?.frente} · vista personal</span>
            <Navegacion />
          </div>
          <h1>{ficha?.nombre || rol}</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem' }}>
          <div style={{ textAlign: 'right' }}>
            <div className="num" style={{ fontSize: '1rem', fontWeight: 600 }}>
              {jornada > 0 ? `Jornada ${jornada}` : 'Antes de la apertura'}
              {' · '}{rotulo(FRANJA, datos.franja)}
            </div>
          </div>
          {/* El mismo cronómetro que el tablero. Que el titular vea en su
              dispositivo lo que la sala ve en la pared es la mitad del asunto:
              la otra mitad es que no tenga que preguntar cuánto queda. */}
          <Cronometro cronometro={datos.cronometro} />
          <Ayuda etiqueta="Cómo corre el reloj de la jornada">{D.cronometro}</Ayuda>
        </div>
      </header>

      <div className="cuerpo" style={{ maxWidth: 900, width: '100%', margin: '0 auto' }}>
        {/* --- BLOQUE 0 · la pregunta del comienzo del día ----------------
            Solo la reciben los dos que pueden convocar una mesa. Va ARRIBA DEL
            TODO y no dentro del detalle porque es lo único de esta pantalla
            que caduca: se contesta hoy o se pierde la jornada. */}
        {datos.notificacion && <Notificacion aviso={datos.notificacion} />}

        {/* --- BLOQUE 1 · su alerta -------------------------------------- */}
        <div className="alerta">
          <span className="eyebrow">
            Lo más urgente
            <Ayuda etiqueta="Cómo se calcula esta alerta">{D.alerta_privada}</Ayuda>
          </span>
          <p>{datos.alerta}</p>
        </div>

        {/* --- BLOQUE 2 · su detalle ------------------------------------- */}
        <div className="tarjeta">
          <Titulo ayuda={D.detalle_privado}>El detalle de su cartera</Titulo>
          <Detalle datos={datos.detalle} />
        </div>

        {/* --- BLOQUE 3 · la guía de acciones ----------------------------
            Es una guía, NO un panel de control: nadie ordena desde su
            pantalla. Lo que añade es poder contestar, antes de hablar, las tres
            preguntas de quien va a pedir algo — si hoy sale, qué hace falta
            antes, y cómo se dice. */}
        {acciones.length > 0 && (
          <div className="tarjeta" style={{ marginTop: '1rem' }}>
            <Titulo ayuda={D.repertorio}>Guía de acciones</Titulo>
            {!datos.admite_ordenes && (
              <p className="repertorio-noche">
                Es de noche: la consola no recibe órdenes hasta la jornada
                siguiente. Esto es lo que podrá pedir cuando abra.
              </p>
            )}
            <div className="guia-envoltura">
              <table className="guia">
                <thead>
                  <tr>
                    <th>Hoy</th>
                    <th>
                      Tipo
                      <Ayuda etiqueta="Los tres tipos de acción">
                        {D.clases_accion}
                      </Ayuda>
                    </th>
                    <th>Acción y efecto</th>
                    <th>
                      Requisitos previos
                      <Ayuda etiqueta="Qué es un requisito previo">
                        {D.requisitos_previos}
                      </Ayuda>
                    </th>
                    <th>
                      Cómo pedirla en la consola
                      <Ayuda etiqueta="Cómo se usan estos ejemplos">
                        {D.ejemplo_consola}
                      </Ayuda>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {acciones.map(a => (
                    <Accion key={a.accion} accion={a} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <p style={{ marginTop: '1.25rem', fontSize: '0.78rem', color: 'var(--texto-3)',
                    textAlign: 'center' }}>
          Personal, no confidencial · solo lectura
          <Ayuda etiqueta="Qué significa personal, no confidencial">
            {D.vista_personal}
          </Ayuda>
        </p>
      </div>
    </div>
  )
}

/**
 * Una fila de la guía: el semáforo, el tipo, cómo se llama y qué hace, qué hace
 * falta antes y cómo se pide.
 *
 * LAS DOS CLASES DE REQUISITO VAN EN COLUMNAS DISTINTAS, y separarlas es la
 * mitad de la pieza:
 *
 *   · `requisitos_previos` es un hecho sobre la acción — no cambia nunca y no
 *     lleva cifras. Es la columna que se lee para entender de qué depende cada
 *     cosa antes de que empiece la jornada.
 *   · `disponibilidad.requisito` es el estado de HOY — sí puede llevar cifras,
 *     porque cuenta lo que hay. Va bajo el semáforo, que es de lo que habla.
 *
 * Mezclarlas dejaba una sola frase que unas veces describía la acción y otras
 * el momento, y no se sabía cuál se estaba leyendo.
 */
function Accion({ accion: a }) {
  const disp = a.disponibilidad || { estado: 'disponible' }
  const chip = CHIP_DISPONIBILIDAD[disp.estado] || 'neutro'

  return (
    <tr className={`accion-fila accion-${disp.estado}`}>
      <td>
        <span className={`chip chip-${chip}`}>
          {rotulo(DISPONIBILIDAD, disp.estado)}
        </span>
        {/* Por qué hoy no, o con qué reparo. Aquí sí caben cifras: esta celda
            habla del estado de hoy y no de la acción. */}
        {disp.requisito && <div className="accion-requisito">{disp.requisito}</div>}
        {disp.habilitada_por?.length > 0 && (
          <div className="accion-habilita">
            Lo habilita: {disp.habilitada_por.join(' · ')}
          </div>
        )}
      </td>

      <td>
        <span className={`chip chip-${CHIP_CLASE[a.clase] || 'neutro'} chip-clase`}>
          {rotulo(CLASE_ACCION, a.clase)}
        </span>
      </td>

      {/* TRES RENGLONES, DE MÁS CORTO A MÁS PRECISO, y ese orden es la pieza.
          Primero el nombre en verbo —«Autorizar al Ejército»—, que es lo que se
          busca con el ojo y lo que se dice en voz alta. Debajo, qué cambia si se
          pide. Y al final, en pequeño, el nombre formal del acto —«Acto
          administrativo de asistencia militar»—, que no se pierde porque es el
          que va al pliego, pero que ya no es lo primero que hay que descifrar
          para saber si esta fila es la que se buscaba. */}
      <td>
        <div className="accion-nombre">{a.nombre || a.descripcion}</div>
        {a.en_claro && <div className="accion-claro">{a.en_claro}</div>}
        {a.nombre && a.descripcion !== a.nombre && (
          <div className="nombre-formal">{a.descripcion}</div>
        )}
      </td>

      <td className="accion-previos">{a.requisitos_previos || '—'}</td>

      {/* Las treinta y nueve tienen ejemplo, y hay una prueba en el motor que
          lo exige. Ocho no lo tuvieron, y esta celda dibujaba en su lugar un
          «todavía no se transcribe» que ya no puede ocurrir. */}
      <td>
        <code className="accion-ejemplo">{a.ejemplo_consola}</code>
      </td>
    </tr>
  )
}

/**
 * LA PREGUNTA DEL COMIENZO DEL DÍA — solo para quien puede convocar una mesa.
 *
 * Es una PREGUNTA y no un aviso, y menos todavía una instrucción. Dice dónde
 * hay mesa instalada, cuál lleva jornadas parada y por qué eso importa; qué
 * hacer con ello es de la sala. «¿Avanza hoy en la mesa del Puente Amarillo?»
 * es un hecho puesto delante de quien decide; «instale la mesa del Puente
 * Amarillo» sería la pantalla decidiendo, y ahí se acabó el ejercicio.
 */
function Notificacion({ aviso }) {
  return (
    <div className="notificacion">
      <span className="eyebrow">
        Al abrir la jornada
        <Ayuda etiqueta="Por qué llega esta pregunta">{D.mesas_diarias}</Ayuda>
      </span>
      <p className="notificacion-pregunta">{aviso.pregunta}</p>
      <p className="notificacion-porque">{aviso.porque}</p>
      <ul className="notificacion-mesas">
        {aviso.mesas.map(m => (
          <li key={m.nodo_id}>
            <strong>{m.punto}</strong>
            <span className="notificacion-avance">{m.avance}</span>
            {m.jornadas_congelada > 0 && (
              <span className="chip chip-medio">
                {m.jornadas_congelada} jornada
                {m.jornadas_congelada === 1 ? '' : 's'} congelada
                {m.jornadas_congelada === 1 ? '' : 's'}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}

/** Renderiza el detalle sea cual sea su forma, sin que la interfaz duplique el
    esquema del motor. Un dato en dos sitios se desincroniza. Siempre. */
function Detalle({ datos }) {
  const campos = Object.entries(datos || {})
  if (!campos.length) {
    return <p style={{ margin: 0, color: 'var(--texto-3)' }}>
      Su cartera todavía no tiene nada que reportar en esta jornada.
    </p>
  }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
      {campos
        .filter(([k]) => !k.startsWith('_'))
        .map(([clave, valor]) => (
          <Campo key={clave} clave={clave} valor={valor} />
        ))}
      {campos.filter(([k]) => k.startsWith('_')).map(([k, v]) => (
        <p key={k} style={{ margin: 0, fontSize: '0.78rem', color: 'var(--medio)',
                            fontStyle: 'italic' }}>
          {String(v)}
        </p>
      ))}
    </div>
  )
}

const etiqueta = (k) => k.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase())

function Campo({ clave, valor }) {
  if (Array.isArray(valor)) {
    if (!valor.length) {
      return <Simple clave={clave} valor="ninguno" />
    }
    // Una lista con huecos no puede tumbar la pantalla entera: `Object.keys` de
    // `null` lanza, y lo que se llevaría por delante es la vista completa de su
    // titular en mitad de la jornada.
    const filas = valor.filter(x => x !== null && x !== undefined)
    if (!filas.length) return <Simple clave={clave} valor="ninguno" />

    if (typeof filas[0] === 'object') {
      const columnas = [...new Set(filas.flatMap(f => Object.keys(f)))]
      return (
        <div>
          <div className="eyebrow" style={{ marginBottom: '0.35rem' }}>{etiqueta(clave)}</div>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>{columnas.map(c => <th key={c}>{etiqueta(c)}</th>)}</tr>
              </thead>
              <tbody>
                {filas.map((fila, i) => (
                  <tr key={i}>
                    {columnas.map(c => (
                      <td key={c} className={typeof fila[c] === 'number' ? 'num' : ''}
                          style={{ color: resalta(c, fila[c]) }}>
                        {formatear(fila[c])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )
    }
    return <Simple clave={clave} valor={filas.join(' · ')} />
  }

  if (valor && typeof valor === 'object') {
    return (
      <div>
        <div className="eyebrow" style={{ marginBottom: '0.35rem' }}>{etiqueta(clave)}</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem 1.5rem' }}>
          {Object.entries(valor).map(([k, v]) => (
            <span key={k} style={{ fontSize: '0.88rem' }}>
              <span style={{ color: 'var(--texto-3)' }}>{etiqueta(k)}: </span>
              <span className="num" style={{ color: resalta(k, v) }}>{formatear(v)}</span>
            </span>
          ))}
        </div>
      </div>
    )
  }

  return <Simple clave={clave} valor={formatear(valor)} color={resalta(clave, valor)} />
}

function Simple({ clave, valor, color }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between',
                  alignItems: 'baseline', gap: '1rem' }}>
      <span style={{ color: 'var(--texto-3)', fontSize: '0.88rem' }}>{etiqueta(clave)}</span>
      <span className="num" style={{ fontSize: '0.95rem', fontWeight: 600,
                                     color: color || 'var(--texto)' }}>
        {valor}
      </span>
    </div>
  )
}

/**
 * El detalle de una vista llega tal como lo escribe el motor: `sin_verificar`,
 * `no se sostiene`, `evaluando`. Son claves, no prosa, y pintarlas crudas deja
 * la pantalla llena de guiones bajos y minúsculas.
 *
 * `rotulo()` sin mapa capitaliza y quita los guiones. Sobre un texto que ya
 * viene bien escrito —el nombre de un punto, por ejemplo— no hace nada.
 */
function formatear(v) {
  if (v === true) return 'Sí'
  if (v === false) return 'No'
  if (v === null || v === undefined) return '—'
  if (typeof v === 'number') return Number.isInteger(v) ? v : v.toFixed(2)
  // Una celda que lleva dentro una lista se enumera; un objeto anidado dentro
  // de una tabla no cabe, y ahí sí el guion es la respuesta correcta.
  if (Array.isArray(v)) return v.length ? v.join(' · ') : '—'
  if (typeof v === 'object') return '—'
  return rotulo(String(v))
}

/** Un número solo no dice nada. Lo que apremia se ve sin leerlo. */
function resalta(clave, valor) {
  const k = String(clave).toLowerCase()
  if (typeof valor === 'number') {
    if (k.includes('oxigeno') || k.includes('dias')) {
      if (valor < 1) return 'var(--mal)'
      if (valor < 2.5) return 'var(--medio)'
      return 'var(--bien)'
    }
    if (k.includes('muertes') && valor > 0) return 'var(--mal)'
    if (k.includes('fatiga') && valor > 0.6) return 'var(--medio)'
    if (k.includes('duplas') && valor === 0) return 'var(--mal)'
  }
  if (valor === true && (k.includes('marcado') || k.includes('sin'))) return 'var(--mal)'
  if (typeof valor === 'string') {
    if (valor.includes('SIN NOMBRE')) return 'var(--mal)'
    if (valor === 'no se sostiene') return 'var(--mal)'
    if (valor === 'se sostiene') return 'var(--bien)'
    if (valor === 'sumados' || valor === 'evaluando') return 'var(--medio)'
  }
  return undefined
}
