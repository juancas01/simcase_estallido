import { useEffect, useState } from 'react'

/**
 * TABLERO DE SITUACIÓN — proyectado a toda la sala.
 *
 * REGLA DURA (§10.1): esta pantalla es una vista de la CAPA 2, nunca de la
 * capa 1. Muestra lo que el Estado tiene por cierto según la fuente que la mesa
 * haya adoptado como oficial — y si no ha adoptado ninguna, muestra la del parte
 * operacional, con su sesgo, sin avisar.
 *
 * Si aquí se pintara el caudal verdadero de cada nodo y su composición real, el
 * motor de información se anularía entero: las cuatro fuentes con sesgo
 * sobrarían, el error doble desaparecería y la Defensoría se quedaría sin
 * oficio. El backend nunca serializa `composicion_real`.
 *
 * El signo de interrogación de un nodo sin verificar es el dato más valioso de
 * la pantalla: proyectado sobre la pared es una petición de decisión.
 */

const GRADO_COLOR = {
  confirmado: '#4ade80',
  estimado: '#fbbf24',
  sin_verificar: '#94a3b8',
}

function Reserva({ nombre, valor, invertida = false, umbral }) {
  const critico = invertida ? valor > umbral : valor < umbral
  return (
    <div style={{
      flex: 1, padding: '0.9rem 1rem', borderRadius: '0.4rem',
      background: 'rgba(255,255,255,0.04)',
      border: `1px solid ${critico ? '#ef4444' : 'rgba(255,255,255,0.1)'}`,
    }}>
      <div style={{
        fontSize: '0.65rem', letterSpacing: '0.1em', textTransform: 'uppercase',
        opacity: 0.6, marginBottom: '0.35rem',
      }}>
        {nombre}{invertida && ' ↓'}
      </div>
      <div style={{
        fontSize: '2rem', fontWeight: 700, lineHeight: 1,
        fontVariantNumeric: 'tabular-nums',
        color: critico ? '#ef4444' : 'inherit',
      }}>
        {Math.round(valor)}
      </div>
      <div style={{
        height: 4, marginTop: '0.5rem', borderRadius: 2,
        background: 'rgba(255,255,255,0.1)', overflow: 'hidden',
      }}>
        <div style={{
          width: `${valor}%`, height: '100%',
          background: critico ? '#ef4444' : '#60a5fa',
        }} />
      </div>
    </div>
  )
}

function RelojAutonomia({ regiones }) {
  const orden = [...regiones].sort((a, b) => a.dias_oxigeno - b.dias_oxigeno)
  return (
    <div>
      <h2 style={estilos.h2}>Reloj de autonomía</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
        <thead>
          <tr style={{ opacity: 0.55, fontSize: '0.68rem', textTransform: 'uppercase' }}>
            <th style={estilos.th}>Región</th>
            <th style={estilos.thNum}>Oxígeno</th>
            <th style={estilos.thNum}>Combustible</th>
            <th style={estilos.thNum}>Alimentos</th>
            <th style={estilos.thNum}>Muertes ev.</th>
          </tr>
        </thead>
        <tbody>
          {orden.map(r => (
            <tr key={r.region_id} style={{ borderTop: '1px solid rgba(255,255,255,0.07)' }}>
              <td style={estilos.td}>{r.nombre}</td>
              <td style={{
                ...estilos.tdNum,
                color: r.dias_oxigeno < 1 ? '#ef4444' : r.dias_oxigeno < 2 ? '#fbbf24' : 'inherit',
                fontWeight: r.dias_oxigeno < 1 ? 700 : 400,
              }}>
                {r.dias_oxigeno.toFixed(1)} d
              </td>
              <td style={estilos.tdNum}>{r.dias_combustible.toFixed(1)} d</td>
              <td style={estilos.tdNum}>{r.dias_alimentos.toFixed(1)} d</td>
              <td style={{ ...estilos.tdNum, color: r.muertes_evitables > 0 ? '#ef4444' : 'inherit' }}>
                {r.muertes_evitables || '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Corredores({ corredores }) {
  return (
    <div>
      <h2 style={estilos.h2}>Corredores</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {corredores.map(c => (
          <div key={c.corredor_id} style={{
            display: 'flex', alignItems: 'center', gap: '0.75rem',
            padding: '0.5rem 0.75rem', borderRadius: '0.3rem',
            background: 'rgba(255,255,255,0.03)',
          }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.9rem' }}>{c.nombre}</div>
              <div style={{ fontSize: '0.7rem', opacity: 0.5 }}>
                {(c.poblacion / 1e6).toFixed(1)} M aguas abajo · {c.clases.join(' · ')}
              </div>
            </div>
            <div style={{ width: 120 }}>
              <div style={{
                height: 8, borderRadius: 4, background: 'rgba(255,255,255,0.1)',
                overflow: 'hidden',
              }}>
                <div style={{
                  width: `${c.caudal * 100}%`, height: '100%',
                  background: c.caudal > 0.5 ? '#4ade80' : c.caudal > 0 ? '#fbbf24' : '#ef4444',
                }} />
              </div>
            </div>
            <div style={{
              width: 48, textAlign: 'right', fontVariantNumeric: 'tabular-nums',
              fontSize: '0.9rem',
            }}>
              {Math.round(c.caudal * 100)}%
            </div>
            {c.anunciado_abierto && c.caudal < 0.3 && (
              <span style={{
                fontSize: '0.65rem', color: '#ef4444', textTransform: 'uppercase',
              }}>
                anunciado abierto
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function Banderas({ banderas }) {
  const nombres = {
    reglas_escritas: 'Reglas de empleo escritas',
    identificacion_agentes: 'Identificación de agentes',
    registro_av: 'Registro audiovisual',
    registro_escrito: 'Registro escrito de decisiones',
    protocolo_voceria: 'Protocolo de vocería',
    protocolo_verificacion: 'Protocolo de verificación',
    criterio_priorizacion: 'Criterio de priorización',
    lineas_rojas_fijadas: 'Líneas rojas fijadas',
  }
  const activas = Object.entries(nombres).filter(([k]) => banderas[k])
  return (
    <div>
      <h2 style={estilos.h2}>
        Lo que la mesa ha constituido{' '}
        <span style={{ opacity: 0.5, fontWeight: 400 }}>
          {activas.length}/{Object.keys(nombres).length}
        </span>
      </h2>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
        {Object.entries(nombres).map(([k, label]) => (
          <span key={k} style={{
            fontSize: '0.72rem', padding: '0.25rem 0.6rem', borderRadius: '0.25rem',
            background: banderas[k] ? 'rgba(74,222,128,0.15)' : 'rgba(255,255,255,0.04)',
            color: banderas[k] ? '#4ade80' : 'rgba(255,255,255,0.35)',
            border: `1px solid ${banderas[k] ? 'rgba(74,222,128,0.3)' : 'transparent'}`,
            textDecoration: banderas[k] ? 'none' : 'none',
          }}>
            {banderas[k] ? '✓ ' : '· '}{label}
          </span>
        ))}
      </div>
    </div>
  )
}

export default function TableroSituacion() {
  const [estado, setEstado] = useState(null)
  const [congelado, setCongelado] = useState(false)

  useEffect(() => {
    let vivo = true
    const cargar = async () => {
      try {
        const r = await fetch('/api/estado')
        const d = await r.json()
        if (vivo) {
          setEstado(d)
          setCongelado(Boolean(d.congelado))
        }
      } catch { /* el tablero no puede romper la sala */ }
    }
    cargar()
    const id = setInterval(cargar, 2000)
    return () => { vivo = false; clearInterval(id) }
  }, [])

  if (!estado) {
    return <div style={estilos.pantalla}><p style={{ opacity: 0.5 }}>Esperando al motor…</p></div>
  }

  const { reservas, regiones, corredores, banderas, fuerza } = estado

  return (
    <div style={estilos.pantalla}>
      {/* Durante la deliberación el tablero NO se actualiza. Si la pantalla se
          mueve mientras la gente habla, la gente mira la pantalla. */}
      {congelado && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, padding: '0.4rem',
          background: '#1e40af', textAlign: 'center', fontSize: '0.75rem',
          letterSpacing: '0.1em', textTransform: 'uppercase', zIndex: 10,
        }}>
          Deliberación en curso · el tablero está congelado
        </div>
      )}

      <header style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
        marginBottom: '1.5rem', marginTop: congelado ? '1.5rem' : 0,
      }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', fontWeight: 600, margin: 0 }}>
            Tablero de situación
          </h1>
          <div style={{ fontSize: '0.8rem', opacity: 0.55 }}>
            Turno {estado.turno} · {estado.franja} ·{' '}
            encuadre dominante: <strong>{estado.encuadre_dominante}</strong>
          </div>
        </div>
        <div style={{ textAlign: 'right', fontSize: '0.8rem', opacity: 0.7 }}>
          <div>Intensidad de movilización: <strong>{estado.intensidad_nacional}</strong></div>
          <div>
            Gremios: <strong>{estado.posicion_gremios}</strong> ·{' '}
            Comité: <strong>{estado.comite_disponible ? 'en la mesa' : 'retirado'}</strong>
          </div>
        </div>
      </header>

      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.75rem' }}>
        <Reserva nombre="Legitimidad" valor={reservas.legitimidad} umbral={40} />
        <Reserva nombre="Credibilidad de la mesa" valor={reservas.credibilidad_mesa} umbral={30} />
        <Reserva nombre="Exposición internacional" valor={reservas.exposicion_internacional}
                 invertida umbral={70} />
        <Reserva nombre="Cohesión de la mesa" valor={reservas.cohesion_mesa} umbral={35} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <RelojAutonomia regiones={regiones} />
        <Corredores corredores={corredores} />
      </div>

      <div style={{ marginTop: '1.75rem' }}>
        <Banderas banderas={banderas} />
      </div>

      <div style={{ marginTop: '1.75rem', fontSize: '0.85rem', opacity: 0.7 }}>
        <h2 style={estilos.h2}>Fuerza</h2>
        ESMAD en reserva <strong>{fuerza.esmad_disponible}</strong>/{fuerza.esmad_total} ·
        fatiga media <strong>{fuerza.fatiga_media_esmad}</strong> ·
        instalaciones bajo custodia <strong>{fuerza.instalaciones_criticas}</strong> ·
        frentes rurales descubiertos <strong>{fuerza.frentes_rurales_descubiertos}</strong>
      </div>
    </div>
  )
}

const estilos = {
  pantalla: {
    minHeight: '100vh', padding: '2rem',
    background: 'var(--bg-main, #0d1117)', color: 'var(--text-main, #e6e9ee)',
    fontFamily: 'system-ui, sans-serif',
  },
  h2: {
    fontSize: '0.72rem', letterSpacing: '0.12em', textTransform: 'uppercase',
    opacity: 0.6, fontWeight: 600, marginBottom: '0.7rem',
  },
  th: { textAlign: 'left', padding: '0.3rem 0.5rem', fontWeight: 600 },
  thNum: { textAlign: 'right', padding: '0.3rem 0.5rem', fontWeight: 600 },
  td: { padding: '0.45rem 0.5rem' },
  tdNum: { padding: '0.45rem 0.5rem', textAlign: 'right', fontVariantNumeric: 'tabular-nums' },
}
