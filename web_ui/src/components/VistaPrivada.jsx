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
//   1 · cabe en una pantalla y NO tiene desplazamiento — dos bloques
//   2 · se congela durante la deliberación
//   3 · nadie ordena desde aquí: es de solo lectura
//   4 · la ficha de rol y la agenda reservada van en papel
//   5 · no repite lo que ya está en el tablero
//
// Prueba para la primera corrida: si en el minuto 4 de la deliberación alguien
// está mirando su pantalla, una de estas cinco se rompió.
// ---------------------------------------------------------------------------

import Ayuda, { Titulo } from './Ayuda'
import { D } from '../definiciones.jsx'
import { Cargando, ROLES, useDatos } from '../comun.jsx'

export default function VistaPrivada({ rol }) {
  const { datos, error } = useDatos(`/vista/${encodeURIComponent(rol)}`, 5000)
  if (!datos) return <Cargando error={error} />

  const ficha = ROLES.find(r => r.id === rol)

  return (
    <div className="pantalla">
      <header className="cabecera">
        <div>
          <span className="eyebrow">{ficha?.frente} · vista personal</span>
          <h1>{ficha?.nombre || rol}</h1>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div className="num" style={{ fontSize: '1rem', fontWeight: 600 }}>
            Turno {datos.turno} · {datos.franja}
          </div>
          {datos.congelado && (
            <div className="congelado">
              congelado
              <Ayuda etiqueta="Qué significa congelado">{D.congelado}</Ayuda>
            </div>
          )}
        </div>
      </header>

      <div className="cuerpo" style={{ maxWidth: 900, width: '100%', margin: '0 auto' }}>
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
          <Titulo ayuda={D.detalle_privado}>Su detalle</Titulo>
          <Detalle datos={datos.detalle} />
        </div>

        {/* Las acciones son un recordatorio de repertorio, NO un panel de
            control: nadie ordena desde su pantalla. */}
        {datos.acciones?.length > 0 && (
          <div className="tarjeta" style={{ marginTop: '1rem' }}>
            <Titulo ayuda={D.repertorio}>Su repertorio</Titulo>
            <table>
              <thead>
                <tr>
                  <th>
                    Clase
                    <Ayuda etiqueta="Qué significa cada clase">{D.clases_accion}</Ayuda>
                  </th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                {datos.acciones.map(a => (
                  <tr key={a.accion}>
                    <td style={{ width: '1%' }}>
                      <span className={`chip chip-${
                        a.clase === 'constitutiva' ? 'neutro'
                        : a.clase === 'operativa' ? 'bien' : 'medio'}`}>
                        {a.clase === 'constitutiva' ? 'constituye'
                          : a.clase === 'operativa' ? 'toca el mundo' : 'informa'}
                      </span>
                    </td>
                    <td style={{ color: 'var(--texto)' }}>{a.descripcion}</td>
                  </tr>
                ))}
              </tbody>
            </table>
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

/** Renderiza el detalle sea cual sea su forma, sin que la interfaz duplique el
    esquema del motor. Un dato en dos sitios se desincroniza. Siempre. */
function Detalle({ datos }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
      {Object.entries(datos)
        .filter(([k]) => !k.startsWith('_'))
        .map(([clave, valor]) => (
          <Campo key={clave} clave={clave} valor={valor} />
        ))}
      {Object.entries(datos).filter(([k]) => k.startsWith('_')).map(([k, v]) => (
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
    if (typeof valor[0] === 'object') {
      const columnas = Object.keys(valor[0])
      return (
        <div>
          <div className="eyebrow" style={{ marginBottom: '0.35rem' }}>{etiqueta(clave)}</div>
          <div style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>{columnas.map(c => <th key={c}>{etiqueta(c)}</th>)}</tr>
              </thead>
              <tbody>
                {valor.map((fila, i) => (
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
    return <Simple clave={clave} valor={valor.join(' · ')} />
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

function formatear(v) {
  if (v === true) return 'sí'
  if (v === false) return 'no'
  if (v === null || v === undefined) return '—'
  if (typeof v === 'number') return Number.isInteger(v) ? v : v.toFixed(2)
  return String(v)
}

/** Un número solo no dice nada. Lo que apremia se ve sin leerlo. */
function resalta(clave, valor) {
  const k = clave.toLowerCase()
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
