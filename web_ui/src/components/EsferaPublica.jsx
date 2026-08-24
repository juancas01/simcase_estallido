import { useEffect, useState } from 'react'

/**
 * ESFERA PÚBLICA — la segunda proyección, a toda la sala.
 *
 * El tablero muestra lo que el Estado tiene por cierto; esta pantalla muestra
 * lo que SE DICE. La distancia entre ambas es el caso.
 *
 * Van en dos superficies simultáneas y nunca en pestañas: la divergencia solo
 * se percibe si se ven a la vez. La sala tiene que poder mirar la cifra oficial
 * en una pared y la cifra que circula en la otra.
 *
 * La franja de LAS TRES CIFRAS es el corazón de esta pantalla.
 */

function TresCifras({ cifras }) {
  if (!cifras) return null
  const { oficial, municipal, verificada } = cifras
  const divergen = Math.max(oficial, municipal, verificada) -
                   Math.min(oficial, municipal, verificada) > 3

  return (
    <div style={{
      padding: '1rem 1.25rem', borderRadius: '0.4rem', marginBottom: '1.5rem',
      background: divergen ? 'rgba(239,68,68,0.08)' : 'rgba(255,255,255,0.04)',
      border: `1px solid ${divergen ? 'rgba(239,68,68,0.35)' : 'rgba(255,255,255,0.1)'}`,
    }}>
      <div style={{
        fontSize: '0.68rem', letterSpacing: '0.12em', textTransform: 'uppercase',
        opacity: 0.6, marginBottom: '0.75rem',
      }}>
        Las tres cifras {divergen && '· en disputa'}
      </div>
      <div style={{ display: 'flex', gap: '2.5rem' }}>
        {[
          ['Parte operacional', oficial, 'Director de Policía'],
          ['Parte municipal', municipal, 'Alcaldía'],
          ['Verificado', verificada, 'Defensoría'],
        ].map(([label, valor, fuente]) => (
          <div key={label}>
            <div style={{ fontSize: '2rem', fontWeight: 700, fontVariantNumeric: 'tabular-nums' }}>
              {valor}
            </div>
            <div style={{ fontSize: '0.8rem' }}>{label}</div>
            <div style={{ fontSize: '0.7rem', opacity: 0.5 }}>{fuente}</div>
          </div>
        ))}
      </div>
      {divergen && (
        <div style={{ marginTop: '0.75rem', fontSize: '0.78rem', color: '#fca5a5' }}>
          Sin protocolo único de verificación, cada actor sostiene su número y el
          desmentido cuesta legitimidad cada vez.
        </div>
      )}
    </div>
  )
}

function Publicacion({ item }) {
  const colores = {
    prensa_nacional: '#60a5fa',
    prensa_internacional: '#a78bfa',
    redes: '#f472b6',
    gremios: '#fbbf24',
    comite_paro: '#4ade80',
    internacional: '#a78bfa',
    alcaldes_entorno: '#38bdf8',
  }
  const color = colores[item.fuente] || '#94a3b8'
  return (
    <div style={{
      padding: '0.75rem 0.9rem', borderRadius: '0.35rem', marginBottom: '0.6rem',
      background: 'rgba(255,255,255,0.03)', borderLeft: `3px solid ${color}`,
    }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
        marginBottom: '0.3rem',
      }}>
        <span style={{
          fontSize: '0.68rem', letterSpacing: '0.08em', textTransform: 'uppercase',
          color,
        }}>
          {item.fuente.replace(/_/g, ' ')}
        </span>
        <span style={{ fontSize: '0.68rem', opacity: 0.45 }}>T{item.turno}</span>
      </div>
      <div style={{ fontSize: '0.92rem', lineHeight: 1.45 }}>{item.texto}</div>
      {item.sin_verificar && (
        <div style={{
          marginTop: '0.4rem', fontSize: '0.7rem', color: '#fbbf24',
          textTransform: 'uppercase', letterSpacing: '0.06em',
        }}>
          ⚠ sin verificar
        </div>
      )}
    </div>
  )
}

export default function EsferaPublica() {
  const [datos, setDatos] = useState(null)

  useEffect(() => {
    let vivo = true
    const cargar = async () => {
      try {
        const r = await fetch('/api/esfera')
        const d = await r.json()
        if (vivo) setDatos(d)
      } catch { /* no puede romper la sala */ }
    }
    cargar()
    const id = setInterval(cargar, 2000)
    return () => { vivo = false; clearInterval(id) }
  }, [])

  if (!datos) {
    return (
      <div style={estilos.pantalla}>
        <p style={{ opacity: 0.5 }}>Esperando al motor…</p>
      </div>
    )
  }

  return (
    <div style={estilos.pantalla}>
      <header style={{ marginBottom: '1.25rem' }}>
        <h1 style={{ fontSize: '1.4rem', fontWeight: 600, margin: 0 }}>Esfera pública</h1>
        <div style={{ fontSize: '0.8rem', opacity: 0.55 }}>
          Lo que se dice · encuadre dominante: <strong>{datos.encuadre_dominante}</strong>
          {' · '}exposición internacional: <strong>{datos.exposicion_internacional}</strong>
        </div>
      </header>

      <TresCifras cifras={datos.cifras} />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        <div>
          <h2 style={estilos.h2}>Prensa e internacional</h2>
          {(datos.publicaciones || [])
            .filter(p => p.fuente.startsWith('prensa') || p.fuente === 'internacional')
            .map((p, i) => <Publicacion key={i} item={p} />)}
        </div>
        <div>
          <h2 style={estilos.h2}>Redes, gremios y contraparte</h2>
          {(datos.publicaciones || [])
            .filter(p => !p.fuente.startsWith('prensa') && p.fuente !== 'internacional')
            .map((p, i) => <Publicacion key={i} item={p} />)}
        </div>
      </div>

      {datos.denuncias?.length > 0 && (
        <div style={{ marginTop: '1.75rem' }}>
          <h2 style={estilos.h2}>Denuncias sin verificar</h2>
          <div style={{
            padding: '0.9rem 1rem', borderRadius: '0.35rem',
            background: 'rgba(251,191,36,0.07)', border: '1px solid rgba(251,191,36,0.25)',
          }}>
            {datos.denuncias.map(d => (
              <div key={d.denuncia_id} style={{ marginBottom: '0.6rem', fontSize: '0.9rem' }}>
                <strong style={{ opacity: 0.6, fontSize: '0.75rem' }}>{d.denuncia_id}</strong>
                {' — '}{d.texto}
                <span style={{ opacity: 0.5, fontSize: '0.75rem' }}> [{d.estado}]</span>
              </div>
            ))}
            <div style={{ fontSize: '0.75rem', opacity: 0.6, marginTop: '0.5rem' }}>
              Verificar una consume la dupla que no verificará la otra.
            </div>
          </div>
        </div>
      )}
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
}
