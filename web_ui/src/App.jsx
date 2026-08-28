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
// los nueve. El sistema conduce el turno.
//
// ESTA PORTADA ES UN LANZADOR, no un documento. Cada tarjeta dice su nombre y su
// ruta; para qué sirve cada una está detrás de su marca de ayuda.
//
// Y LOS OCHO ROLES SON OCHO DESTINOS EQUIVALENTES: misma caja, mismo peso, texto
// centrado. Quien llega busca el suyo, no compara. La rejilla que lo garantiza
// es `.rejilla-roles`, en `index.css`.
// ---------------------------------------------------------------------------

import { Component } from 'react'

import Tablero from './components/Tablero'
import Consola from './components/Consola'
import VistaPrivada from './components/VistaPrivada'
import Ayuda from './components/Ayuda'
import { ROLES } from './comun.jsx'
import LogoAiLab from '../logos/LOGO Ai Lab_blanco.png'

// ---------------------------------------------------------------------------
// LA RED DE SEGURIDAD
//
// React desmonta el árbol entero cuando un componente lanza durante el pintado.
// Sin nada que lo intercepte, **el resultado es una pantalla en blanco**: ni
// mensaje, ni traza, ni forma de saber si el problema es el servidor, la red o
// un dato con una forma inesperada. En una sala con diez pantallas encendidas y
// dos horas de reloj, eso es el fallo más caro que puede tener esta interfaz,
// porque no se puede diagnosticar sin abrir la consola del navegador.
//
// Con esto, lo peor que puede pasar es una tarjeta que dice qué se rompió y un
// botón para recargar. Una pantalla que explica su fallo se arregla en la sala;
// una en blanco, no.
// ---------------------------------------------------------------------------

class Salvavidas extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  render() {
    if (!this.state.error) return this.props.children
    return (
      <div className="pantalla">
        <div className="cuerpo cargando">
          <div className="cargando-caja con-error">
            <div className="eyebrow">Esta pantalla se rompió al dibujarse</div>
            <p className="cargando-titulo">
              El motor sigue corriendo. Lo que falló es la interfaz.
            </p>
            <p className="cargando-detalle">{String(this.state.error)}</p>
            <button className="primario"
                    onClick={() => window.location.reload()}>
              Recargar la pantalla
            </button>
          </div>
        </div>
      </div>
    )
  }
}

const AYUDA_TABLERO = (
  <>
    <p>
      <strong>Lo que el Estado tiene por cierto</strong>, en grano grueso: el
      reloj del ejercicio, las reservas, el mapa de corredores, el semáforo de
      abastecimiento y el pliego de decisiones.
    </p>
    <p>
      Lleva la <strong>esfera pública</strong> —lo que se dice— en una barra
      lateral plegable. Las dos se muestran a la vez porque lo que el ejercicio
      enseña es la distancia entre ambas, y esa distancia solo se aprecia
      comparándolas.
    </p>
  </>
)

const AYUDA_CONSOLA = (
  <>
    <p>
      <strong>Aquí se transcribe lo que la mesa acordó.</strong> La pantalla
      devuelve el plan interpretado con su banda de riesgo, para leerlo en voz
      alta antes de ejecutarlo.
    </p>
    <p>
      No se proyecta a la sala. Puede operarla cualquiera de los nueve: quien lo
      hace transcribe, y no conduce el ejercicio ni decide su ritmo.
    </p>
  </>
)

const AYUDA_VISTAS = (
  <>
    <p>
      <strong>Cada rol abre la suya en su propio dispositivo.</strong> Responde
      cuánto, dónde exactamente y desde cuándo, con un detalle que el tablero
      general no da.
    </p>
    <p>
      Es personal, no confidencial: el sistema la muestra solo a su titular, y el
      ejercicio espera que su contenido se comparta con la mesa.
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

        {/* Ocho destinos equivalentes: rejilla propia, dos filas de cuatro y
            todas las cajas de la misma altura. Con `auto-fit` salían tres
            columnas, una última fila de dos y alturas distintas según el cargo
            envolviera a una línea o a dos. */}
        <Seccion titulo="Vista personal de cada rol" ayuda={AYUDA_VISTAS}
                 rejilla="rejilla-roles">
          {ROLES.map(r => (
            <a key={r.id} href={`/vista/${encodeURIComponent(r.id)}`}
               className="tarjeta tarjeta-rol">
              <span className="eyebrow">{r.frente}</span>
              <span className="tarjeta-rol-nombre">{r.nombre}</span>
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

/** Un bloque de la portada. `rejilla` nombra la clase que reparte las tarjetas:
    la de los nueve roles necesita una propia y las demás se quedan con la de la
    portada, que acomoda una sola tarjeta ancha. */
function Seccion({ titulo, ayuda, rejilla = 'rejilla-portada', children }) {
  return (
    <div style={{ width: '100%', maxWidth: '52rem' }}>
      <div style={{ marginBottom: '0.5rem' }}>
        <span className="eyebrow">
          {titulo}
          {ayuda && <Ayuda etiqueta={`Para qué sirve: ${titulo}`}>{ayuda}</Ayuda>}
        </span>
      </div>
      <div className={rejilla}>{children}</div>
    </div>
  )
}

export default function App() {
  return <Salvavidas><Superficie /></Salvavidas>
}

function Superficie() {
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
    // NORMALIZADO. `Policía` y `Defensoría` llevan tilde, y una tilde puede
    // llegar en dos codificaciones Unicode distintas —compuesta o
    // descompuesta— según de dónde salga el enlace. Sin normalizar, la
    // comparación falla y el titular aterriza en la portada sin entender por
    // qué su propia vista no existe.
    const rol = ruta.slice('/vista/'.length).normalize('NFC')
    const ficha = ROLES.find(r => r.id.normalize('NFC') === rol)
    if (ficha) return <VistaPrivada rol={ficha.id} />
  }

  return <Portada />
}
