// ---------------------------------------------------------------------------
// CUATRO SUPERFICIES
//
//   /tablero        PROYECTAR · lo que el Estado tiene por cierto, grano grueso
//                   — lleva la esfera pública como barra lateral plegable
//   /esfera         PROYECTAR · lo que se dice, como pantalla aparte
//   /vista/{rol}    el dispositivo de cada uno · su cartera en alta resolución
//   /consola        donde se transcriben las órdenes · NO proyectar
//
// La distancia entre las dos proyecciones es el caso, y solo se percibe si se ven
// A LA VEZ. De ahí los dos montajes:
//
//   · con DOS proyectores, `/tablero` y `/esfera` en pantallas distintas
//   · con UNO solo o un portátil, `/tablero` con su barra lateral abierta
//
// Lo que no se hace nunca es ponerla en una pestaña: una pestaña sustituye una
// cosa por la otra y elimina justamente lo que hay que enseñar.
//
// Y NO HAY MODERADOR COMO FIGURA APARTE: quien opera la consola puede ser uno de
// los ocho. El sistema conduce el turno.
//
// ESTA PORTADA ES UN LANZADOR, no un documento. Cada tarjeta dice su nombre y su
// ruta; para qué sirve cada una está detrás de su marca de ayuda. Quien monta la
// sala ya lo sabe y quien no, lo pide.
// ---------------------------------------------------------------------------

import Tablero from './components/Tablero'
import EsferaPublica from './components/EsferaPublica'
import Consola from './components/Consola'
import VistaPrivada from './components/VistaPrivada'
import Ayuda from './components/Ayuda'
import { ROLES } from './comun.jsx'
import LogoAiLab from '../logos/LOGO Ai Lab_blanco.png'

const PROYECCIONES = [
  {
    ruta: '/tablero',
    nombre: 'Tablero de situación',
    ayuda: (
      <>
        <p>
          <strong>Lo que el Estado tiene por cierto</strong>, en grano grueso:
          reservas, mapa de corredores, semáforo de abastecimiento y pliego de
          decisiones.
        </p>
        <p>
          Lleva la esfera pública como barra lateral plegable, para montajes de
          una sola pantalla.
        </p>
      </>
    ),
  },
  {
    ruta: '/esfera',
    nombre: 'Esfera pública',
    ayuda: (
      <>
        <p>
          <strong>Lo que se dice:</strong> prensa nacional e internacional,
          redes, gremios y denuncias graves sin verificar.
        </p>
        <p>
          Esta ruta es para el montaje de dos proyectores. Con uno solo, la misma
          información va en la barra lateral del tablero.
        </p>
      </>
    ),
  },
]

const AYUDA_CONSOLA = (
  <>
    <p>
      <strong>Se transcribe lo que la mesa acordó</strong> y la pantalla devuelve
      el plan interpretado con su banda de riesgo, para leerlo en voz alta antes
      de ejecutar.
    </p>
    <p>
      No proyectar. Puede operarla cualquiera de los ocho: quien la opera
      transcribe, no conduce ni decide el ritmo.
    </p>
  </>
)

const AYUDA_VISTAS = (
  <>
    <p>
      <strong>Cada rol en su propio dispositivo.</strong> Responde cuánto, dónde
      exactamente y desde cuándo, con un grado de resolución que el tablero
      general no tiene.
    </p>
    <p>
      Personal, no confidencial: el sistema la muestra solo a su titular, y el
      ejercicio busca que su contenido se comunique a la mesa.
    </p>
  </>
)

function Portada() {
  return (
    <div className="pantalla">
      <div className="cuerpo" style={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', gap: '1.75rem', padding: '3rem 1.5rem',
      }}>
        <img src={LogoAiLab} alt="AI Lab" style={{ height: '2.6rem', opacity: 0.85 }} />
        <div style={{ textAlign: 'center', maxWidth: '40rem' }}>
          <h1 style={{ fontSize: '1.5rem' }}>
            SIMCASE · El Estado frente al Estallido Social
          </h1>
          <p style={{ color: 'var(--texto-2)', marginTop: '0.75rem' }}>
            Puesto de Mando Unificado · segunda semana de mayo
          </p>
        </div>

        <Seccion titulo="Proyectar a la sala">
          {/* La marca de ayuda va FUERA del enlace: un botón dentro de un ancla
              es HTML inválido, y pulsarlo navegaría en vez de explicar. */}
          {PROYECCIONES.map(p => (
            <div key={p.ruta} className="tarjeta">
              <div style={{ display: 'flex', alignItems: 'baseline',
                            justifyContent: 'space-between', gap: '0.5rem' }}>
                <a href={p.ruta} style={{ fontWeight: 650, textDecoration: 'none',
                                          color: 'var(--texto)' }}>
                  {p.nombre}
                </a>
                <Ayuda etiqueta={`Para qué sirve: ${p.nombre}`}>{p.ayuda}</Ayuda>
              </div>
              <code style={{ color: 'var(--texto-3)', fontSize: '0.78rem' }}>{p.ruta}</code>
            </div>
          ))}
        </Seccion>

        <Seccion titulo="Vista personal de cada rol" ayuda={AYUDA_VISTAS}>
          {ROLES.map(r => (
            <a key={r.id} href={`/vista/${encodeURIComponent(r.id)}`} className="tarjeta"
               style={{ textDecoration: 'none', color: 'inherit', display: 'block',
                        padding: '0.7rem 0.9rem' }}>
              <span className="eyebrow">{r.frente}</span>
              <div style={{ fontWeight: 600, fontSize: '0.92rem' }}>{r.nombre}</div>
            </a>
          ))}
        </Seccion>

        <Seccion titulo="Consola" ayuda={AYUDA_CONSOLA}>
          <a href="/consola" className="tarjeta"
             style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
            <div style={{ fontWeight: 650 }}>Transcripción de órdenes</div>
            <code style={{ color: 'var(--texto-3)', fontSize: '0.78rem' }}>/consola</code>
          </a>
        </Seccion>
      </div>
    </div>
  )
}

function Seccion({ titulo, ayuda, children }) {
  return (
    <div style={{ width: '100%', maxWidth: '52rem' }}>
      <div style={{ marginBottom: '0.5rem' }}>
        <span className="eyebrow">
          {titulo}
          {ayuda && <Ayuda etiqueta={`Para qué sirve: ${titulo}`}>{ayuda}</Ayuda>}
        </span>
      </div>
      <div className="rejilla" style={{
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.6rem',
      }}>
        {children}
      </div>
    </div>
  )
}

export default function App() {
  const ruta = decodeURIComponent(window.location.pathname)

  if (ruta === '/tablero') return <Tablero />
  if (ruta === '/esfera') return <EsferaPublica />
  if (ruta === '/consola') return <Consola />

  if (ruta.startsWith('/vista/')) {
    const rol = ruta.slice('/vista/'.length)
    if (ROLES.some(r => r.id === rol)) return <VistaPrivada rol={rol} />
  }

  return <Portada />
}
