// ---------------------------------------------------------------------------
// TRES SUPERFICIES
//
//   /tablero        PROYECTAR · lo que el Estado tiene por cierto
//                   — con la esfera pública como barra lateral plegable
//   /vista/{rol}    el dispositivo de cada uno · su cartera en alta resolución
//   /consola        donde se transcriben las órdenes · NO proyectar
//
// LA ESFERA PÚBLICA YA NO TIENE RUTA PROPIA
// ----------------------------------------
// La tenía, para montajes de dos proyectores. Se ha retirado, y no por poda:
//
//     La distancia entre lo que el Estado tiene por cierto y lo que se dice
//     es el caso, y SOLO SE PERCIBE SIMULTÁNEA.
//
// Mientras la esfera tuvo ruta propia, esa doctrina dependía de que quien monta
// la sala hiciera lo correcto: bastaba proyectar una de las dos sola para perder
// justamente lo que hay que enseñar. Ahora vive dentro del tablero y **el
// montaje incorrecto deja de ser posible.**
//
// Una regla que el software garantiza vale más que una que el software
// recomienda.
//
// Y NO HAY MODERADOR COMO FIGURA APARTE: quien opera la consola puede ser uno de
// los ocho. El sistema conduce el turno.
//
// ESTA PORTADA ES UN LANZADOR, no un documento. Cada tarjeta dice su nombre y su
// ruta; para qué sirve cada una está detrás de su marca de ayuda.
// ---------------------------------------------------------------------------

import Tablero from './components/Tablero'
import Consola from './components/Consola'
import VistaPrivada from './components/VistaPrivada'
import Ayuda from './components/Ayuda'
import { ROLES } from './comun.jsx'
import LogoAiLab from '../logos/LOGO Ai Lab_blanco.png'

const AYUDA_TABLERO = (
  <>
    <p>
      <strong>Lo que el Estado tiene por cierto</strong>, en grano grueso: el
      reloj del ejercicio, las reservas, el mapa de corredores, el semáforo de
      abastecimiento y el pliego de decisiones.
    </p>
    <p>
      Lleva la <strong>esfera pública</strong> —lo que se dice— como barra
      lateral plegable. Las dos se ven a la vez a propósito: la distancia entre
      una y otra es el caso, y solo se percibe simultánea.
    </p>
  </>
)

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
          <div className="tarjeta">
            <div style={{ display: 'flex', alignItems: 'baseline',
                          justifyContent: 'space-between', gap: '0.5rem' }}>
              <a href="/tablero" style={{ fontWeight: 650, textDecoration: 'none',
                                          color: 'var(--texto)' }}>
                Tablero de situación
              </a>
              <Ayuda etiqueta="Para qué sirve el tablero">{AYUDA_TABLERO}</Ayuda>
            </div>
            <code style={{ color: 'var(--texto-3)', fontSize: '0.78rem' }}>/tablero</code>
          </div>
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
  if (ruta === '/consola') return <Consola />

  // La esfera vivió aquí hasta que se metió dentro del tablero. Quien llegue por
  // un enlace viejo aterriza donde está ahora, no en la portada.
  if (ruta === '/esfera') {
    window.location.replace('/tablero')
    return null
  }

  if (ruta.startsWith('/vista/')) {
    const rol = ruta.slice('/vista/'.length)
    if (ROLES.some(r => r.id === rol)) return <VistaPrivada rol={rol} />
  }

  return <Portada />
}
