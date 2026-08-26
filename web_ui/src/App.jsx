// ---------------------------------------------------------------------------
// CUATRO SUPERFICIES (v2)
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
// ---------------------------------------------------------------------------

import Tablero from './components/Tablero'
import EsferaPublica from './components/EsferaPublica'
import Consola from './components/Consola'
import VistaPrivada from './components/VistaPrivada'
import { ROLES } from './comun.jsx'
import LogoAiLab from '../logos/LOGO Ai Lab_blanco.png'

const PROYECCIONES = [
  {
    ruta: '/tablero',
    nombre: 'Tablero de situación',
    detalle: 'Qué está pasando: reservas, mapa, corredores y pliego. Lleva la esfera pública como barra lateral, para montajes de una sola pantalla.',
  },
  {
    ruta: '/esfera',
    nombre: 'Esfera pública',
    detalle: 'Qué se dice: prensa, redes, gremios y denuncias sin verificar. Para el montaje de dos proyectores.',
  },
]

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
            Puesto de Mando Unificado · segunda semana de mayo.
            Ocho personas, dos horas, y un motor que calcula las consecuencias de
            lo que la sala decide.
          </p>
        </div>

        <Seccion titulo="Proyectar a la sala" nota="a la vez · con una sola pantalla, use la barra del tablero">
          {PROYECCIONES.map(p => (
            <a key={p.ruta} href={p.ruta} className="tarjeta"
               style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
              <div style={{ fontWeight: 650 }}>{p.nombre}</div>
              <div style={{ color: 'var(--texto-2)', fontSize: '0.88rem',
                            marginTop: '0.15rem' }}>{p.detalle}</div>
              <code style={{ color: 'var(--texto-3)', fontSize: '0.78rem' }}>{p.ruta}</code>
            </a>
          ))}
        </Seccion>

        <Seccion titulo="Vista personal de cada rol"
                 nota="en su propio dispositivo · personal, no confidencial">
          {ROLES.map(r => (
            <a key={r.id} href={`/vista/${encodeURIComponent(r.id)}`} className="tarjeta"
               style={{ textDecoration: 'none', color: 'inherit', display: 'block',
                        padding: '0.7rem 0.9rem' }}>
              <span className="eyebrow">{r.frente}</span>
              <div style={{ fontWeight: 600, fontSize: '0.92rem' }}>{r.nombre}</div>
            </a>
          ))}
        </Seccion>

        <Seccion titulo="Consola" nota="no proyectar · puede operarla uno de los ocho">
          <a href="/consola" className="tarjeta"
             style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}>
            <div style={{ fontWeight: 650 }}>Transcripción de órdenes</div>
            <div style={{ color: 'var(--texto-2)', fontSize: '0.88rem',
                          marginTop: '0.15rem' }}>
              Se escribe lo que la mesa acordó y la pantalla devuelve el plan con su
              banda de riesgo, para leerlo en voz alta antes de ejecutar.
            </div>
            <code style={{ color: 'var(--texto-3)', fontSize: '0.78rem' }}>/consola</code>
          </a>
        </Seccion>
      </div>
    </div>
  )
}

function Seccion({ titulo, nota, children }) {
  return (
    <div style={{ width: '100%', maxWidth: '52rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between',
                    alignItems: 'baseline', marginBottom: '0.5rem' }}>
        <span className="eyebrow">{titulo}</span>
        <span className="eyebrow" style={{ letterSpacing: '0.06em',
                                           textTransform: 'none' }}>{nota}</span>
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
