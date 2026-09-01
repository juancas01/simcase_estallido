// ---------------------------------------------------------------------------
// LA PESTAÑA DE UN ROL — su cartera, en una pantalla y sin desplazamiento.
//
// Lo que antes era la vista privada y luego una sección del tablero es ahora
// UNA PESTAÑA más del tablero, al mismo nivel que la vista general. La sala
// alterna entre la sala entera y la cartera de cualquiera sin moverse de la
// pantalla ni perder el reloj.
//
// TRES COSAS Y NADA MÁS
// ---------------------
//   1 · la ALERTA        lo más urgente de esta cartera, en una línea
//   2 · el DETALLE       su cartera en alta resolución, en rejilla compacta
//   3 · el SEMÁFORO      qué se puede pedir HOY — un punto de color por acción
//
// LA GUÍA DE ACCIONES YA NO ESTÁ EN PANTALLA, y no es una pérdida: la guía —
// qué hace cada acción, qué hace falta antes, cómo se dice— va impresa en la
// mesa, que es donde se lee con calma. Lo que el papel no puede hacer es estar
// AL DÍA, y eso es exactamente lo que queda aquí: el semáforo del repertorio,
// un punto de color por acción, con su reparo al alcance del puntero. Papel
// para entenderla, pantalla para saber si hoy sale.
//
// EL SEMÁFORO NO DICE QUÉ HACER. Dice un hecho —«esta aún no sale»— y quién
// puede habilitarla; la conversación sobre eso vuelve a la mesa, que es donde
// el ejercicio la quiere.
// ---------------------------------------------------------------------------

import Ayuda from './Ayuda'
import { Cargando, ROLES, useDatos } from '../comun.jsx'
import { D } from '../definiciones.jsx'
import { CHIP_DISPONIBILIDAD, rotulo } from '../etiquetas.jsx'

/** Bloqueadas al final: lo que hoy no se puede pedir no compite por el ojo. */
const ORDEN_DISPONIBILIDAD = {
  disponible: 0, condicionada: 1, hecha: 2, bloqueada: 3,
}

export default function VistaRol({ rol }) {
  const ruta = `/vista/${encodeURIComponent(rol)}`
  const { datos, error } = useDatos(ruta)
  const ficha = ROLES.find(r => r.id === rol)

  if (!datos) return <Cargando error={error} ruta={ruta} />

  const acciones = [...(datos.acciones || [])].sort((a, b) =>
    (ORDEN_DISPONIBILIDAD[a.disponibilidad?.estado ?? 'disponible'] ?? 0)
    - (ORDEN_DISPONIBILIDAD[b.disponibilidad?.estado ?? 'disponible'] ?? 0))

  return (
    <div className="rol-vista">
      {/* --- 1 · la alerta, con la pregunta del día si la hay -------------- */}
      {datos.notificacion && (
        <div className="notificacion rol-notificacion">
          <p className="notificacion-pregunta">{datos.notificacion.pregunta}</p>
          <ul className="notificacion-mesas">
            {datos.notificacion.mesas.map(m => (
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
      )}

      <div className="rol-alerta">
        <span className="eyebrow">
          Lo más urgente de {ficha?.nombre || rol}
          <Ayuda etiqueta="Cómo se calcula esta alerta">{D.alerta_privada}</Ayuda>
        </span>
        <p>{datos.alerta}</p>
      </div>

      {/* --- 2 · el detalle, en rejilla y con su propio desplazamiento ----- */}
      <div className="rol-detalle">
        <Detalle datos={datos.detalle} />
      </div>

      {/* --- 3 · el semáforo del repertorio -------------------------------- */}
      {acciones.length > 0 && (
        <div className="rol-repertorio">
          <span className="eyebrow">
            Hoy
            <Ayuda etiqueta="Qué dice este semáforo">{D.repertorio}</Ayuda>
          </span>
          <div className="rol-acciones">
            {acciones.map(a => {
              const disp = a.disponibilidad || { estado: 'disponible' }
              const nota = [disp.requisito,
                disp.habilitada_por?.length
                  ? `Lo habilita: ${disp.habilitada_por.join(' · ')}` : null,
              ].filter(Boolean).join(' — ')
              return (
                <span
                  key={a.accion}
                  className={`rol-acc rol-acc-${disp.estado}`}
                  title={nota || rotulo(String(disp.estado))}
                >
                  <span className="rol-acc-punto" aria-hidden="true" />
                  {a.nombre || a.descripcion}
                </span>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

/** Renderiza el detalle sea cual sea su forma, sin que la interfaz duplique el
    esquema del motor. Un dato en dos sitios se desincroniza. Siempre. */
function Detalle({ datos }) {
  const campos = Object.entries(datos || {})
  if (!campos.length) {
    return <p style={{ margin: 0, color: 'var(--texto-3)' }}>
      Esta cartera todavía no tiene nada que reportar en esta jornada.
    </p>
  }
  return (
    <>
      {campos
        .filter(([k]) => !k.startsWith('_'))
        .map(([clave, valor]) => (
          <Campo key={clave} clave={clave} valor={valor} />
        ))}
      {campos.filter(([k]) => k.startsWith('_')).map(([k, v]) => (
        <p key={k} className="rol-nota">{String(v)}</p>
      ))}
    </>
  )
}

const etiqueta = (k) => k.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase())

function Campo({ clave, valor }) {
  if (Array.isArray(valor)) {
    if (!valor.length) return <Simple clave={clave} valor="ninguno" />
    // Una lista con huecos no puede tumbar la pestaña: `Object.keys` de `null`
    // lanza, y lo que se llevaría por delante es la pantalla entera.
    const filas = valor.filter(x => x !== null && x !== undefined)
    if (!filas.length) return <Simple clave={clave} valor="ninguno" />

    if (typeof filas[0] === 'object') {
      const columnas = [...new Set(filas.flatMap(f => Object.keys(f)))]
      return (
        <div className="rol-bloque rol-bloque-tabla">
          <div className="eyebrow">{etiqueta(clave)}</div>
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
      <div className="rol-bloque">
        <div className="eyebrow">{etiqueta(clave)}</div>
        <div className="rol-claves">
          {Object.entries(valor).map(([k, v]) => (
            <span key={k}>
              <span className="rol-clave">{etiqueta(k)}</span>
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
    <div className="rol-bloque rol-bloque-simple">
      <div className="eyebrow">{etiqueta(clave)}</div>
      <div className="num" style={{ color: color || 'var(--texto)' }}>{valor}</div>
    </div>
  )
}

/**
 * El detalle llega tal como lo escribe el motor: `sin_verificar`, `no se
 * sostiene`, `evaluando`. Son claves, no prosa. `rotulo()` sin mapa capitaliza
 * y quita los guiones; sobre un texto que ya viene bien escrito no hace nada.
 */
function formatear(v) {
  if (v === true) return 'Sí'
  if (v === false) return 'No'
  if (v === null || v === undefined) return '—'
  if (typeof v === 'number') return Number.isInteger(v) ? v : v.toFixed(2)
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
    if (k.includes('equipos') && valor === 0) return 'var(--mal)'
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
