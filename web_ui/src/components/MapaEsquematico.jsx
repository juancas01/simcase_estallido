// ---------------------------------------------------------------------------
// EL MAPA — un esquema de líneas, no un mapa geográfico.
//
// La forma correcta es un plano de metro antes que un mapa de carreteras, y la
// razón no es estética: **el modelo del mundo tiene exactamente esa forma.** Un
// corredor ES una secuencia ordenada de puntos entre un origen y un destino,
// igual que una línea de metro es una secuencia ordenada de estaciones.
//
//     La topología es la información; la geometría es decoración.
//
// TRES COSAS QUE HACE Y UNA TABLA NO
//   · enseña sin palabras que un corredor vale lo que su peor punto
//   · hace visibles los huecos — un «?» proyectado es una petición de decisión
//   · da algo que señalar: la discusión pasa de «el corredor al puerto» a «P3»
//
// TRES GUARDARRAÍLES
//   1 · No hay distancias, ni escala, ni tiempos de desplazamiento. El esquema
//       debe PARECER esquemático para que nadie lea distancia en él.
//   2 · No muestra lo que el tablero no muestra: ni la mezcla real de un punto,
//       ni si una denuncia es cierta.
//   3 · Se congela durante la deliberación, igual que todo lo demás.
// ---------------------------------------------------------------------------

const COLOR_CORREDOR = {
  'C-PUE': '#7aa5e8',
  'C-SUR': '#4fb286',
  'C-HOS': '#c98ae0',
  'C-REF': '#d9a441',
  'C-NOR': '#6fc4d4',
}

const COLOR_ESTADO = {
  abierto: '#4fb286',
  parcial: '#d9a441',
  cerrado: '#d9636f',
  sin_verificar: '#6d7a91',
}

// El modo por el que se abrió decide la FORMA del nodo. Lo abierto por fuerza se
// dibuja distinto de lo pactado, porque no vale lo mismo: uno vuelve a cerrarse
// esta noche y el otro se sostiene.
const FORMA = {
  fuerza: 'fuerza',
  concertacion: 'pactado',
  desgaste: 'desgaste',
  cerrado: 'cerrado',
}

const VB = { w: 100, h: 104, pad: 6 }

export default function MapaEsquematico({ tablero, seleccionado, onSeleccionar }) {
  if (!tablero?.puntos?.length) return null

  const puntos = tablero.puntos
  const porId = Object.fromEntries(puntos.map(p => [p.nodo_id, p]))
  const corredores = tablero.corredores || []
  const regiones = Object.fromEntries((tablero.regiones || []).map(r => [r.region_id, r]))

  return (
    <div className="tarjeta" style={{ padding: '0.9rem 1rem 0.6rem' }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'baseline', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem',
      }}>
        <h2 style={{ margin: 0 }}>Mapa de corredores</h2>
        <span className="eyebrow">esquema · sin escala ni distancias</span>
      </div>

      <svg
        viewBox={`${-VB.pad} ${-VB.pad} ${VB.w + VB.pad * 2} ${VB.h + VB.pad * 2}`}
        style={{ width: '100%', height: 'auto', display: 'block' }}
        role="img"
        aria-label="Esquema de los cinco corredores y sus puntos de cierre"
      >
        {/* Las líneas: cada corredor une sus puntos EN ORDEN. Que la línea se vea
            entera y sin embargo el corredor esté cerrado es exactamente lo que
            hay que enseñar: vale lo que su peor punto. */}
        {corredores.map(c => {
          const nodos = (c.nodos || []).map(id => porId[id]).filter(Boolean)
          if (nodos.length < 2) return null
          const d = nodos.map((n, i) => `${i === 0 ? 'M' : 'L'} ${n.x} ${n.y}`).join(' ')
          const pasa = c.caudal > 0.05
          return (
            <path
              key={c.corredor_id}
              d={d}
              fill="none"
              stroke={COLOR_CORREDOR[c.corredor_id] || '#5b6478'}
              strokeWidth={pasa ? 1.6 : 1.1}
              strokeOpacity={pasa ? 0.95 : 0.32}
              strokeDasharray={pasa ? undefined : '2.5 2'}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          )
        })}

        {/* Los puntos */}
        {puntos.map(p => {
          const color = COLOR_ESTADO[p.estado] || COLOR_ESTADO.cerrado
          const forma = FORMA[p.modo_apertura] || 'cerrado'
          const sel = seleccionado === p.nodo_id
          const sinMirar = p.estado === 'sin_verificar'

          return (
            <g
              key={p.nodo_id}
              onClick={() => onSeleccionar?.(sel ? null : p.nodo_id)}
              style={{ cursor: onSeleccionar ? 'pointer' : 'default' }}
            >
              <title>
                {`${p.nombre} · ${regiones[p.region_id]?.nombre || p.region_id}`}
                {p.modo_apertura !== 'cerrado' ? ` · abierto por ${p.modo_apertura}` : ''}
                {sinMirar ? ' · SIN VERIFICAR' : ''}
              </title>

              {sel && <circle cx={p.x} cy={p.y} r={3.4} fill="none"
                              stroke="#e8ecf4" strokeWidth={0.5} />}

              {forma === 'pactado' ? (
                // Cuadrado: lo pactado se sostiene mientras el acuerdo se cumpla
                <rect x={p.x - 1.7} y={p.y - 1.7} width={3.4} height={3.4}
                      rx={0.5} fill={color} stroke="#0b0e14" strokeWidth={0.35} />
              ) : forma === 'fuerza' ? (
                // Rombo: lo abierto por la fuerza reabre esta noche
                <rect x={p.x - 1.7} y={p.y - 1.7} width={3.4} height={3.4}
                      transform={`rotate(45 ${p.x} ${p.y})`}
                      fill={color} stroke="#0b0e14" strokeWidth={0.35} />
              ) : (
                <circle cx={p.x} cy={p.y} r={1.9}
                        fill={sinMirar ? '#0b0e14' : color}
                        stroke={color} strokeWidth={sinMirar ? 0.7 : 0.35} />
              )}

              {/* Un signo de interrogación proyectado en la pared es una petición
                  de decisión: hay alguien en la mesa que puede resolverlo
                  gastando una dupla, y todos lo están viendo. */}
              {sinMirar && (
                <text x={p.x} y={p.y + 0.85} textAnchor="middle"
                      fontSize="2.2" fill="#aab4c6" fontWeight="700"
                      style={{ pointerEvents: 'none' }}>?</text>
              )}

              <text
                x={p.x} y={p.y - 3}
                textAnchor="middle"
                fontSize="1.85"
                fill={sel ? '#e8ecf4' : '#8e9aae'}
                style={{ pointerEvents: 'none' }}
              >
                {p.nodo_id}
              </text>
            </g>
          )
        })}
      </svg>

      <Leyenda corredores={corredores} />
    </div>
  )
}

function Leyenda({ corredores }) {
  return (
    <div style={{
      display: 'flex', flexWrap: 'wrap', gap: '0.35rem 1rem',
      paddingTop: '0.55rem', borderTop: '1px solid var(--borde-suave)',
      fontSize: '0.72rem', color: 'var(--texto-3)',
    }}>
      {corredores.map(c => (
        <span key={c.corredor_id} style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <span style={{
            width: 12, height: 2.5, borderRadius: 2,
            background: COLOR_CORREDOR[c.corredor_id],
            opacity: c.caudal > 0.05 ? 1 : 0.35,
          }} />
          {c.nombre}
        </span>
      ))}
      <span style={{ marginLeft: 'auto', display: 'flex', gap: '0.75rem' }}>
        <span>● cerrado</span>
        <span>◆ por fuerza</span>
        <span>■ pactado</span>
        <span>? sin verificar</span>
      </span>
    </div>
  )
}
