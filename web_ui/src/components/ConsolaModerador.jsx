import { useEffect, useState } from 'react'

/**
 * CONSOLA DEL MODERADOR — el único teclado. NO se proyecta.
 *
 * Hace cuatro cosas (§10.2):
 *   1. Transcribe lo que la mesa acordó, en lenguaje natural.
 *   2. LEE DE VUELTA EL PLAN INTERPRETADO, con su banda de riesgo, antes de
 *      ejecutar. Este momento es una pieza de diseño, no un trámite: la sala
 *      oye su propia decisión reformulada con su riesgo, y con frecuencia la
 *      cambia. Es el mejor punto de intervención pedagógica del montaje.
 *   3. Entrega información privada en papel.
 *   4. Inyecta eventos y, si hace falta, corrige un resultado estocástico.
 */

function Cronometro({ segundos, etiqueta, onFin }) {
  const [restante, setRestante] = useState(segundos)
  useEffect(() => { setRestante(segundos) }, [segundos])
  useEffect(() => {
    if (restante <= 0) { onFin?.(); return }
    const id = setTimeout(() => setRestante(r => r - 1), 1000)
    return () => clearTimeout(id)
  }, [restante, onFin])

  const m = Math.floor(Math.max(0, restante) / 60)
  const s = Math.max(0, restante) % 60
  const critico = restante <= 30
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{
        fontSize: '0.65rem', letterSpacing: '0.12em', textTransform: 'uppercase',
        opacity: 0.6,
      }}>
        {etiqueta}
      </div>
      <div style={{
        fontSize: '2.6rem', fontWeight: 700, fontVariantNumeric: 'tabular-nums',
        lineHeight: 1.1, color: critico ? '#ef4444' : 'inherit',
      }}>
        {m}:{String(s).padStart(2, '0')}
      </div>
    </div>
  )
}

/** La banda de riesgo se muestra ANTES de decidir, no después. */
function BandaRiesgo({ banda, p, ausentes }) {
  const colores = { baja: '#4ade80', media: '#fbbf24', alta: '#fb923c', critica: '#ef4444' }
  return (
    <div style={{
      padding: '0.6rem 0.8rem', borderRadius: '0.3rem', marginTop: '0.4rem',
      background: `${colores[banda]}18`, border: `1px solid ${colores[banda]}55`,
    }}>
      <span style={{
        color: colores[banda], fontWeight: 700, textTransform: 'uppercase',
        letterSpacing: '0.06em', fontSize: '0.8rem',
      }}>
        Riesgo {banda}
      </span>
      <span style={{ opacity: 0.75, fontSize: '0.85rem' }}> · P = {Math.round(p * 100)} %</span>
      {ausentes?.length > 0 && (
        <div style={{ fontSize: '0.75rem', opacity: 0.65, marginTop: '0.3rem' }}>
          Mitigadores ausentes: {ausentes.join(', ')}
        </div>
      )}
    </div>
  )
}

export default function ConsolaModerador() {
  const [texto, setTexto] = useState('')
  const [plan, setPlan] = useState(null)
  const [estado, setEstado] = useState(null)
  const [fase, setFase] = useState('deliberacion')

  useEffect(() => {
    fetch('/api/estado').then(r => r.json()).then(setEstado).catch(() => {})
  }, [fase])

  const interpretar = async () => {
    const r = await fetch('/api/plan/interpretar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ texto }),
    })
    setPlan(await r.json())
    setFase('confirmacion')
  }

  const confirmar = async () => {
    await fetch('/api/plan/ejecutar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan_id: plan?.plan_id }),
    })
    setPlan(null); setTexto(''); setFase('resolucion')
  }

  return (
    <div style={estilos.pantalla}>
      <header style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        marginBottom: '1.5rem', paddingBottom: '1rem',
        borderBottom: '1px solid rgba(255,255,255,0.12)',
      }}>
        <div>
          <h1 style={{ fontSize: '1.2rem', fontWeight: 600, margin: 0 }}>
            Consola del moderador
          </h1>
          <div style={{ fontSize: '0.78rem', opacity: 0.55 }}>
            Turno {estado?.turno ?? '—'} · {estado?.franja ?? '—'} · no proyectar esta pantalla
          </div>
        </div>
        <Cronometro
          segundos={fase === 'deliberacion' ? 360 : 150}
          etiqueta={fase === 'deliberacion' ? 'Deliberación' : 'Órdenes'}
        />
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1.4fr 1fr', gap: '1.5rem' }}>
        <div>
          <h2 style={estilos.h2}>1 · Transcribir lo que la mesa acordó</h2>
          <textarea
            value={texto}
            onChange={e => setTexto(e.target.value)}
            placeholder="Ej: Concentrar ESMAD en el anillo hospitalario, con dupla de la Defensoría, responsable el Ministro de Defensa."
            style={{
              width: '100%', minHeight: '7rem', padding: '0.75rem',
              borderRadius: '0.35rem', background: 'rgba(255,255,255,0.05)',
              color: 'inherit', border: '1px solid rgba(255,255,255,0.15)',
              fontFamily: 'inherit', fontSize: '0.95rem', resize: 'vertical',
            }}
          />
          <button onClick={interpretar} disabled={!texto.trim()} style={estilos.boton}>
            Interpretar plan
          </button>

          {plan && (
            <div style={{ marginTop: '1.25rem' }}>
              <h2 style={estilos.h2}>2 · Leer de vuelta a la sala, en voz alta</h2>
              <div style={{
                padding: '1rem', borderRadius: '0.4rem',
                background: 'rgba(96,165,250,0.08)',
                border: '1px solid rgba(96,165,250,0.3)',
              }}>
                {(plan.acciones || []).map((a, i) => (
                  <div key={i} style={{ marginBottom: '0.9rem' }}>
                    <div style={{ fontSize: '0.95rem' }}>
                      <strong>{a.rol}</strong> · {a.descripcion}
                    </div>
                    {a.requisitos_faltantes?.length > 0 && (
                      <div style={{ fontSize: '0.8rem', color: '#fbbf24', marginTop: '0.25rem' }}>
                        Falta: {a.requisitos_faltantes.join(', ')}
                        {a.habilitada_por?.length > 0 && ` — corresponde a ${a.habilitada_por.join(', ')}`}
                      </div>
                    )}
                    {a.riesgo && (
                      <BandaRiesgo banda={a.riesgo.banda} p={a.riesgo.p_incidente}
                                   ausentes={a.riesgo.mitigadores_ausentes} />
                    )}
                  </div>
                ))}
                <div style={{ display: 'flex', gap: '0.6rem', marginTop: '0.5rem' }}>
                  <button onClick={confirmar} style={estilos.boton}>La sala confirma</button>
                  <button onClick={() => { setPlan(null); setFase('deliberacion') }}
                          style={{ ...estilos.boton, background: 'rgba(255,255,255,0.08)' }}>
                    Corregir
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        <div>
          <h2 style={estilos.h2}>3 · Entregas en papel de este turno</h2>
          <div style={{
            padding: '0.9rem', borderRadius: '0.35rem', fontSize: '0.85rem',
            background: 'rgba(255,255,255,0.04)', lineHeight: 1.7,
          }}>
            La asimetría de información se resuelve en mano, no en pantalla. Una
            nota entregada a un solo participante en mitad de la deliberación
            produce más tensión que cualquier notificación: los otros siete ven
            que alguien recibió algo y no saben qué.
            <ul style={{ paddingLeft: '1.1rem', marginTop: '0.6rem' }}>
              <li>Parte operacional → solo Policía</li>
              <li>Inteligencia sobre financiación → solo Defensa</li>
              <li>Verificaciones de duplas → solo Defensoría</li>
              <li>Calendario de agotamiento → solo Minas</li>
            </ul>
          </div>

          <h2 style={{ ...estilos.h2, marginTop: '1.25rem' }}>4 · Pliego de decisiones</h2>
          <div style={{
            padding: '0.9rem', borderRadius: '0.35rem', fontSize: '0.85rem',
            background: 'rgba(255,255,255,0.04)',
          }}>
            {(estado?.registro || []).length === 0 ? (
              <span style={{ opacity: 0.5 }}>
                Ningún renglón escrito todavía. El renglón vacío es más elocuente
                que cualquier advertencia.
              </span>
            ) : (
              (estado.registro || []).map((d, i) => (
                <div key={i} style={{ marginBottom: '0.4rem' }}>
                  T{d.turno} · {d.rol} · {d.descripcion}
                  <span style={{ color: d.responsable_nominado ? '#4ade80' : '#ef4444' }}>
                    {' '}{d.responsable_nominado || '(sin responsable nominado)'}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const estilos = {
  pantalla: {
    minHeight: '100vh', padding: '1.5rem 2rem',
    background: 'var(--bg-main, #0d1117)', color: 'var(--text-main, #e6e9ee)',
    fontFamily: 'system-ui, sans-serif',
  },
  h2: {
    fontSize: '0.72rem', letterSpacing: '0.12em', textTransform: 'uppercase',
    opacity: 0.6, fontWeight: 600, marginBottom: '0.6rem',
  },
  boton: {
    marginTop: '0.7rem', padding: '0.55rem 1.1rem', borderRadius: '0.3rem',
    background: '#2563eb', color: 'white', border: 'none', cursor: 'pointer',
    fontSize: '0.9rem', fontFamily: 'inherit',
  },
}
